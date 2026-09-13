"""Ignored, review-only source snapshots written by explicit scan actions."""

from __future__ import annotations

import json
import os
import tempfile
from collections.abc import Mapping
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import TYPE_CHECKING, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from .models import BindingRecord, StableTextId, TextRole

if TYPE_CHECKING:
    from ..build import ProjectManifest

_Value = TypeVar("_Value")


class ReviewUse(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    role: TextRole
    stable_id: StableTextId = Field(alias="stableId")
    disposition: Literal["translated", "verbatim"]
    input_ordinal: int = Field(alias="inputOrdinal", ge=0)
    call_ordinal: int = Field(alias="callOrdinal", ge=0)
    function_name: str | None = Field(alias="functionName")
    path: str
    line: int = Field(ge=1)
    column: int = Field(ge=1)


class ReviewEntry(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    stable_id: StableTextId = Field(alias="stableId")
    primary_role: TextRole = Field(alias="primaryRole")
    roles: list[TextRole] = Field(min_length=1)
    panel_order: int = Field(alias="panelOrder", ge=0)


class ReviewSection(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    role: TextRole
    entries: list[ReviewEntry] = Field(min_length=1)


class ReviewLayout(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    schema_version: Literal[1] = Field(alias="schemaVersion")
    sections: list[ReviewSection]

    def stable_ids(self) -> list[str]:
        return [entry.stable_id for section in self.sections for entry in section.entries]

    def canonicalize(self, values: Mapping[str, _Value]) -> dict[str, dict[str, _Value]]:
        expected = set(self.stable_ids())
        unknown = sorted(set(values) - expected)
        if unknown:
            raise ValueError(f"values are absent from review layout: {', '.join(unknown)}")
        result: dict[str, dict[str, _Value]] = {}
        for section in self.sections:
            role_values = {
                entry.stable_id: values[entry.stable_id]
                for entry in section.entries
                if entry.stable_id in values
            }
            if role_values:
                result[section.role] = role_values
        return result


class ProjectIndexEntry(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    name: str
    role: str
    category: str
    catalog_path: str = Field(alias="catalogPath")
    scan_state: str = Field(alias="scanState")


class ProjectIndex(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    schema_version: Literal[1] = Field(alias="schemaVersion")
    scanned_at: str | None = Field(alias="scannedAt")
    projects: list[ProjectIndexEntry]


class SourceSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)

    schema_version: Literal[1] = Field(alias="schemaVersion")
    project: str
    scanned_at: str = Field(alias="scannedAt")
    project_path: str = Field(alias="projectPath")
    role: str
    category: str
    catalog_path: str = Field(alias="catalogPath")
    family_definition_path: str = Field(alias="familyDefinitionPath")
    inputs: list[str]
    input_hashes: dict[str, str] = Field(alias="inputHashes", default_factory=dict)
    bindings: list[BindingRecord]
    review_uses: list[ReviewUse] = Field(alias="reviewUses")
    review_layout: ReviewLayout = Field(alias="reviewLayout")
    diagnostics: list[dict[str, object]]


def _timestamp() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def _atomic_json(path: Path, document: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=path.name + ".tmp.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(document, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


class ProjectIndexRepository:
    def __init__(self, repository_root: str | Path) -> None:
        self.repository_root = Path(repository_root).resolve()
        self.cache_root = (
            self.repository_root / "_localization" / ".cache" / "aetext-review"
        ).resolve()
        self.path = self.cache_root / "index.json"

    def load(self) -> ProjectIndex:
        if not self.path.is_file():
            return ProjectIndex(schemaVersion=1, scannedAt=None, projects=[])
        document = json.loads(self.path.read_text(encoding="utf-8-sig"))
        return ProjectIndex.model_validate(document, strict=True)

    def update(self, snapshot: SourceSnapshot) -> ProjectIndex:
        current = self.load()
        entries = {entry.name.casefold(): entry for entry in current.projects}
        entries[snapshot.project.casefold()] = ProjectIndexEntry(
            name=snapshot.project,
            role=snapshot.role,
            category=snapshot.category,
            catalogPath=snapshot.catalog_path,
            scanState="ready",
        )
        updated = ProjectIndex(
            schemaVersion=1,
            scannedAt=snapshot.scanned_at,
            projects=sorted(entries.values(), key=lambda entry: entry.name.casefold()),
        )
        _atomic_json(self.path, updated.model_dump(by_alias=True))
        return updated


class SourceSnapshotRepository:
    def __init__(self, repository_root: str | Path) -> None:
        self.repository_root = Path(repository_root).resolve()
        self.index = ProjectIndexRepository(self.repository_root)
        self.project_root = self.index.cache_root / "projects"

    @staticmethod
    def _safe_name(project_name: str) -> str:
        if (
            not project_name
            or project_name in {".", ".."}
            or Path(project_name).name != project_name
            or "/" in project_name
            or "\\" in project_name
        ):
            raise ValueError("project name must not be a path")
        return project_name

    def _path(self, project_name: str) -> Path:
        return self.project_root / f"{self._safe_name(project_name)}.json"

    def _stored_path(self, path: Path, *, allow_external: bool = False) -> str:
        resolved = path.resolve()
        if resolved.is_relative_to(self.repository_root):
            return resolved.relative_to(self.repository_root).as_posix()
        if allow_external:
            return resolved.as_posix()
        raise ValueError(f"source snapshot path escaped repository: {resolved}")

    def load(self, project_name: str) -> SourceSnapshot | None:
        path = self._path(project_name)
        if not path.is_file():
            return None
        document = json.loads(path.read_text(encoding="utf-8-sig"))
        if isinstance(document, dict):
            document.pop("sourceChangePending", None)
        return SourceSnapshot.model_validate(document, strict=True)

    def hash_inputs(self, paths: list[Path]) -> dict[str, str]:
        return {
            self._stored_path(path, allow_external=True): sha256(path.read_bytes()).hexdigest()
            for path in paths
        }

    def save(
        self,
        manifest: ProjectManifest,
        bindings: list[BindingRecord],
        review_uses: list[ReviewUse],
        review_layout: ReviewLayout,
        diagnostics: list[dict[str, object]],
        input_hashes: dict[str, str],
    ) -> SourceSnapshot:
        snapshot = SourceSnapshot(
            schemaVersion=1,
            project=manifest.name,
            scannedAt=_timestamp(),
            projectPath=self._stored_path(manifest.project_path),
            role=manifest.role,
            category=manifest.category,
            catalogPath=self._stored_path(manifest.catalog_path),
            familyDefinitionPath=self._stored_path(manifest.family_definition_path),
            inputs=[self._stored_path(path, allow_external=True) for path in manifest.inputs],
            inputHashes=input_hashes,
            bindings=bindings,
            reviewUses=review_uses,
            reviewLayout=review_layout,
            diagnostics=diagnostics,
        )
        _atomic_json(self._path(manifest.name), snapshot.model_dump(by_alias=True))
        self.index.update(snapshot)
        return snapshot
