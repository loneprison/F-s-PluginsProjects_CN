"""Stable report helpers shared by the Tree-sitter scanner and its consumers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ROLE_ORDER = {
    "Param": 0,
    "Label": 1,
    "Popup": 2,
    "Topic": 3,
    "About": 4,
    "Error": 5,
}
WRAPPERS = {
    "AETEXT_PARAM": ("Param", "translated"),
    "AETEXT_LABEL": ("Label", "translated"),
    "AETEXT_POPUP": ("Popup", "translated"),
    "AETEXT_TOPIC": ("Topic", "translated"),
    "AETEXT_ABOUT": ("About", "translated"),
    "AETEXT_ERROR": ("Error", "translated"),
    "AETEXT_VERBATIM_PARAM": ("Param", "verbatim"),
    "AETEXT_VERBATIM_LABEL": ("Label", "verbatim"),
    "AETEXT_VERBATIM_POPUP": ("Popup", "verbatim"),
    "AETEXT_VERBATIM_TOPIC": ("Topic", "verbatim"),
    "AETEXT_VERBATIM_ABOUT": ("About", "verbatim"),
    "AETEXT_VERBATIM_ERROR": ("Error", "verbatim"),
}


@dataclass(frozen=True)
class MacroDefinition:
    stable_id: str
    original: str
    location: dict[str, object]


def diagnostic(
    code: str,
    message: str,
    path: str,
    line: int,
    column: int,
) -> dict[str, object]:
    return {
        "code": code,
        "severity": "error",
        "message": message,
        "path": path,
        "line": line,
        "column": column,
    }


def relative_path(path: Path, root: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(root.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()
