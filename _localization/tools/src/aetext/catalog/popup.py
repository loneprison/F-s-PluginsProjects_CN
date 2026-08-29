"""Adobe Effect popup string structure shared by validation and review UI."""

from __future__ import annotations

POPUP_SEPARATOR = "(-"


def split_popup(value: str) -> list[str]:
    return value.split("|")


def popup_structure_errors(original: str, translated: str) -> list[str]:
    original_items = split_popup(original)
    translated_items = split_popup(translated)
    if len(original_items) != len(translated_items):
        return [
            f"项数应为 {len(original_items)}，当前为 {len(translated_items)}"  # noqa: RUF001
        ]

    errors: list[str] = []
    for index, (original_item, translated_item) in enumerate(
        zip(original_items, translated_items, strict=True),
        start=1,
    ):
        if (original_item == "") != (translated_item == ""):
            errors.append(f"第 {index} 项的空项结构与原文不一致")
        if (original_item == POPUP_SEPARATOR) != (translated_item == POPUP_SEPARATOR):
            errors.append(f"第 {index} 项的分隔符结构与原文不一致")
    return errors
