"""Structural gate for removing the temporary legacy catalog generation path."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

_REMOVE_PATHS = (
    "_localization/generator/templates/EffectLegacyAccessor.h.template",
    "_localization/generator/templates/EffectLegacyRole.h.template",
)
_REMOVE_SYMBOLS = (
    "_localization/generator/Catalog.ps1 legacy bindings schema branch",
    "_localization/generator/EffectGenerator.ps1 Legacy mode",
    "_localization/AeText.h AeText::LegacyAboutText and Client::LegacyAbout",
    "_localization/core/AeTextClient.cpp Client::LegacyAbout implementation",
)


@dataclass(frozen=True)
class LegacyRetirementReport:
    ready: bool
    effect_catalog_count: int
    legacy_catalogs: list[str]
    current_target_legacy_catalogs: list[str]
    deferred_legacy_catalogs: list[str]
    source_derived_catalogs: list[str]
    invalid_catalogs: list[str]
    remove_paths: tuple[str, ...]
    remove_symbols: tuple[str, ...]


def assess_legacy_retirement(root: str | Path) -> LegacyRetirementReport:
    repository = Path(root).resolve()
    catalog_root = repository / "_localization" / "catalog"
    legacy: list[str] = []
    current_target_legacy: list[str] = []
    deferred_legacy: list[str] = []
    source_derived: list[str] = []
    invalid: list[str] = []
    effect_count = 0
    for path in sorted(catalog_root.rglob("*.json")):
        relative = path.relative_to(catalog_root).as_posix()
        if relative.startswith("_Support/"):
            continue
        effect_count += 1
        try:
            document = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            invalid.append(relative)
            continue
        if not isinstance(document, dict) or not isinstance(document.get("translations"), dict):
            invalid.append(relative)
        elif "bindings" in document:
            legacy.append(relative)
            current_target_legacy.append(relative)
        else:
            source_derived.append(relative)
    return LegacyRetirementReport(
        ready=effect_count > 0 and not legacy and not invalid,
        effect_catalog_count=effect_count,
        legacy_catalogs=legacy,
        current_target_legacy_catalogs=current_target_legacy,
        deferred_legacy_catalogs=deferred_legacy,
        source_derived_catalogs=source_derived,
        invalid_catalogs=invalid,
        remove_paths=_REMOVE_PATHS,
        remove_symbols=_REMOVE_SYMBOLS,
    )
