from __future__ import annotations

from pathlib import Path

from aetext.legacy_retirement import assess_legacy_retirement


def _catalog(root: Path, name: str, *, legacy: bool) -> None:
    path = root / "_localization" / "catalog" / "NF's Plugins-Filter" / f"{name}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    bindings = ', "bindings": {"Param": {"Token": "L10N_PARAM"}}' if legacy else ""
    path.write_text(f'{{"schemaVersion": 1{bindings}, "translations": {{}}}}\n', encoding="utf-8")


def test_retirement_gate_stays_closed_while_any_legacy_catalog_remains(tmp_path: Path) -> None:
    _catalog(tmp_path, "Legacy", legacy=True)
    _catalog(tmp_path, "Modern", legacy=False)

    report = assess_legacy_retirement(tmp_path)

    assert not report.ready
    assert report.legacy_catalogs == ["NF's Plugins-Filter/Legacy.json"]
    assert (
        "_localization/generator/templates/EffectLegacyAccessor.h.template" in report.remove_paths
    )


def test_nfs_skeleton_is_not_deferred_from_current_content_scope(
    tmp_path: Path,
) -> None:
    _catalog(tmp_path, "Current", legacy=True)
    _catalog(tmp_path, "NFsSkelton", legacy=True)
    _catalog(tmp_path, "Modern", legacy=False)

    report = assess_legacy_retirement(tmp_path)

    assert not report.ready
    assert report.current_target_legacy_catalogs == [
        "NF's Plugins-Filter/Current.json",
        "NF's Plugins-Filter/NFsSkelton.json",
    ]
    assert report.deferred_legacy_catalogs == []
    assert report.source_derived_catalogs == ["NF's Plugins-Filter/Modern.json"]
    assert len(report.legacy_catalogs) == 2


def test_retirement_gate_opens_only_when_all_effect_catalogs_are_source_derived(
    tmp_path: Path,
) -> None:
    _catalog(tmp_path, "Modern", legacy=False)
    settings = tmp_path / "_localization" / "catalog" / "_Support" / "Settings.json"
    settings.parent.mkdir(parents=True)
    settings.write_text('{"schemaVersion": 1, "translations": {}}\n', encoding="utf-8")

    report = assess_legacy_retirement(tmp_path)

    assert report.ready
    assert report.effect_catalog_count == 1
    assert report.legacy_catalogs == []
    assert report.current_target_legacy_catalogs == []
    assert report.deferred_legacy_catalogs == []
    assert report.source_derived_catalogs == ["NF's Plugins-Filter/Modern.json"]
