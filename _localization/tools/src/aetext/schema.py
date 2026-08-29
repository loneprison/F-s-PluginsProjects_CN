"""Validation for family-driven AeText generation and effect catalog data."""

from __future__ import annotations

import copy
import re
from collections.abc import Mapping, Sequence

from pydantic import ValidationError

from .catalog.models import FamilyDefinition
from .core.scanner_contract import ROLE_ORDER

_ASCII_ID = re.compile(r"^[\x21-\x7E]+$")
_STABLE_TEXT_ID = re.compile(r"^L10N_[A-Z0-9]+(?:_[A-Z0-9]+)*$")
_ENCODING_PROFILES = {
    "windows-1252",
    "windows-932",
    "windows-936",
    "windows-936-ae-display",
    "utf-8",
}
_ROLE_NAMES = set(ROLE_ORDER)


def _issue(code: str, severity: str, message: str) -> dict[str, object]:
    return {"code": code, "severity": severity, "message": message}


def _is_object(value: object) -> bool:
    return isinstance(value, Mapping)


def _is_array(value: object) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray))


def _unknown_fields(
    value: Mapping[str, object],
    allowed: set[str],
    name: str,
    diagnostics: list[dict[str, object]],
) -> None:
    for field in sorted(set(value) - allowed):
        diagnostics.append(_issue("AET2001", "error", f"unknown {name} field: {field}"))


def _valid_ascii_id(value: object) -> bool:
    return isinstance(value, str) and bool(value) and _ASCII_ID.fullmatch(value) is not None


def validate_family_definition(document: object) -> list[dict[str, object]]:
    diagnostics: list[dict[str, object]] = []
    if not _is_object(document):
        return [_issue("AET2002", "error", "family definition root must be an object")]
    root = document
    _unknown_fields(
        root,
        {"schemaVersion", "familyId", "sourceVariantId", "variants"},
        "family definition",
        diagnostics,
    )
    if root.get("schemaVersion") != 1:
        diagnostics.append(_issue("AET2003", "error", "family schemaVersion must equal 1"))
    if not _valid_ascii_id(root.get("familyId")):
        diagnostics.append(
            _issue("AET2004", "error", "familyId must be a nonempty stable ASCII ID")
        )
    source_variant_id = root.get("sourceVariantId")
    if not _valid_ascii_id(source_variant_id):
        diagnostics.append(
            _issue("AET2005", "error", "sourceVariantId must be a nonempty stable ASCII ID")
        )
    variants = root.get("variants")
    if not _is_array(variants) or not variants:
        diagnostics.append(_issue("AET2006", "error", "variants must be a nonempty array"))
        return diagnostics

    variants_by_id: dict[str, Mapping[str, object]] = {}
    locale_definitions: dict[str, list[tuple[str, str]]] = {}
    for index, variant_value in enumerate(variants):
        name = f"variants[{index}]"
        if not _is_object(variant_value):
            diagnostics.append(_issue("AET2007", "error", f"{name} must be an object"))
            continue
        variant = variant_value
        _unknown_fields(variant, {"id", "textSource", "encodingProfile"}, name, diagnostics)
        variant_id = variant.get("id")
        if not _valid_ascii_id(variant_id):
            diagnostics.append(
                _issue("AET2008", "error", f"{name}.id must be a nonempty stable ASCII ID")
            )
        elif variant_id in variants_by_id:
            diagnostics.append(_issue("AET2009", "error", f"duplicate Variant ID: {variant_id}"))
        else:
            variants_by_id[str(variant_id)] = variant

        encoding_profile = variant.get("encodingProfile")
        if encoding_profile not in _ENCODING_PROFILES:
            diagnostics.append(
                _issue("AET2010", "error", f"unregistered encoding profile: {encoding_profile}")
            )
        text_source_value = variant.get("textSource")
        if not _is_object(text_source_value):
            diagnostics.append(_issue("AET2011", "error", f"{name}.textSource must be an object"))
            continue
        text_source = text_source_value
        _unknown_fields(text_source, {"kind", "locale"}, f"{name}.textSource", diagnostics)
        kind = text_source.get("kind")
        if kind == "source":
            if "locale" in text_source:
                diagnostics.append(
                    _issue(
                        "AET2012", "error", f"source Variant must not carry locale: {variant_id}"
                    )
                )
        elif kind == "translation":
            locale = text_source.get("locale")
            if not _valid_ascii_id(locale):
                diagnostics.append(
                    _issue(
                        "AET2013",
                        "error",
                        (
                            "translation Variant requires a nonempty stable ASCII locale: "
                            f"{variant_id}"
                        ),
                    )
                )
            else:
                locale_definitions.setdefault(str(locale), []).append(
                    (str(variant_id), str(encoding_profile))
                )
        else:
            diagnostics.append(
                _issue(
                    "AET2014", "error", f"unknown textSource kind for Variant {variant_id}: {kind}"
                )
            )

    if isinstance(source_variant_id, str):
        source_variant = variants_by_id.get(source_variant_id)
        if source_variant is None:
            diagnostics.append(
                _issue(
                    "AET2015",
                    "error",
                    f"sourceVariantId does not name a Variant: {source_variant_id}",
                )
            )
        else:
            text_source = source_variant.get("textSource")
            if not _is_object(text_source) or text_source.get("kind") != "source":
                diagnostics.append(
                    _issue("AET2016", "error", "sourceVariantId must name a source Variant")
                )

    for locale, definitions in locale_definitions.items():
        seen_variants = {variant_id for variant_id, _ in definitions}
        if len(seen_variants) != len(definitions):
            diagnostics.append(
                _issue("AET2017", "error", f"contradictory translation definitions: {locale}")
            )
    return diagnostics


def _family_model(family: object) -> FamilyDefinition | None:
    try:
        return FamilyDefinition.model_validate(family, strict=True)
    except ValidationError:
        return None


def _required_locale_order(family: object) -> list[str]:
    model = _family_model(family)
    return [] if model is None else model.translation_locales()


def _binding_maps(
    bindings: object,
    diagnostics: list[dict[str, object]],
) -> tuple[set[str], set[str]]:
    translated: set[str] = set()
    verbatim: set[str] = set()
    policies: dict[str, set[str]] = {}
    if not _is_array(bindings):
        diagnostics.append(_issue("AET2018", "error", "bindings must be an array"))
        return translated, verbatim
    for index, binding_value in enumerate(bindings):
        if not _is_object(binding_value):
            diagnostics.append(_issue("AET2019", "error", f"bindings[{index}] must be an object"))
            continue
        stable_id = binding_value.get("stableId")
        disposition = binding_value.get("disposition")
        if not isinstance(stable_id, str) or _STABLE_TEXT_ID.fullmatch(stable_id) is None:
            diagnostics.append(
                _issue("AET2020", "error", f"invalid binding stable ID: {stable_id}")
            )
            continue
        if disposition not in ("translated", "verbatim"):
            diagnostics.append(
                _issue("AET2021", "error", f"invalid binding disposition: {stable_id}")
            )
            continue
        policies.setdefault(stable_id, set()).add(str(disposition))
        (translated if disposition == "translated" else verbatim).add(stable_id)
    for stable_id, dispositions in policies.items():
        if len(dispositions) > 1:
            diagnostics.append(
                _issue(
                    "AET1020",
                    "error",
                    f"inconsistent binding policy for stable ID: {stable_id}",
                )
            )
    return translated, verbatim


def flatten_role_sections(sections: object) -> dict[str, object]:
    if not _is_object(sections):
        raise ValueError("Role sections must be an object")
    result: dict[str, object] = {}
    for role, role_value in sections.items():
        if role not in _ROLE_NAMES or not _is_object(role_value):
            raise ValueError(f"invalid Role section: {role}")
        for stable_id, value in role_value.items():
            if stable_id in result:
                raise ValueError(f"stable ID appears in multiple Role sections: {stable_id}")
            result[str(stable_id)] = value
    return result


def _flatten_role_sections(
    sections: object,
    name: str,
    diagnostics: list[dict[str, object]],
) -> tuple[dict[str, object], dict[str, str]]:
    values: dict[str, object] = {}
    roles: dict[str, str] = {}
    if not _is_object(sections):
        diagnostics.append(_issue("AET2027", "error", f"{name} must be an object"))
        return values, roles
    for role, role_value in sections.items():
        if role not in _ROLE_NAMES:
            diagnostics.append(_issue("AET2028", "error", f"unsupported Role section: {role}"))
            continue
        if not _is_object(role_value):
            diagnostics.append(_issue("AET2027", "error", f"{name}.{role} must be an object"))
            continue
        for stable_id, value in role_value.items():
            stable_id = str(stable_id)
            if stable_id in values:
                diagnostics.append(
                    _issue(
                        "AET2029",
                        "error",
                        f"stable ID appears in multiple Role sections: {stable_id}",
                    )
                )
                continue
            values[stable_id] = value
            roles[stable_id] = str(role)
    return values, roles


def _layout_entries(review_layout: object, bindings: object) -> list[tuple[str, str]]:
    if _is_object(review_layout) and _is_array(review_layout.get("sections")):
        result: list[tuple[str, str]] = []
        for section in review_layout["sections"]:
            if not _is_object(section) or not _is_array(section.get("entries")):
                raise ValueError("reviewLayout sections must contain entries")
            role = section.get("role")
            if role not in _ROLE_NAMES:
                raise ValueError(f"reviewLayout has unsupported Role: {role}")
            for entry in section["entries"]:
                if not _is_object(entry) or entry.get("primaryRole") != role:
                    raise ValueError("reviewLayout entry primary Role mismatch")
                result.append((str(role), str(entry.get("stableId"))))
        return result
    if not _is_array(bindings):
        return []
    first_roles: dict[str, str] = {}
    for binding in bindings:
        if not _is_object(binding) or binding.get("disposition") != "translated":
            continue
        stable_id = str(binding.get("stableId"))
        role = str(binding.get("role"))
        previous = first_roles.get(stable_id)
        if previous is None or ROLE_ORDER.get(role, 999) < ROLE_ORDER.get(previous, 999):
            first_roles[stable_id] = role
    return sorted(
        ((role, stable_id) for stable_id, role in first_roles.items()),
        key=lambda item: (ROLE_ORDER[item[0]], item[1]),
    )


def canonicalize_role_sections(
    values: Mapping[str, object],
    review_layout: object,
    bindings: object = None,
) -> dict[str, dict[str, object]]:
    entries = _layout_entries(review_layout, bindings)
    expected = {stable_id for _, stable_id in entries}
    unknown = sorted(set(values) - expected)
    if unknown:
        raise ValueError(f"values are absent from reviewLayout: {', '.join(unknown)}")
    result: dict[str, dict[str, object]] = {}
    for role, stable_id in entries:
        if stable_id in values:
            result.setdefault(role, {})[stable_id] = values[stable_id]
    return result


def validate_effect_catalog(
    document: object,
    family: object,
    bindings: object,
    *,
    publication: bool,
    review_layout: object = None,
) -> list[dict[str, object]]:
    diagnostics = list(validate_family_definition(family))
    family_model = _family_model(family)
    if family_model is None:
        return diagnostics
    required_locales = set(family_model.translation_locales())
    translated, verbatim = _binding_maps(bindings, diagnostics)
    if not _is_object(document):
        diagnostics.append(_issue("AET2022", "error", "effect catalog root must be an object"))
        return diagnostics
    root = document
    _unknown_fields(
        root,
        {"schemaVersion", "translations", "workflow"},
        "effect catalog",
        diagnostics,
    )
    if root.get("schemaVersion") != 1:
        diagnostics.append(_issue("AET2023", "error", "effect schemaVersion must equal 1"))
    translations_value = root.get("translations")
    if not _is_object(translations_value):
        diagnostics.append(_issue("AET2024", "error", "translations must be an object"))
        return diagnostics
    translations = translations_value
    actual_locales = set(translations)
    for locale in sorted(required_locales - actual_locales):
        diagnostics.append(
            _issue("AET2025", "error", f"missing family translation locale: {locale}")
        )
    for locale in sorted(actual_locales - required_locales):
        diagnostics.append(
            _issue("AET2026", "error", f"locale is not used by this family: {locale}")
        )

    incomplete_severity = "error" if publication else "warning"
    for locale in sorted(required_locales & actual_locales):
        translation_map, actual_roles = _flatten_role_sections(
            translations.get(locale),
            f"translations.{locale}",
            diagnostics,
        )
        try:
            expected_roles = {
                stable_id: role for role, stable_id in _layout_entries(review_layout, bindings)
            }
        except ValueError as error:
            diagnostics.append(_issue("AET2030", "error", str(error)))
            expected_roles = {}
        for stable_id, role in sorted(actual_roles.items()):
            if stable_id in expected_roles and expected_roles[stable_id] != role:
                diagnostics.append(
                    _issue(
                        "AET2031",
                        "error",
                        f"translation Role mismatch: locale={locale} id={stable_id} "
                        f"expected={expected_roles[stable_id]} actual={role}",
                    )
                )
        for stable_id in sorted(set(translation_map) - translated):
            message = (
                f"Verbatim binding must not appear in translations: {stable_id}"
                if stable_id in verbatim
                else f"translation has no live translated binding: {stable_id}"
            )
            diagnostics.append(_issue("AET3020", "error", message))
        for stable_id in sorted(translated):
            if stable_id not in translation_map:
                diagnostics.append(
                    _issue(
                        "AET3021",
                        incomplete_severity,
                        f"missing translation: locale={locale} id={stable_id}",
                    )
                )
                continue
            value = translation_map[stable_id]
            if value is None:
                diagnostics.append(
                    _issue(
                        "AET3022",
                        incomplete_severity,
                        f"incomplete translation: locale={locale} id={stable_id}",
                    )
                )
            elif isinstance(value, str):
                if not value:
                    diagnostics.append(
                        _issue(
                            "AET3023",
                            "error",
                            f"translation must not be empty: locale={locale} id={stable_id}",
                        )
                    )
            elif _is_object(value):
                if dict(value) != {"useSource": True}:
                    diagnostics.append(
                        _issue(
                            "AET3024",
                            "error",
                            (
                                "translation object must be exact useSource: "
                                f"locale={locale} id={stable_id}"
                            ),
                        )
                    )
            else:
                diagnostics.append(
                    _issue(
                        "AET3025",
                        "error",
                        f"invalid translation value: locale={locale} id={stable_id}",
                    )
                )
    return diagnostics


def synchronize_effect_catalog(
    document: object,
    family: object,
    bindings: object,
    *,
    prune: bool,
    review_layout: object = None,
) -> dict[str, object]:
    """Prepare an explicit sync result without mutating the supplied catalog."""

    diagnostics = list(validate_family_definition(family))
    if not _is_object(family) or not _is_object(document):
        diagnostics.append(_issue("AET2022", "error", "effect catalog root must be an object"))
        return {
            "catalog": document,
            "added": [],
            "orphans": [],
            "pruned": [],
            "diagnostics": diagnostics,
        }
    translated, verbatim = _binding_maps(bindings, diagnostics)
    if document.get("schemaVersion") != 1 or not _is_object(document.get("translations")):
        diagnostics.append(
            _issue("AET2024", "error", "sync requires a schemaVersion 1 translations object")
        )
        return {
            "catalog": document,
            "added": [],
            "orphans": [],
            "pruned": [],
            "diagnostics": diagnostics,
        }

    result = copy.deepcopy(document)
    translations = result["translations"]
    assert isinstance(translations, dict)
    required_order = _required_locale_order(family)
    if set(translations) != set(required_order):
        diagnostics.append(
            _issue("AET2026", "error", "sync requires the exact family translation locale set")
        )
        return {
            "catalog": document,
            "added": [],
            "orphans": [],
            "pruned": [],
            "diagnostics": diagnostics,
        }

    added: list[dict[str, str]] = []
    orphans: list[dict[str, str]] = []
    pruned: list[dict[str, str]] = []
    ordered_translations: dict[str, object] = {}
    for locale in required_order:
        locale_map, locale_roles = _flatten_role_sections(
            translations[locale],
            f"translations.{locale}",
            diagnostics,
        )
        for stable_id in sorted(translated):
            if stable_id not in locale_map:
                locale_map[stable_id] = None
                added.append({"locale": locale, "stableId": stable_id})
        for stable_id in sorted(set(locale_map) - translated):
            orphan = {"locale": locale, "stableId": stable_id}
            orphans.append(orphan)
            if prune:
                del locale_map[stable_id]
                pruned.append(orphan)
        try:
            ordered_locale = canonicalize_role_sections(
                {
                    stable_id: value
                    for stable_id, value in locale_map.items()
                    if stable_id in translated
                },
                review_layout,
                bindings,
            )
            if not prune:
                for stable_id in sorted(set(locale_map) - translated):
                    role = locale_roles.get(stable_id)
                    if role in _ROLE_NAMES:
                        ordered_locale.setdefault(role, {})[stable_id] = locale_map[stable_id]
            ordered_translations[locale] = ordered_locale
        except ValueError as error:
            diagnostics.append(_issue("AET2030", "error", str(error)))
    result["translations"] = ordered_translations
    return {
        "catalog": result,
        "added": added,
        "orphans": orphans,
        "pruned": pruned,
        "verbatimIds": sorted(verbatim),
        "diagnostics": diagnostics,
    }
