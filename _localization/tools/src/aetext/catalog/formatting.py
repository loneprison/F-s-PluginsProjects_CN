"""Canonical human-facing JSON formatting for effect catalogs."""

from __future__ import annotations

import json
import re

_EXPANDED_USE_SOURCE = re.compile(r'\{\n *"useSource": true\n *\}')


def format_catalog_json(document: object) -> str:
    """Indent catalog structure while keeping exact useSource sentinels on one line."""

    formatted = json.dumps(document, ensure_ascii=False, indent=2)
    return _EXPANDED_USE_SOURCE.sub('{"useSource": true}', formatted) + "\n"
