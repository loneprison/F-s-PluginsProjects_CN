from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from aetext.build import ProjectManifest
from aetext.catalog.repository import CatalogConflictError
from aetext.catalog.review import ReviewWorkspaceService

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture
def workspace(tmp_path: Path):
    family = tmp_path / "_localization" / "families" / "fs"
    family.mkdir(parents=True)
    for name in ("generation.json", "review-workflow.json"):
        shutil.copyfile(REPOSITORY_ROOT / "_localization" / "families" / "fs" / name, family / name)
    catalog = tmp_path / "_localization" / "catalog" / "(Templates)" / "Fixture.json"
    catalog.parent.mkdir(parents=True)
    catalog.write_text(
        json.dumps(
            {
                "schemaVersion": 1,
                "translations": {
                    "en": {"Param": {"L10N_VALUE": {"useSource": True}}},
                    "zh": {"Param": {"L10N_VALUE": "值"}},
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    source = tmp_path / "Fixture.cpp"
    source.write_text(
        '#define L10N_VALUE "Value"\nauto value = AETEXT_PARAM(strings, L10N_VALUE);\n',
        encoding="utf-8",
    )
    manifest = ProjectManifest(
        project_path=tmp_path / "Fixture.vcxproj",
        name="Fixture",
        catalog_path=catalog,
        namespace="FixtureText",
        role="Templates",
        category="",
        family_definition_path=family / "generation.json",
        inputs=[source],
    )
    service = ReviewWorkspaceService(
        tmp_path, discovery=SimpleNamespace(discover=lambda _: manifest)
    )
    return service, catalog


def test_cli_starts() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "aetext", "--help"],
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    )
    assert "review" in result.stdout


def test_review_scan_save_and_reload(workspace) -> None:
    service, catalog = workspace
    session = service.scan_project("Fixture", "zh")
    assert session.rows[0].original == "Value"
    row = session.rows[0].model_dump()
    row["translation"] = "新值"
    service.save_locale(session, [row])
    service.reload_catalogs()

    reopened = service.open_cached_project("Fixture", "zh")
    assert reopened.rows[0].translation == "新值"
    assert reopened.rows[0].content_status == "valid"
    document = json.loads(catalog.read_text(encoding="utf-8"))
    assert document["translations"]["en"] == {"Param": {"L10N_VALUE": {"useSource": True}}}
    assert document["translations"]["zh"] == {"Param": {"L10N_VALUE": "新值"}}


def test_invalid_translation_is_not_saved(workspace) -> None:
    service, catalog = workspace
    session = service.scan_project("Fixture", "zh")
    before = catalog.read_bytes()
    row = session.rows[0].model_dump()
    row["translation"] = ""

    with pytest.raises(ValueError):
        service.save_locale(session, [row])
    assert catalog.read_bytes() == before


def test_external_change_is_not_overwritten(workspace) -> None:
    service, catalog = workspace
    session = service.scan_project("Fixture", "zh")
    catalog.write_text(
        catalog.read_text(encoding="utf-8").replace("值", "外部修改"), encoding="utf-8"
    )
    external = catalog.read_bytes()
    row = session.rows[0].model_dump()
    row["translation"] = "旧页面"

    with pytest.raises(CatalogConflictError):
        service.save_locale(session, [row])
    assert catalog.read_bytes() == external
