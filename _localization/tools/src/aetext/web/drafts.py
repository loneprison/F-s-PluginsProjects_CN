"""Keep unsaved row values separate from the source and saved review baseline."""

from __future__ import annotations

from dataclasses import dataclass

from ..catalog.review import ReviewContextChangedError, ReviewRow, ReviewSession
from ..catalog.saving import workflow_semantics

DRAFT_FIELDS = ("translation", "use_source", "workflow_stage", "workflow_stage_explicit")


@dataclass(frozen=True)
class LocaleDraft:
    base_session: ReviewSession
    rows: list[dict[str, object]]


class DraftConflictError(ValueError):
    """A draft field was also changed on disk after editing began."""


def _values(row: ReviewRow | dict[str, object]) -> dict[str, object]:
    if isinstance(row, ReviewRow):
        return {field: getattr(row, field) for field in DRAFT_FIELDS}
    return {field: row.get(field) for field in DRAFT_FIELDS}


def draft_changes(draft: LocaleDraft) -> dict[str, dict[str, object]]:
    base = {row.stable_id: _values(row) for row in draft.base_session.rows}
    changes = {}
    for row in draft.rows:
        stable_id = str(row["stable_id"])
        values = _values(row)
        changed = {
            field: value
            for field, value in values.items()
            if base.get(stable_id, {}).get(field) != value
        }
        if changed:
            changes[stable_id] = changed
    return changes


def apply_draft(session: ReviewSession, draft: LocaleDraft) -> ReviewSession:
    if {row.stable_id: row.original for row in session.rows} != {
        row.stable_id: row.original for row in draft.base_session.rows
    } or workflow_semantics(session.workflow) != workflow_semantics(draft.base_session.workflow):
        raise ReviewContextChangedError("draft confirmation belongs to an older source or workflow")
    return _merge(session, draft, reset_review=False)


def rebase_draft(session: ReviewSession, draft: LocaleDraft) -> LocaleDraft:
    merged = _merge(session, draft, reset_review=True)
    return LocaleDraft(session, [row.model_dump() for row in merged.rows])


def _merge(session: ReviewSession, draft: LocaleDraft, *, reset_review: bool) -> ReviewSession:
    changes = draft_changes(draft)
    available = {row.stable_id: row for row in session.rows}
    base = {row.stable_id: row for row in draft.base_session.rows}
    missing = sorted(set(changes) - set(available))
    if missing:
        raise DraftConflictError(f"draft source IDs are no longer available: {missing}")
    workflow_changed = workflow_semantics(session.workflow) != workflow_semantics(
        draft.base_session.workflow
    )
    for stable_id, fields in changes.items():
        reset = reset_review and (
            workflow_changed or available[stable_id].original != base[stable_id].original
        )
        if reset:
            fields.pop("workflow_stage", None)
            fields.pop("workflow_stage_explicit", None)
        for field, value in fields.items():
            if getattr(available[stable_id], field) not in (getattr(base[stable_id], field), value):
                raise DraftConflictError(f"draft field also changed on disk: {stable_id}.{field}")
        if reset and fields and session.workflow.enabled:
            fields["workflow_stage"] = session.workflow.defaults.manual_edit
            fields["workflow_stage_explicit"] = False
    return session.model_copy(
        update={
            "rows": [row.model_copy(update=changes.get(row.stable_id, {})) for row in session.rows]
        }
    )
