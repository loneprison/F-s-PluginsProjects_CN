"""AeText domain validation shared by generation, review, and save services."""

from __future__ import annotations

import re

from .models import BindingRecord, EffectCatalog, FamilyDefinition, TranslationTextSource, UseSource
from .popup import popup_structure_issues
from .source_index import ReviewLayout

_NAMED_PLACEHOLDER = re.compile(r"\{[A-Za-z_][A-Za-z0-9_]*\}")
_PRINTF_PLACEHOLDER = re.compile(
    r"%%|%(?:\d+\$)?[-+ #0']*(?:\d+|\*)?(?:\.(?:\d+|\*))?"
    r"(?:hh|h|ll|l|j|z|t|L)?[diuoxXfFeEgGaAcspn]"
)
_PYTHON_ENCODINGS = {
    "windows-1252": "cp1252",
    "windows-932": "cp932",
    "windows-936": "gbk",
    "utf-8": "utf-8",
}


def placeholders(value: str) -> list[str]:
    result = sorted(_NAMED_PLACEHOLDER.findall(value))
    result.extend(
        f"printf:{match}" for match in _PRINTF_PLACEHOLDER.findall(value) if match != "%%"
    )
    return result


def _issue(
    code: str,
    message: str,
    *,
    locale: str,
    stable_id: str,
    arguments: dict[str, object] | None = None,
) -> dict[str, object]:
    result: dict[str, object] = {
        "code": code,
        "severity": "error",
        "message": message,
        "locale": locale,
        "stableId": stable_id,
    }
    if arguments is not None:
        result["arguments"] = arguments
    return result


def validate_catalog_domain(
    catalog: EffectCatalog,
    family: FamilyDefinition,
    bindings: list[BindingRecord],
    review_layout: ReviewLayout,
    *,
    publication: bool = False,
) -> list[dict[str, object]]:
    diagnostics: list[dict[str, object]] = []
    required_locales = set(family.translation_locales())
    actual_locales = set(catalog.translations)
    for locale in sorted(required_locales - actual_locales):
        diagnostics.append(
            {
                "code": "AET2025",
                "severity": "error",
                "message": f"missing family translation locale: {locale}",
            }
        )
    for locale in sorted(actual_locales - required_locales):
        diagnostics.append(
            {
                "code": "AET2026",
                "severity": "error",
                "message": f"locale is not used by this family: {locale}",
            }
        )
    translated_ids = {
        binding.stable_id for binding in bindings if binding.disposition == "translated"
    }
    verbatim_ids = {binding.stable_id for binding in bindings if binding.disposition == "verbatim"}
    expected_roles = {
        entry.stable_id: section.role
        for section in review_layout.sections
        for entry in section.entries
    }
    for locale in sorted(required_locales & actual_locales):
        values = catalog.flatten_locale(locale)
        for role, role_map in catalog.translations[locale].items():
            for stable_id in role_map:
                if stable_id in expected_roles and expected_roles[stable_id] != role:
                    diagnostics.append(
                        _issue(
                            "AET2031",
                            f"translation Role mismatch: locale={locale} id={stable_id} "
                            f"expected={expected_roles[stable_id]} actual={role}",
                            locale=locale,
                            stable_id=stable_id,
                        )
                    )
        for stable_id in sorted(set(values) - translated_ids):
            message = (
                f"Verbatim binding must not appear in translations: {stable_id}"
                if stable_id in verbatim_ids
                else f"translation has no live translated binding: {stable_id}"
            )
            diagnostics.append(_issue("AET3020", message, locale=locale, stable_id=stable_id))
        for stable_id in sorted(translated_ids):
            if stable_id not in values or values[stable_id] is None:
                missing = stable_id not in values
                diagnostic = _issue(
                    "AET3021" if missing else "AET3022",
                    f"{'missing' if missing else 'incomplete'} translation: "
                    f"locale={locale} id={stable_id}",
                    locale=locale,
                    stable_id=stable_id,
                )
                diagnostic["severity"] = "error" if publication else "warning"
                diagnostics.append(diagnostic)
            elif values[stable_id] == "":
                diagnostics.append(
                    _issue(
                        "AET3023",
                        f"translation must not be empty: locale={locale} id={stable_id}",
                        locale=locale,
                        stable_id=stable_id,
                    )
                )
    profiles_by_locale: dict[str, list[str]] = {}
    for variant in family.variants:
        source = variant.text_source
        if isinstance(source, TranslationTextSource):
            profiles_by_locale.setdefault(source.locale, []).append(variant.encoding_profile)
    locale_maps = {locale: catalog.flatten_locale(locale) for locale in catalog.translations}

    for binding in bindings:
        if binding.disposition != "translated":
            continue
        for locale in family.translation_locales():
            if locale not in catalog.translations:
                continue
            locale_map = locale_maps[locale]
            if binding.stable_id not in locale_map:
                continue
            value = locale_map[binding.stable_id]
            if value is None:
                continue
            translated = binding.original if isinstance(value, UseSource) else value
            if placeholders(binding.original) != placeholders(translated):
                diagnostics.append(
                    _issue(
                        "AET3030",
                        f"placeholder mismatch: locale={locale} id={binding.stable_id}",
                        locale=locale,
                        stable_id=binding.stable_id,
                    )
                )
            if binding.role == "Popup":
                structure_issues = popup_structure_issues(binding.original, translated)
                item_count_issue = next(
                    (item for item in structure_issues if item.kind == "item-count"),
                    None,
                )
                if item_count_issue is not None:
                    diagnostics.append(
                        _issue(
                            "AET3031",
                            "Popup structure mismatch: "
                            f"locale={locale} id={binding.stable_id} "
                            f"expected_items={item_count_issue.expected_count}",
                            locale=locale,
                            stable_id=binding.stable_id,
                            arguments={
                                "expectedItems": item_count_issue.expected_count,
                                "actualItems": item_count_issue.actual_count,
                            },
                        )
                    )
                else:
                    empty_indices = [
                        item.index for item in structure_issues if item.kind == "empty-item"
                    ]
                    if empty_indices:
                        diagnostics.append(
                            _issue(
                                "AET3032",
                                f"Popup empty-item structure mismatch: locale={locale} "
                                f"id={binding.stable_id}",
                                locale=locale,
                                stable_id=binding.stable_id,
                                arguments={
                                    "indices": ", ".join(str(index) for index in empty_indices)
                                },
                            )
                        )
                    separator_indices = [
                        item.index for item in structure_issues if item.kind == "separator"
                    ]
                    if separator_indices:
                        diagnostics.append(
                            _issue(
                                "AET3033",
                                f"Popup separator structure mismatch: locale={locale} "
                                f"id={binding.stable_id}",
                                locale=locale,
                                stable_id=binding.stable_id,
                                arguments={
                                    "indices": ", ".join(str(index) for index in separator_indices)
                                },
                            )
                        )
            profiles = list(profiles_by_locale.get(locale, []))
            if binding.role in {"About", "Error"} and "utf-8" not in profiles:
                profiles.append("utf-8")
            limit = 31 if binding.role in {"Param", "Topic"} else 255
            for profile in profiles:
                codec = _PYTHON_ENCODINGS.get(profile)
                if codec is None:
                    diagnostics.append(
                        _issue(
                            "AET4001",
                            f"unsupported review encoding profile: {profile}",
                            locale=locale,
                            stable_id=binding.stable_id,
                            arguments={"profile": profile},
                        )
                    )
                    continue
                try:
                    encoded = translated.encode(codec, errors="strict")
                except UnicodeEncodeError:
                    diagnostics.append(
                        _issue(
                            "AET4002",
                            f"translation is not encodable as {profile}: "
                            f"locale={locale} id={binding.stable_id}",
                            locale=locale,
                            stable_id=binding.stable_id,
                            arguments={"profile": profile},
                        )
                    )
                    continue
                if len(encoded) > limit:
                    diagnostics.append(
                        _issue(
                            "AET4003",
                            f"text exceeds {limit}-byte limit: locale={locale} "
                            f"id={binding.stable_id} profile={profile} bytes={len(encoded)}",
                            locale=locale,
                            stable_id=binding.stable_id,
                            arguments={"profile": profile, "limit": limit, "bytes": len(encoded)},
                        )
                    )
    return diagnostics


def has_errors(diagnostics: list[dict[str, object]]) -> bool:
    return any(diagnostic.get("severity") == "error" for diagnostic in diagnostics)
