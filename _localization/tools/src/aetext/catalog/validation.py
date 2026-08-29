"""AeText domain validation shared by generation, review, and save services."""

from __future__ import annotations

import re

from ..schema import validate_effect_catalog
from .models import BindingRecord, EffectCatalog, FamilyDefinition, TranslationTextSource, UseSource
from .popup import popup_structure_errors
from .source_index import ReviewLayout

_NAMED_PLACEHOLDER = re.compile(r"\{[A-Za-z_][A-Za-z0-9_]*\}")
_PRINTF_PLACEHOLDER = re.compile(
    r"%(?:\d+\$)?[-+ #0']*(?:\d+|\*)?(?:\.(?:\d+|\*))?"
    r"(?:hh|h|ll|l|j|z|t|L)?[diuoxXfFeEgGaAcspn]"
)
_PYTHON_ENCODINGS = {
    "windows-1252": "cp1252",
    "windows-932": "cp932",
    "windows-936": "gbk",
    "utf-8": "utf-8",
}


def placeholders(value: str) -> list[str]:
    result = _NAMED_PLACEHOLDER.findall(value)
    result.extend(f"printf:{match}" for match in _PRINTF_PLACEHOLDER.findall(value))
    return sorted(result)


def _issue(
    code: str,
    message: str,
    *,
    locale: str,
    stable_id: str,
) -> dict[str, object]:
    return {
        "code": code,
        "severity": "error",
        "message": message,
        "locale": locale,
        "stableId": stable_id,
    }


def validate_catalog_domain(
    catalog: EffectCatalog,
    family: FamilyDefinition,
    bindings: list[BindingRecord],
    review_layout: ReviewLayout | None = None,
    *,
    publication: bool = False,
) -> list[dict[str, object]]:
    raw_bindings = [binding.model_dump(by_alias=True) for binding in bindings]
    diagnostics = validate_effect_catalog(
        catalog.model_dump(by_alias=True),
        family.model_dump(by_alias=True),
        raw_bindings,
        publication=publication,
        review_layout=None if review_layout is None else review_layout.model_dump(by_alias=True),
    )
    profiles_by_locale: dict[str, list[str]] = {}
    for variant in family.variants:
        source = variant.text_source
        if isinstance(source, TranslationTextSource):
            profiles_by_locale.setdefault(source.locale, []).append(variant.encoding_profile)

    for binding in bindings:
        if binding.disposition != "translated" or binding.original is None:
            continue
        for locale in family.translation_locales():
            if locale not in catalog.translations:
                continue
            locale_map = catalog.flatten_locale(locale)
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
                original_items = binding.original.split("|")
                translated_items = translated.split("|")
                if len(original_items) != len(translated_items):
                    diagnostics.append(
                        _issue(
                            "AET3031",
                            "Popup structure mismatch: "
                            f"locale={locale} id={binding.stable_id} "
                            f"expected_items={len(original_items)}",
                            locale=locale,
                            stable_id=binding.stable_id,
                        )
                    )
                else:
                    structure_errors = popup_structure_errors(binding.original, translated)
                    if any("空项" in message for message in structure_errors):
                        diagnostics.append(
                            _issue(
                                "AET3032",
                                f"Popup empty-item structure mismatch: locale={locale} "
                                f"id={binding.stable_id}",
                                locale=locale,
                                stable_id=binding.stable_id,
                            )
                        )
                    if any("分隔符" in message for message in structure_errors):
                        diagnostics.append(
                            _issue(
                                "AET3033",
                                f"Popup separator structure mismatch: locale={locale} "
                                f"id={binding.stable_id}",
                                locale=locale,
                                stable_id=binding.stable_id,
                            )
                        )
            if binding.role == "Error":
                continue
            for profile in profiles_by_locale.get(locale, []):
                codec = _PYTHON_ENCODINGS.get(profile)
                if codec is None:
                    diagnostics.append(
                        _issue(
                            "AET4001",
                            f"unsupported review encoding profile: {profile}",
                            locale=locale,
                            stable_id=binding.stable_id,
                        )
                    )
                    continue
                try:
                    translated.encode(codec, errors="strict")
                except UnicodeEncodeError:
                    diagnostics.append(
                        _issue(
                            "AET4002",
                            f"translation is not encodable as {profile}: "
                            f"locale={locale} id={binding.stable_id}",
                            locale=locale,
                            stable_id=binding.stable_id,
                        )
                    )
    return diagnostics


def has_errors(diagnostics: list[dict[str, object]]) -> bool:
    return any(diagnostic.get("severity") == "error" for diagnostic in diagnostics)
