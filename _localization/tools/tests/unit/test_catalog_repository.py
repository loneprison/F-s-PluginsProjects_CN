from __future__ import annotations

import json
from pathlib import Path

import pytest

from aetext.catalog.repository import CatalogConflictError, CatalogRepository


def _write_catalog(root: Path) -> Path:
    path = root / "_localization" / "catalog" / "fixture.json"
    path.parent.mkdir(parents=True)
    path.write_text(
        json.dumps(
            {
                "schemaVersion": 1,
                "translations": {
                    "en": {"Param": {"L10N_VALUE": {"useSource": True}}},
                    "zh": {"Param": {"L10N_VALUE": "值"}},
                },
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def test_save_changes_only_selected_locale(tmp_path: Path) -> None:
    path = _write_catalog(tmp_path)
    repository = CatalogRepository(tmp_path)
    snapshot = repository.load(path)
    before_en = snapshot.catalog.model_dump(by_alias=True)["translations"]["en"]

    saved = repository.save_locale(snapshot, "zh", {"Param": {"L10N_VALUE": "新值"}})

    document = saved.catalog.model_dump(by_alias=True)
    assert document["translations"]["en"] == before_en
    assert document["translations"]["zh"] == {"Param": {"L10N_VALUE": "新值"}}


def test_save_compacts_exact_use_source_objects(tmp_path: Path) -> None:
    path = _write_catalog(tmp_path)
    repository = CatalogRepository(tmp_path)
    snapshot = repository.load(path)

    repository.save_locale(
        snapshot,
        "en",
        {"Param": {"L10N_VALUE": {"useSource": True}}},
    )

    contents = path.read_text(encoding="utf-8")
    assert '"L10N_VALUE": {"useSource": true}' in contents
    assert '"L10N_VALUE": {\n' not in contents


def test_stale_snapshot_cannot_overwrite_external_change(tmp_path: Path) -> None:
    path = _write_catalog(tmp_path)
    repository = CatalogRepository(tmp_path)
    snapshot = repository.load(path)
    external = path.read_text(encoding="utf-8").replace("值", "外部修改")
    path.write_text(external, encoding="utf-8")

    with pytest.raises(CatalogConflictError):
        repository.save_locale(snapshot, "zh", {"Param": {"L10N_VALUE": "旧页面"}})

    assert "外部修改" in path.read_text(encoding="utf-8")


def test_save_updates_only_selected_locale_workflow(tmp_path: Path) -> None:
    path = _write_catalog(tmp_path)
    repository = CatalogRepository(tmp_path)
    first = repository.load(path)
    with_workflow = repository.save_locale(
        first,
        "zh",
        {"Param": {"L10N_VALUE": "值"}},
        {"Param": {"L10N_VALUE": "reviewed"}},
    )
    repository.save_locale(
        with_workflow,
        "en",
        {"Param": {"L10N_VALUE": {"useSource": True}}},
        {},
    )

    document = json.loads(path.read_text(encoding="utf-8"))
    assert document["workflow"] == {"zh": {"Param": {"L10N_VALUE": "reviewed"}}}


def test_repository_rejects_catalog_outside_root(tmp_path: Path) -> None:
    repository = CatalogRepository(tmp_path)
    outside = tmp_path / "outside.json"
    outside.write_text("{}", encoding="utf-8")

    with pytest.raises(ValueError):
        repository.load(outside)
