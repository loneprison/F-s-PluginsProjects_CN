from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from aetext.build import ProjectManifest
from aetext.catalog.models import BindingRecord
from aetext.catalog.source_index import ReviewLayout, ReviewUse, SourceSnapshotRepository


def _manifest(root: Path) -> ProjectManifest:
    project = root / "PluginSkeleton" / "Win" / "PluginSkeleton.vcxproj"
    catalog = root / "_localization" / "catalog" / "(Templates)" / "PluginSkeleton.json"
    family = root / "_localization" / "families" / "fs" / "generation.json"
    source = root / "PluginSkeleton" / "PluginSkeleton.cpp"
    for path in (project, catalog, family, source):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("fixture", encoding="utf-8")
    return ProjectManifest(
        project_path=project,
        name="PluginSkeleton",
        catalog_path=catalog,
        namespace="PluginSkeletonText",
        role="Templates",
        category="",
        family_definition_path=family,
        inputs=[source],
    )


def _binding() -> BindingRecord:
    return BindingRecord.model_validate(
        {
            "role": "Param",
            "stableId": "L10N_VALUE",
            "disposition": "translated",
            "index": 0,
            "original": "Value",
            "definition": {"path": "PluginSkeleton.cpp", "line": 1, "column": 1},
            "uses": [{"path": "PluginSkeleton.cpp", "line": 2, "column": 1}],
        },
        strict=True,
    )


def _review_use() -> ReviewUse:
    return ReviewUse.model_validate(
        {
            "role": "Param",
            "stableId": "L10N_VALUE",
            "disposition": "translated",
            "inputOrdinal": 0,
            "callOrdinal": 0,
            "functionName": "ParamsSetup",
            "path": "PluginSkeleton.cpp",
            "line": 2,
            "column": 1,
        },
        strict=True,
    )


def _review_layout() -> ReviewLayout:
    return ReviewLayout.model_validate(
        {
            "schemaVersion": 1,
            "sections": [
                {
                    "role": "Param",
                    "entries": [
                        {
                            "stableId": "L10N_VALUE",
                            "primaryRole": "Param",
                            "roles": ["Param"],
                            "panelOrder": 0,
                        }
                    ],
                }
            ],
        },
        strict=True,
    )


def test_source_snapshot_and_project_index_are_atomic_strict_and_relative(
    tmp_path: Path,
) -> None:
    repository = SourceSnapshotRepository(tmp_path)
    saved = repository.save(
        _manifest(tmp_path),
        [_binding()],
        [_review_use()],
        _review_layout(),
        [],
        source_change_pending={"en": ["L10N_VALUE"], "zh": ["L10N_VALUE"]},
    )

    assert saved.project_path == "PluginSkeleton/Win/PluginSkeleton.vcxproj"
    assert saved.inputs == ["PluginSkeleton/PluginSkeleton.cpp"]
    assert repository.load("PluginSkeleton") == saved
    index = repository.index.load()
    assert [(entry.name, entry.scan_state) for entry in index.projects] == [
        ("PluginSkeleton", "ready")
    ]

    acknowledged = repository.acknowledge_source_changes(saved, "zh")
    assert acknowledged.source_change_pending == {"en": ["L10N_VALUE"]}
    assert repository.load("PluginSkeleton") == acknowledged

    document = json.loads(repository.index.path.read_text(encoding="utf-8"))
    document["schemaVersion"] = 2
    repository.index.path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(ValidationError):
        repository.index.load()


def test_source_snapshot_rejects_project_name_paths(tmp_path: Path) -> None:
    repository = SourceSnapshotRepository(tmp_path)

    with pytest.raises(ValueError, match="must not be a path"):
        repository.load("../PluginSkeleton")


def test_source_snapshot_records_external_project_inputs_but_not_external_identity_paths(
    tmp_path: Path,
) -> None:
    repository_root = tmp_path / "repository"
    external = tmp_path / "sdk" / "Util.cpp"
    external.parent.mkdir(parents=True)
    external.write_text("fixture", encoding="utf-8")
    manifest = _manifest(repository_root).model_copy(update={"inputs": [external]})
    repository = SourceSnapshotRepository(repository_root)

    saved = repository.save(manifest, [_binding()], [_review_use()], _review_layout(), [])

    assert saved.inputs == [external.resolve().as_posix()]
    escaped = manifest.model_copy(update={"catalog_path": external})
    with pytest.raises(ValueError, match="escaped repository"):
        repository.save(escaped, [_binding()], [_review_use()], _review_layout(), [])
