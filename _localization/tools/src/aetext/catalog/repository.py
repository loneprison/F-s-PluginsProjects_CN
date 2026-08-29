"""Safe language-scoped persistence for human-maintained effect catalogs."""

from __future__ import annotations

import json
import os
import tempfile
from collections.abc import Mapping
from hashlib import sha256
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from .formatting import format_catalog_json
from .models import EffectCatalog, TranslationValue


class CatalogConflictError(RuntimeError):
    """Raised when a page attempts to overwrite a catalog changed after it was opened."""


class CatalogSnapshot(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    path: Path
    sha256: str
    catalog: EffectCatalog


class CatalogRepository:
    def __init__(self, repository_root: str | Path) -> None:
        self.repository_root = Path(repository_root).resolve()
        self.catalog_root = (self.repository_root / "_localization" / "catalog").resolve()

    def _catalog_path(self, path: str | Path) -> Path:
        candidate = Path(path).resolve()
        if not candidate.is_relative_to(self.catalog_root):
            raise ValueError(f"catalog path escaped repository catalog root: {candidate}")
        return candidate

    @staticmethod
    def _hash(data: bytes) -> str:
        return sha256(data).hexdigest().upper()

    def load(self, path: str | Path) -> CatalogSnapshot:
        catalog_path = self._catalog_path(path)
        data = catalog_path.read_bytes()
        document = json.loads(data.decode("utf-8-sig"))
        catalog = EffectCatalog.model_validate(document, strict=True)
        return CatalogSnapshot(path=catalog_path, sha256=self._hash(data), catalog=catalog)

    def save_locale(
        self,
        snapshot: CatalogSnapshot,
        locale: str,
        translations: Mapping[
            str,
            Mapping[str, TranslationValue | dict[str, object]],
        ],
        workflow_stages: Mapping[str, Mapping[str, str]] | None = None,
    ) -> CatalogSnapshot:
        catalog_path = self._catalog_path(snapshot.path)
        current_data = catalog_path.read_bytes()
        current_hash = self._hash(current_data)
        if current_hash != snapshot.sha256:
            raise CatalogConflictError(f"catalog changed after review opened: {catalog_path}")
        current_document = json.loads(current_data.decode("utf-8-sig"))
        current = EffectCatalog.model_validate(current_document, strict=True)
        document = current.model_dump(by_alias=True, exclude_none=True)
        locale_maps = document["translations"]
        if locale not in locale_maps:
            raise ValueError(f"catalog does not contain current locale: {locale}")
        locale_maps[locale] = {
            role: dict(role_values) for role, role_values in translations.items()
        }
        if workflow_stages is not None:
            workflow = document.setdefault("workflow", {})
            stages = {
                role: dict(role_values)
                for role, role_values in workflow_stages.items()
                if role_values
            }
            if stages:
                workflow[locale] = stages
            else:
                workflow.pop(locale, None)
            if not workflow:
                document.pop("workflow", None)
        validated = EffectCatalog.model_validate(document, strict=True)
        output = format_catalog_json(validated.model_dump(by_alias=True, exclude_none=True)).encode(
            "utf-8"
        )

        descriptor, temporary_name = tempfile.mkstemp(
            prefix=catalog_path.name + ".tmp.",
            dir=catalog_path.parent,
        )
        temporary = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(output)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, catalog_path)
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
        return CatalogSnapshot(
            path=catalog_path,
            sha256=self._hash(output),
            catalog=validated,
        )
