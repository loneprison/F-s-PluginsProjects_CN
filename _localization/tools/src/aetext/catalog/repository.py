"""Safe language-scoped persistence for human-maintained effect catalogs."""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from .files import FileWrite
from .formatting import format_catalog_json
from .models import EffectCatalog


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

    def prepare(self, snapshot: CatalogSnapshot, catalog: EffectCatalog) -> FileWrite:
        path = self._catalog_path(snapshot.path)
        output = format_catalog_json(catalog.model_dump(by_alias=True, exclude_none=True)).encode(
            "utf-8"
        )
        return FileWrite(path, snapshot.sha256, output, CatalogConflictError)
