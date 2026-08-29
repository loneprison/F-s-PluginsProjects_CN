from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from aetext.build import ProjectManifest
from aetext.catalog.review import (
    ReviewUnavailableError,
    ReviewValidationError,
    ReviewWorkspaceService,
)
from aetext.scanner import scan_sources


class FakeDiscovery:
    def __init__(self, manifests: dict[str, ProjectManifest]) -> None:
        self.manifests = manifests
        self.calls = 0

    def discover(self, plugin_name: str) -> ProjectManifest:
        self.calls += 1
        if plugin_name not in self.manifests:
            raise FileNotFoundError(plugin_name)
        return self.manifests[plugin_name]


class CountingScanner:
    def __init__(self) -> None:
        self.calls = 0

    def __call__(self, paths, *, project_root):
        self.calls += 1
        return scan_sources(paths, project_root=project_root)


def _workflow() -> dict[str, object]:
    return {
        "schemaVersion": 1,
        "enabled": True,
        "stages": [
            {"id": "needs-review", "label": "待核对", "color": "orange", "enabled": True},
            {"id": "reviewed", "label": "已校对", "color": "green", "enabled": True},
        ],
        "completedStageId": "reviewed",
        "defaults": {"manualEdit": "needs-review", "pretranslation": None},
        "sourceChange": {"reviewed": "needs-review"},
    }


def _fixture(
    tmp_path: Path,
    *,
    name: str = "Fixture",
    role: str = "Param",
    original: str = "Value",
):
    catalog = tmp_path / "_localization" / "catalog" / "(Templates)" / f"{name}.json"
    family_root = tmp_path / "_localization" / "families" / "fs"
    family = family_root / "generation.json"
    workflow = family_root / "review-workflow.json"
    source = tmp_path / f"{name}.cpp"
    project = tmp_path / f"{name}.vcxproj"
    catalog.parent.mkdir(parents=True)
    family.parent.mkdir(parents=True)
    catalog.write_text(
        json.dumps(
            {
                "schemaVersion": 1,
                "translations": {
                    "en": {role: {"L10N_VALUE": {"useSource": True}}},
                    "zh": {role: {"L10N_VALUE": "值"}},
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    family.write_text(
        json.dumps(
            {
                "schemaVersion": 1,
                "familyId": "fs",
                "sourceVariantId": "source",
                "variants": [
                    {
                        "id": "en",
                        "textSource": {"kind": "translation", "locale": "en"},
                        "encodingProfile": "windows-1252",
                    },
                    {
                        "id": "source",
                        "textSource": {"kind": "source"},
                        "encodingProfile": "windows-932",
                    },
                    {
                        "id": "zh",
                        "textSource": {"kind": "translation", "locale": "zh"},
                        "encodingProfile": "windows-936",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    workflow.write_text(json.dumps(_workflow(), ensure_ascii=False), encoding="utf-8")
    source.write_text(
        f'#define L10N_VALUE "{original}"\n'
        f"auto value = AETEXT_{role.upper()}(strings, L10N_VALUE);\n",
        encoding="utf-8",
    )
    project.write_text("<Project />", encoding="utf-8")
    manifest = ProjectManifest(
        project_path=project,
        name=name,
        catalog_path=catalog,
        namespace="FixtureText",
        role="Templates",
        category="",
        family_definition_path=family,
        inputs=[source],
    )
    discovery = FakeDiscovery({name: manifest})
    scanner = CountingScanner()
    service = ReviewWorkspaceService(tmp_path, discovery=discovery, scanner=scanner)
    return service, catalog, source, discovery, scanner


def test_workspace_includes_nfs_skeleton_in_normal_content_scope(tmp_path: Path) -> None:
    service, _, _, _, _ = _fixture(tmp_path, name="NFsSkelton")

    assert not service.workspace.projects[0].deferred


def test_normal_web_paths_do_not_discover_or_scan(tmp_path: Path) -> None:
    service, catalog, _, discovery, scanner = _fixture(tmp_path)
    assert len(service.workspace.projects) == 1
    assert service.workspace.projects[0].scan_state == "unscanned"
    assert discovery.calls == scanner.calls == 0

    with pytest.raises(ReviewUnavailableError):
        service.open_cached_project("Fixture", "zh")
    assert discovery.calls == scanner.calls == 0

    session = service.scan_project("Fixture", "zh")
    assert discovery.calls == scanner.calls == 1
    opened = service.open_cached_project("Fixture", "zh")
    english = service.switch_locale(opened, "en")
    row = service.switch_locale(english, "zh").rows[0].model_dump()
    row["translation"] = "新值"
    saved = service.save_locale(session, [row])
    service.reload_catalogs()

    assert discovery.calls == scanner.calls == 1
    document = json.loads(catalog.read_text(encoding="utf-8"))
    assert document["translations"]["en"] == {"Param": {"L10N_VALUE": {"useSource": True}}}
    assert document["translations"]["zh"] == {"Param": {"L10N_VALUE": "新值"}}
    assert saved.rows[0].translation == "新值"


def test_cached_startup_does_not_check_changed_source_and_cache_can_be_deleted(
    tmp_path: Path,
) -> None:
    service, catalog, source, discovery, scanner = _fixture(tmp_path)
    scanned = service.scan_project("Fixture", "zh")
    assert scanned.rows[0].original == "Value"
    source.write_text(
        '#define L10N_VALUE "Changed"\nauto value = AETEXT_PARAM(strings, L10N_VALUE);\n',
        encoding="utf-8",
    )

    reopened = ReviewWorkspaceService(tmp_path, discovery=discovery, scanner=scanner)
    assert reopened.open_cached_project("Fixture", "zh").rows[0].original == "Value"
    assert discovery.calls == scanner.calls == 1

    before = catalog.read_bytes()
    shutil.rmtree(tmp_path / "_localization" / ".cache" / "aetext-review")
    without_cache = ReviewWorkspaceService(tmp_path, discovery=discovery, scanner=scanner)
    assert without_cache.workspace.projects[0].scan_state == "unscanned"
    assert catalog.read_bytes() == before
    assert discovery.calls == scanner.calls == 1


def test_content_status_and_manual_workflow_are_independent(tmp_path: Path) -> None:
    service, catalog, _, _, _ = _fixture(tmp_path)
    session = service.scan_project("Fixture", "zh")
    assert session.rows[0].content_status == "valid"
    assert session.rows[0].workflow_stage is None

    row = session.rows[0].model_dump()
    row["translation"] = "修改"
    saved = service.save_locale(session, [row])

    assert saved.rows[0].content_status == "valid"
    assert saved.rows[0].workflow_stage == "needs-review"
    document = json.loads(catalog.read_text(encoding="utf-8"))
    assert document["workflow"]["zh"] == {"Param": {"L10N_VALUE": "needs-review"}}

    english = service.open_cached_project("Fixture", "en")
    assert english.rows[0].content_status == "use-source"


def test_workflow_can_be_disabled_without_losing_plugin_state(tmp_path: Path) -> None:
    service, catalog, _, _, _ = _fixture(tmp_path)
    session = service.scan_project("Fixture", "zh")
    reviewed = service.set_workflow_stage(session, {"L10N_VALUE"}, "reviewed")
    service.save_locale(reviewed, [reviewed.rows[0].model_dump()])
    definition = service.workflow.model_dump(by_alias=True)
    definition["enabled"] = False
    service.save_workflow_definition(definition)

    disabled = service.open_cached_project("Fixture", "zh")
    assert disabled.workflow.enabled is False
    assert disabled.rows[0].workflow_stage == "reviewed"
    service.save_locale(disabled, [disabled.rows[0].model_dump()])
    assert json.loads(catalog.read_text(encoding="utf-8"))["workflow"]["zh"] == {
        "Param": {"L10N_VALUE": "reviewed"}
    }


def test_workflow_settings_are_data_driven_and_referenced_stages_cannot_disappear(
    tmp_path: Path,
) -> None:
    service, _, _, discovery, scanner = _fixture(tmp_path)
    session = service.scan_project("Fixture", "zh")
    reviewed = service.set_workflow_stage(session, {"L10N_VALUE"}, "reviewed")
    service.save_locale(reviewed, [reviewed.rows[0].model_dump()])
    definition = service.workflow.model_dump(by_alias=True)
    definition["stages"].reverse()
    definition["stages"][0].update(label="批准", color="teal", enabled=False)

    saved = service.save_workflow_definition(definition)

    assert [stage.id for stage in saved.stages] == ["reviewed", "needs-review"]
    assert (saved.stages[0].label, saved.stages[0].color, saved.stages[0].enabled) == (
        "批准",
        "teal",
        False,
    )
    without_reviewed = saved.model_dump(by_alias=True)
    without_reviewed["stages"] = [without_reviewed["stages"][1]]
    without_reviewed["completedStageId"] = "needs-review"
    without_reviewed["sourceChange"] = {}
    with pytest.raises(ValueError, match="still referenced"):
        service.save_workflow_definition(without_reviewed)
    assert discovery.calls == scanner.calls == 1


def test_progress_uses_explicit_completed_stage_instead_of_stage_order(tmp_path: Path) -> None:
    service, _, _, _, _ = _fixture(tmp_path)
    session = service.scan_project("Fixture", "zh")
    reviewed = service.set_workflow_stage(session, {"L10N_VALUE"}, "reviewed")
    service.save_locale(reviewed, [reviewed.rows[0].model_dump()])
    definition = service.workflow.model_dump(by_alias=True)
    definition["stages"].append(
        {"id": "published", "label": "发布确认", "color": "purple", "enabled": True}
    )
    definition["stages"][1]["enabled"] = False
    service.save_workflow_definition(definition)

    project = next(item for item in service.workspace.projects if item.name == "Fixture")

    assert definition["completedStageId"] == "reviewed"
    assert project.progress["zh"].reviewed == 1
    assert project.progress["zh"].pending_review == 0


def test_popup_structure_error_prevents_save_without_rescan(tmp_path: Path) -> None:
    service, catalog, _, discovery, scanner = _fixture(
        tmp_path,
        role="Popup",
        original="One|Two",
    )
    session = service.scan_project("Fixture", "zh")
    before = catalog.read_bytes()
    row = session.rows[0].model_dump()
    row["translation"] = "只有一项"

    with pytest.raises(ReviewValidationError):
        service.save_locale(session, [row])

    assert catalog.read_bytes() == before
    assert discovery.calls == scanner.calls == 1

    document = json.loads(catalog.read_text(encoding="utf-8"))
    document["translations"]["zh"]["Popup"]["L10N_VALUE"] = "仍然一项"
    catalog.write_text(json.dumps(document, ensure_ascii=False), encoding="utf-8")
    service.reload_catalogs()
    assert service.open_cached_project("Fixture", "zh").rows[0].content_status == "error"


def test_popup_separator_position_is_structural(tmp_path: Path) -> None:
    service, catalog, _, discovery, scanner = _fixture(
        tmp_path,
        role="Popup",
        original="One|(-|Two",
    )
    session = service.scan_project("Fixture", "zh")
    before = catalog.read_bytes()
    row = session.rows[0].model_dump()
    row["translation"] = "一|普通文字|二"

    with pytest.raises(ReviewValidationError) as error:
        service.save_locale(session, [row])

    assert any(item["code"] == "AET3033" for item in error.value.diagnostics)
    assert catalog.read_bytes() == before
    assert discovery.calls == scanner.calls == 1


def test_source_change_uses_effective_fallback_until_explicit_save(tmp_path: Path) -> None:
    service, catalog, source, discovery, scanner = _fixture(tmp_path)
    session = service.scan_project("Fixture", "zh")
    reviewed = service.set_workflow_stage(session, {"L10N_VALUE"}, "reviewed")
    saved = service.save_locale(reviewed, [reviewed.rows[0].model_dump()])
    assert saved.rows[0].workflow_stage == "reviewed"

    source.write_text(
        '#define L10N_VALUE "Changed"\nauto value = AETEXT_PARAM(strings, L10N_VALUE);\n',
        encoding="utf-8",
    )
    changed = service.scan_project("Fixture", "zh")

    assert changed.rows[0].workflow_stage == "needs-review"
    assert json.loads(catalog.read_text(encoding="utf-8"))["workflow"]["zh"] == {
        "Param": {"L10N_VALUE": "reviewed"}
    }
    persisted = service.save_locale(changed, [changed.rows[0].model_dump()])
    assert persisted.rows[0].workflow_stage == "needs-review"
    reviewed_again = service.set_workflow_stage(persisted, {"L10N_VALUE"}, "reviewed")
    final = service.save_locale(reviewed_again, [reviewed_again.rows[0].model_dump()])
    assert final.rows[0].workflow_stage == "reviewed"
    assert discovery.calls == scanner.calls == 2


def test_disabled_workflow_does_not_acknowledge_pending_source_change(tmp_path: Path) -> None:
    service, catalog, source, _, _ = _fixture(tmp_path)
    session = service.scan_project("Fixture", "zh")
    reviewed = service.set_workflow_stage(session, {"L10N_VALUE"}, "reviewed")
    service.save_locale(reviewed, [reviewed.rows[0].model_dump()])
    source.write_text(
        '#define L10N_VALUE "Changed"\nauto value = AETEXT_PARAM(strings, L10N_VALUE);\n',
        encoding="utf-8",
    )
    changed = service.scan_project("Fixture", "zh")
    assert changed.rows[0].workflow_stage == "needs-review"

    disabled_definition = service.workflow.model_dump(by_alias=True)
    disabled_definition["enabled"] = False
    service.save_workflow_definition(disabled_definition)
    disabled = service.open_cached_project("Fixture", "zh")
    service.save_locale(disabled, [disabled.rows[0].model_dump()])

    enabled_definition = service.workflow.model_dump(by_alias=True)
    enabled_definition["enabled"] = True
    service.save_workflow_definition(enabled_definition)
    reopened = service.open_cached_project("Fixture", "zh")

    assert reopened.rows[0].workflow_stage == "needs-review"
    assert reopened.source_snapshot.source_change_pending["zh"] == ["L10N_VALUE"]
    assert json.loads(catalog.read_text(encoding="utf-8"))["workflow"]["zh"] == {
        "Param": {"L10N_VALUE": "reviewed"}
    }


def test_scan_all_continues_after_one_project_fails(tmp_path: Path) -> None:
    service, catalog, _, discovery, scanner = _fixture(tmp_path)
    broken_catalog = tmp_path / "_localization" / "catalog" / "NF's Plugins-Filter" / "Broken.json"
    broken_catalog.parent.mkdir(parents=True)
    broken_catalog.write_text(
        json.dumps(
            {
                "schemaVersion": 1,
                "translations": {
                    "en": {"Param": {"L10N_VALUE": None}},
                    "zh": {"Param": {"L10N_VALUE": None}},
                },
            }
        ),
        encoding="utf-8",
    )
    service.reload_catalogs()
    before = {path: path.read_bytes() for path in (catalog, broken_catalog)}

    result = service.scan_all()

    assert [(item.project, item.status) for item in result.results] == [
        ("Broken", "failed"),
        ("Fixture", "ready"),
    ]
    assert discovery.calls == 2
    assert scanner.calls == 1
    assert {path: path.read_bytes() for path in before} == before


def test_scan_all_honors_cancellation_before_discovery(tmp_path: Path) -> None:
    service, _, _, discovery, scanner = _fixture(tmp_path)

    result = service.scan_all(cancelled=lambda: True)

    assert result.cancelled is True
    assert [(item.project, item.status) for item in result.results] == [("Fixture", "cancelled")]
    assert discovery.calls == scanner.calls == 0


def test_browser_row_order_cannot_change_source_derived_catalog_order(tmp_path: Path) -> None:
    service, catalog, source, discovery, scanner = _fixture(tmp_path)
    catalog.write_text(
        json.dumps(
            {
                "schemaVersion": 1,
                "translations": {
                    "en": {
                        "Param": {
                            "L10N_ALPHA": {"useSource": True},
                            "L10N_ZETA": {"useSource": True},
                        }
                    },
                    "zh": {
                        "Param": {
                            "L10N_ALPHA": "前",
                            "L10N_ZETA": "后",
                        }
                    },
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    source.write_text(
        '#define L10N_ZETA "Zeta"\n'
        '#define L10N_ALPHA "Alpha"\n'
        "void ParamsSetup() {\n"
        "  AETEXT_PARAM(strings, L10N_ZETA);\n"
        "  AETEXT_PARAM(strings, L10N_ALPHA);\n"
        "}\n",
        encoding="utf-8",
    )
    service.reload_catalogs()

    before_scan = catalog.read_bytes()
    session = service.scan_project("Fixture", "zh")
    assert catalog.read_bytes() == before_scan
    assert [row.stable_id for row in session.rows] == ["L10N_ZETA", "L10N_ALPHA"]
    assert [(binding.stable_id, binding.index) for binding in session.source_snapshot.bindings] == [
        ("L10N_ALPHA", 0),
        ("L10N_ZETA", 1),
    ]
    submitted = [row.model_dump() for row in reversed(session.rows)]
    submitted[0]["translation"] = "浏览器排序后编辑"
    service.save_locale(session, submitted)

    document = json.loads(catalog.read_text(encoding="utf-8"))
    assert list(document["translations"]["zh"]["Param"]) == [
        "L10N_ZETA",
        "L10N_ALPHA",
    ]
    assert document["translations"]["zh"]["Param"]["L10N_ALPHA"] == "浏览器排序后编辑"
    assert discovery.calls == scanner.calls == 1
