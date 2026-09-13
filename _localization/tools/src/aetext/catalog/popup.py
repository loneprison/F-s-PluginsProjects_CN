"""Adobe Effect popup string structure shared by validation and review UI."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

POPUP_SEPARATOR = "(-"

PopupStructureIssueKind = Literal["item-count", "empty-item", "separator"]


@dataclass(frozen=True)
class PopupStructureIssue:
    kind: PopupStructureIssueKind
    index: int | None = None
    expected_count: int | None = None
    actual_count: int | None = None

    def english_message(self) -> str:
        if self.kind == "item-count":
            return f"expected {self.expected_count} items; found {self.actual_count}"
        if self.kind == "empty-item":
            return f"item {self.index} does not match the source empty-item structure"
        return f"item {self.index} does not match the source separator structure"


def split_popup(value: str) -> list[str]:
    return value.split("|")


def popup_structure_issues(original: str, translated: str) -> list[PopupStructureIssue]:
    original_items = split_popup(original)
    translated_items = split_popup(translated)
    if len(original_items) != len(translated_items):
        return [
            PopupStructureIssue(
                kind="item-count",
                expected_count=len(original_items),
                actual_count=len(translated_items),
            )
        ]

    issues: list[PopupStructureIssue] = []
    for index, (original_item, translated_item) in enumerate(
        zip(original_items, translated_items, strict=True),
        start=1,
    ):
        if (original_item == "") != (translated_item == ""):
            issues.append(PopupStructureIssue(kind="empty-item", index=index))
        if (original_item == POPUP_SEPARATOR) != (translated_item == POPUP_SEPARATOR):
            issues.append(PopupStructureIssue(kind="separator", index=index))
    return issues
