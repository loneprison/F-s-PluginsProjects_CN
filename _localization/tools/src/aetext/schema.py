"""Explicit catalog synchronization from catalog, family and scanner-report files."""

from __future__ import annotations

from pydantic import TypeAdapter, ValidationError

from .catalog.models import BindingRecord, EffectCatalog, FamilyDefinition, TranslationSections
from .catalog.source_index import ReviewLayout


def synchronize_effect_catalog(
    document: object,
    family: object,
    bindings: object,
    *,
    prune: bool,
    review_layout: object,
) -> dict[str, object]:
    """Prepare an explicit sync result without mutating the supplied catalog."""

    result: dict[str, object] = {
        "catalog": document,
        "added": [],
        "orphans": [],
        "pruned": [],
        "diagnostics": [],
    }
    try:
        catalog = EffectCatalog.model_validate(document, strict=True)
        definition = FamilyDefinition.model_validate(family, strict=True)
        records = TypeAdapter(list[BindingRecord]).validate_python(bindings, strict=True)
        layout = ReviewLayout.model_validate(review_layout, strict=True)
        required_order = definition.translation_locales()
        if set(catalog.translations) != set(required_order):
            raise ValueError("sync requires the exact family translation locale set")
        translated = {record.stable_id for record in records if record.disposition == "translated"}
        verbatim = {record.stable_id for record in records if record.disposition == "verbatim"}
        if translated & verbatim:
            raise ValueError("scanner report contains inconsistent binding policies")
        if set(layout.stable_ids()) != translated:
            raise ValueError("scanner report layout does not match its translated bindings")
    except (ValidationError, ValueError) as error:
        result["diagnostics"] = [{"code": "AET2001", "severity": "error", "message": str(error)}]
        return result

    added: list[dict[str, str]] = []
    orphans: list[dict[str, str]] = []
    pruned: list[dict[str, str]] = []
    ordered_translations = {}
    for locale in required_order:
        locale_map = catalog.flatten_locale(locale)
        locale_roles = {
            stable_id: role
            for role, values in catalog.translations[locale].items()
            for stable_id in values
        }
        for stable_id in sorted(translated - set(locale_map)):
            locale_map[stable_id] = None
            added.append({"locale": locale, "stableId": stable_id})
        orphan_ids = sorted(set(locale_map) - translated)
        for stable_id in orphan_ids:
            orphan = {"locale": locale, "stableId": stable_id}
            orphans.append(orphan)
            if prune:
                pruned.append(orphan)
        ordered_locale = layout.canonicalize(
            {stable_id: value for stable_id, value in locale_map.items() if stable_id in translated}
        )
        if not prune:
            for stable_id in orphan_ids:
                ordered_locale.setdefault(locale_roles[stable_id], {})[stable_id] = locale_map[
                    stable_id
                ]
        ordered_translations[locale] = ordered_locale
    result.update(
        catalog={
            "schemaVersion": 1,
            "translations": TypeAdapter(dict[str, TranslationSections]).dump_python(
                ordered_translations, by_alias=True
            ),
        },
        added=added,
        orphans=orphans,
        pruned=pruned,
        verbatimIds=sorted(verbatim),
    )
    return result
