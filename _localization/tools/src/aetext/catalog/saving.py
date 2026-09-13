"""Interpret edited rows and construct review baselines without writing files."""

from __future__ import annotations

from .models import TranslationValue, UseSource, WorkflowDefinition
from .review_state import (
    ReviewBaseline,
    ReviewStateEntry,
    source_fingerprint,
    translation_fingerprint,
)


def workflow_semantics(workflow: WorkflowDefinition) -> tuple:
    return (
        workflow.enabled,
        workflow.completed_stage_id,
        workflow.defaults.manual_edit,
        tuple(sorted(workflow.source_change.items())),
        tuple((stage.id, stage.enabled) for stage in workflow.stages),
    )


def submitted_values(
    rows: list[dict[str, object]],
    old_values: dict[str, TranslationValue],
    base_stages: dict[str, str | None],
    workflow: WorkflowDefinition,
) -> tuple[dict[str, TranslationValue], dict[str, str | None]]:
    ids = [str(row.get("stable_id")) for row in rows]
    if len(ids) != len(set(ids)) or set(ids) != set(base_stages):
        raise ValueError("submitted rows do not exactly match the reviewed source IDs")
    known_stages = {stage.id for stage in workflow.stages}
    values: dict[str, TranslationValue] = {}
    stages: dict[str, str | None] = {}
    for row, stable_id in zip(rows, ids, strict=True):
        value = (
            UseSource(useSource=True) if row.get("use_source") is True else row.get("translation")
        )
        if value is not None and not isinstance(value, (str, UseSource)):
            raise ValueError("translation must be nonempty or use source")
        if value == "":
            raise ValueError("translation must be nonempty")
        values[stable_id] = value
        stage_value = row.get("workflow_stage")
        stage = None if stage_value in {None, ""} else str(stage_value)
        if stage is not None and stage not in known_stages:
            raise ValueError(f"unknown workflow stage: {stage}")
        explicit = row.get("workflow_stage_explicit") is True or stage != base_stages[stable_id]
        if workflow.enabled and old_values.get(stable_id) != value and not explicit:
            stage = workflow.defaults.manual_edit
        stages[stable_id] = stage
    return values, stages


def review_entries(
    values: dict[str, TranslationValue],
    stages: dict[str, str | None],
    originals: dict[str, str],
    locale: str,
    workflow: WorkflowDefinition,
) -> dict[str, ReviewStateEntry]:
    entries: dict[str, ReviewStateEntry] = {}
    for stable_id, stage in stages.items():
        if stage is None:
            continue
        baseline = None
        if stage == workflow.completed_stage_id:
            value = values[stable_id]
            if value is None:
                raise ValueError(f"completed review requires a non-null translation: {stable_id}")
            baseline = ReviewBaseline(
                source=source_fingerprint(stable_id, originals[stable_id]),
                translation=translation_fingerprint(locale, stable_id, value),
            )
        entries[stable_id] = ReviewStateEntry(stage=stage, reviewedAgainst=baseline)
    return entries
