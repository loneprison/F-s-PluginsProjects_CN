"""Tracked review-state models, fingerprints, and catalog-mirrored persistence."""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, RootModel, StringConstraints

from .files import FileWrite, commit_files
from .models import (
    StableAsciiId,
    StableTextId,
    StrictModel,
    TranslationValue,
    UseSource,
    WorkflowDefinition,
)

Fingerprint = Annotated[str, StringConstraints(pattern=r"^sha256-v1:[0-9a-f]{64}$")]
ReviewChangeReason = Literal[
    "source-baseline-missing",
    "source-changed",
    "translation-baseline-missing",
    "translation-changed",
]


class ReviewBaseline(StrictModel):
    source: Fingerprint
    translation: Fingerprint


class ReviewStateEntry(StrictModel):
    stage: StableAsciiId
    reviewed_against: ReviewBaseline | None = Field(alias="reviewedAgainst", default=None)


class ReviewLocaleState(RootModel[dict[StableTextId, ReviewStateEntry]]):
    pass


class ReviewStateDocument(StrictModel):
    schema_version: Literal[1] = Field(alias="schemaVersion")
    locales: dict[StableAsciiId, ReviewLocaleState]


class EffectiveReviewState(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    persisted_stage: str | None
    effective_stage: str | None
    reasons: list[ReviewChangeReason]


def _fingerprint(domain: str, fields: tuple[str, ...]) -> str:
    payload = bytearray(b"AeText.review-fingerprint\0")
    for value in (domain, *fields):
        encoded = value.encode("utf-8")
        payload.extend(len(encoded).to_bytes(8, "big"))
        payload.extend(encoded)
    return "sha256-v1:" + sha256(payload).hexdigest()


def source_fingerprint(stable_id: str, original: str) -> str:
    return _fingerprint("source", (stable_id, original))


def translation_fingerprint(
    locale: str,
    stable_id: str,
    value: TranslationValue,
) -> str:
    if isinstance(value, str):
        fields = (locale, stable_id, "string", value)
    elif isinstance(value, UseSource):
        fields = (locale, stable_id, "useSource")
    else:
        raise ValueError("incomplete translation cannot have a review fingerprint")
    return _fingerprint("translation", fields)


def effective_review_state(
    entry: ReviewStateEntry | None,
    workflow: WorkflowDefinition,
    current_source: str,
    current_translation: str | None,
) -> EffectiveReviewState:
    if entry is None:
        return EffectiveReviewState(
            persisted_stage=None,
            effective_stage=None,
            reasons=[],
        )
    if entry.stage != workflow.completed_stage_id:
        return EffectiveReviewState(
            persisted_stage=entry.stage,
            effective_stage=entry.stage,
            reasons=[],
        )

    baseline = entry.reviewed_against
    reasons: list[ReviewChangeReason] = []
    if baseline is None:
        reasons.extend(["source-baseline-missing", "translation-baseline-missing"])
    else:
        if baseline.source != current_source:
            reasons.append("source-changed")
        if current_translation is None or baseline.translation != current_translation:
            reasons.append("translation-changed")
    if not reasons:
        effective_stage = entry.stage
    elif any(reason.startswith("translation-") for reason in reasons):
        effective_stage = workflow.defaults.manual_edit
    else:
        effective_stage = workflow.source_change.get(entry.stage)
    if reasons and effective_stage == workflow.completed_stage_id:
        effective_stage = None
    return EffectiveReviewState(
        persisted_stage=entry.stage,
        effective_stage=effective_stage,
        reasons=reasons,
    )


class ReviewStateConflictError(RuntimeError):
    """Raised when tracked review-state changed after a page was opened."""


class ReviewStateSnapshot(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    path: Path
    sha256: str | None
    document: ReviewStateDocument


def _format_review_state(document: ReviewStateDocument) -> bytes:
    value = document.model_dump(by_alias=True, exclude_none=True)
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


class ReviewStateRepository:
    def __init__(self, repository_root: str | Path) -> None:
        self.repository_root = Path(repository_root).resolve()
        self.catalog_root = (self.repository_root / "_localization" / "catalog").resolve()
        self.state_root = (self.repository_root / "_localization" / "review-state").resolve()

    @staticmethod
    def _hash(data: bytes) -> str:
        return sha256(data).hexdigest().upper()

    def path_for_catalog(self, catalog_path: str | Path) -> Path:
        catalog = Path(catalog_path).resolve()
        if not catalog.is_relative_to(self.catalog_root):
            raise ValueError(f"catalog path escaped repository catalog root: {catalog}")
        return self.state_root / catalog.relative_to(self.catalog_root)

    def load_for_catalog(self, catalog_path: str | Path) -> ReviewStateSnapshot:
        path = self.path_for_catalog(catalog_path)
        if not path.is_file():
            return ReviewStateSnapshot(
                path=path,
                sha256=None,
                document=ReviewStateDocument(schemaVersion=1, locales={}),
            )
        data = path.read_bytes()
        document = json.loads(data.decode("utf-8-sig"))
        validated = ReviewStateDocument.model_validate(document, strict=True)
        return ReviewStateSnapshot(path=path, sha256=self._hash(data), document=validated)

    def assert_current(self, snapshot: ReviewStateSnapshot) -> None:
        path = snapshot.path.resolve()
        if not path.is_relative_to(self.state_root):
            raise ValueError(f"review-state path escaped repository root: {path}")
        current_hash = self._hash(path.read_bytes()) if path.is_file() else None
        if current_hash != snapshot.sha256:
            raise ReviewStateConflictError(f"review-state changed after review opened: {path}")

    def prepare_locale(
        self,
        snapshot: ReviewStateSnapshot,
        locale: str,
        entries: dict[str, ReviewStateEntry],
    ) -> tuple[ReviewStateSnapshot, FileWrite]:
        self.assert_current(snapshot)
        locales = {key: dict(value.root) for key, value in snapshot.document.locales.items()}
        if entries:
            locales[locale] = dict(entries)
        else:
            locales.pop(locale, None)
        document = ReviewStateDocument(schemaVersion=1, locales=locales)
        output = _format_review_state(document)
        saved = ReviewStateSnapshot(
            path=snapshot.path,
            sha256=self._hash(output),
            document=document,
        )
        return saved, FileWrite(snapshot.path, snapshot.sha256, output, ReviewStateConflictError)

    def save_locale(
        self,
        snapshot: ReviewStateSnapshot,
        locale: str,
        entries: dict[str, ReviewStateEntry],
    ) -> ReviewStateSnapshot:
        saved, write = self.prepare_locale(snapshot, locale, entries)
        catalog_path = self.catalog_root / snapshot.path.relative_to(self.state_root)
        commit_files(catalog_path, [write])
        return saved
