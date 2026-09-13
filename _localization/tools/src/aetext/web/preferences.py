"""Ignored workspace-local preferences for the review Web UI."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from .i18n import DEFAULT_UI_LOCALE, UiLocale, normalize_ui_locale


class UiPreferencesRepository:
    def __init__(self, repository_root: str | Path) -> None:
        self.path = (
            Path(repository_root).resolve()
            / "_localization"
            / ".cache"
            / "aetext-review"
            / "preferences.json"
        )

    def load(self) -> UiLocale:
        try:
            document = json.loads(self.path.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            return DEFAULT_UI_LOCALE
        if not isinstance(document, dict) or document.get("schemaVersion") != 1:
            return DEFAULT_UI_LOCALE
        return normalize_ui_locale(document.get("uiLocale"))

    def save(self, locale: UiLocale) -> None:
        normalized = normalize_ui_locale(locale)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        output = (
            json.dumps(
                {"schemaVersion": 1, "uiLocale": normalized},
                ensure_ascii=False,
                indent=2,
            )
            + "\n"
        )
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=self.path.name + ".tmp.",
            dir=self.path.parent,
        )
        temporary = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
                stream.write(output)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.path)
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
