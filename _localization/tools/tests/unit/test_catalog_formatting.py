from __future__ import annotations

import json

from aetext.catalog.formatting import format_catalog_json


def test_only_exact_use_source_sentinels_are_compacted() -> None:
    document = {
        "translation": {"useSource": True},
        "ordinary": {"useSource": True, "note": "keep expanded"},
    }

    formatted = format_catalog_json(document)

    assert '"translation": {"useSource": true}' in formatted
    assert '"ordinary": {\n' in formatted
    assert json.loads(formatted) == document
