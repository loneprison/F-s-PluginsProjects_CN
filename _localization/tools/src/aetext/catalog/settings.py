"""Validated Settings catalog access for the shared review workspace."""

from __future__ import annotations

import json
from collections.abc import Mapping
from hashlib import sha256
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from .files import FileWrite
from .formatting import format_catalog_json
from .models import StableTextId, StrictModel, UseSource
from .repository import CatalogConflictError
from .validation import placeholders

SETTINGS_TRANSLATION_LOCALES = ("en", "ja")
NonEmptyText = Annotated[str, StringConstraints(min_length=1)]
SettingsToken = Annotated[str, StringConstraints(pattern=r"^[A-Z][A-Za-z0-9]*$")]


class SettingsEntry(StrictModel):
    id: StableTextId
    token: SettingsToken
    zh: NonEmptyText
    en: NonEmptyText | UseSource | None = None
    ja: NonEmptyText | UseSource | None = None


class SettingsCatalog(StrictModel):
    entries: list[SettingsEntry] = Field(min_length=1)
    references: list[StableTextId] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_identity_and_references(self) -> SettingsCatalog:
        ids = [entry.id for entry in self.entries]
        tokens = [entry.token for entry in self.entries]
        if len(ids) != len(set(ids)):
            raise ValueError("Settings stable text IDs must be unique")
        if len(tokens) != len(set(tokens)):
            raise ValueError("Settings C++ tokens must be unique")
        if len(self.references) != len(set(self.references)):
            raise ValueError("Settings references must be unique")
        if set(self.references) != set(ids):
            raise ValueError("Settings references must exactly cover catalog entries")
        return self

    def with_locale(
        self,
        locale: str,
        values: Mapping[str, str | UseSource | None],
    ) -> SettingsCatalog:
        if locale not in SETTINGS_TRANSLATION_LOCALES:
            raise ValueError(f"unsupported Settings translation locale: {locale}")
        expected = {entry.id for entry in self.entries}
        if set(values) != expected:
            raise ValueError("Settings translations must exactly cover catalog entries")
        entries = []
        for entry in self.entries:
            value = values[entry.id]
            update = {locale: value}
            entries.append(entry.model_copy(update=update))
        return SettingsCatalog.model_validate(
            self.model_copy(update={"entries": entries}).model_dump(
                by_alias=True,
                exclude_none=True,
            ),
            strict=True,
        )


class SettingsCatalogSnapshot(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    path: Path
    sha256: str
    catalog: SettingsCatalog


def validate_settings_catalog(
    catalog: SettingsCatalog,
    locale: str | None = None,
    *,
    publication: bool = False,
) -> list[dict[str, object]]:
    locales = SETTINGS_TRANSLATION_LOCALES if locale is None else (locale,)
    diagnostics: list[dict[str, object]] = []
    for selected in locales:
        if selected not in SETTINGS_TRANSLATION_LOCALES:
            raise ValueError(f"unsupported Settings translation locale: {selected}")
        for entry in catalog.entries:
            value = getattr(entry, selected)
            if value is None:
                diagnostics.append(
                    {
                        "code": "AET3001",
                        "severity": "error" if publication else "warning",
                        "message": f"missing translation: locale={selected} id={entry.id}",
                        "locale": selected,
                        "stableId": entry.id,
                    }
                )
                continue
            translated = entry.zh if isinstance(value, UseSource) else value
            if placeholders(entry.zh) == placeholders(translated):
                continue
            diagnostics.append(
                {
                    "code": "AET3030",
                    "severity": "error",
                    "message": f"placeholder mismatch: locale={selected} id={entry.id}",
                    "locale": selected,
                    "stableId": entry.id,
                }
            )
    return diagnostics


def _format_settings_catalog(catalog: SettingsCatalog, *, newline: str = "\n") -> bytes:
    document = catalog.model_dump(by_alias=True, exclude_none=True)
    output = format_catalog_json(document)
    return output.replace("\n", newline).encode("utf-8")


class SettingsCatalogRepository:
    def __init__(self, repository_root: str | Path) -> None:
        self.repository_root = Path(repository_root).resolve()
        self.catalog_root = (self.repository_root / "_localization" / "catalog").resolve()

    @staticmethod
    def _hash(data: bytes) -> str:
        return sha256(data).hexdigest().upper()

    def _catalog_path(self, path: str | Path) -> Path:
        candidate = Path(path).resolve()
        if not candidate.is_relative_to(self.catalog_root):
            raise ValueError(f"catalog path escaped repository catalog root: {candidate}")
        return candidate

    def load(self, path: str | Path) -> SettingsCatalogSnapshot:
        catalog_path = self._catalog_path(path)
        data = catalog_path.read_bytes()
        document = json.loads(data.decode("utf-8-sig"))
        catalog = SettingsCatalog.model_validate(document, strict=True)
        return SettingsCatalogSnapshot(
            path=catalog_path,
            sha256=self._hash(data),
            catalog=catalog,
        )

    def prepare(self, snapshot: SettingsCatalogSnapshot, catalog: SettingsCatalog) -> FileWrite:
        path = self._catalog_path(snapshot.path)
        current_data = path.read_bytes()
        newline = "\r\n" if b"\r\n" in current_data else "\n"
        return FileWrite(
            path,
            snapshot.sha256,
            _format_settings_catalog(catalog, newline=newline),
            CatalogConflictError,
        )
