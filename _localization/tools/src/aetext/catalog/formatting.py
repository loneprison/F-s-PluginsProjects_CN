"""Canonical human-facing JSON formatting for effect catalogs."""

from __future__ import annotations

import json
import re

_EXPANDED_USE_SOURCE = re.compile(r'\{\n(?P<inner> *)"useSource": true\n(?P<outer> *)\}')


def format_catalog_json(document: object) -> str:
    """Indent catalog structure while keeping exact useSource sentinels on one line."""

    formatted = json.dumps(document, ensure_ascii=False, indent=2)

    def compact(match: re.Match[str]) -> str:
        if match.group("inner") != match.group("outer") + "  ":
            return match.group(0)
        return '{"useSource": true}'

    return _EXPANDED_USE_SOURCE.sub(compact, formatted) + "\n"
