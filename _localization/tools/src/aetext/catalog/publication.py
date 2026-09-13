"""Publication review validation shared by the Web preview and build gate."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from .models import (
    BindingRecord,
    EffectCatalog,
    FamilyDefinition,
    TranslationValue,
    WorkflowDefinition,
)
from .review_state import (
    ReviewStateDocument,
    effective_review_state,
    source_fingerprint,
    translation_fingerprint,
)
from .settings import SETTINGS_TRANSLATION_LOCALES, SettingsCatalog, validate_settings_catalog
from .source_index import ReviewLayout
from .validation import validate_catalog_domain


class PublicationReviewIssue(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    code: str
    message: str
    locale: str | None = None
    stable_id: str | None = None
    arguments: dict[str, object] = Field(default_factory=dict)


class PublicationReviewReport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    total: int
    completed: int
    issues: list[PublicationReviewIssue]

    @property
    def valid(self) -> bool:
        return not self.issues and self.completed == self.total


def _issue(
    code: str,
    message: str,
    *,
    locale: str | None = None,
    stable_id: str | None = None,
    arguments: dict[str, object] | None = None,
) -> PublicationReviewIssue:
    return PublicationReviewIssue(
        code=code,
        message=message,
        locale=locale,
        stable_id=stable_id,
        arguments={} if arguments is None else arguments,
    )


def validate_publication_review(
    catalog: EffectCatalog,
    family: FamilyDefinition,
    bindings: list[BindingRecord],
    review_layout: ReviewLayout,
    workflow: WorkflowDefinition,
    review_state: ReviewStateDocument,
) -> PublicationReviewReport:
    issues: list[PublicationReviewIssue] = []
    for diagnostic in validate_catalog_domain(
        catalog,
        family,
        bindings,
        review_layout,
        publication=True,
    ):
        if diagnostic["severity"] != "error":
            continue
        issues.append(
            _issue(
                diagnostic["code"],
                diagnostic["message"],
                locale=diagnostic.get("locale"),
                stable_id=diagnostic.get("stableId"),
                arguments=diagnostic.get("arguments", {}),
            )
        )

    originals = {
        binding.stable_id: binding.original
        for binding in bindings
        if binding.disposition == "translated"
    }
    return _validate_review_evidence(
        {
            locale: catalog.flatten_locale(locale) if locale in catalog.translations else {}
            for locale in family.translation_locales()
        },
        {stable_id: originals[stable_id] for stable_id in review_layout.stable_ids()},
        workflow,
        review_state,
        issues,
    )


def validate_settings_publication_review(
    catalog: SettingsCatalog,
    workflow: WorkflowDefinition,
    review_state: ReviewStateDocument,
) -> PublicationReviewReport:
    issues = [
        _issue(
            diagnostic["code"],
            diagnostic["message"],
            locale=diagnostic.get("locale"),
            stable_id=diagnostic.get("stableId"),
        )
        for diagnostic in validate_settings_catalog(catalog, publication=True)
    ]
    return _validate_review_evidence(
        {
            locale: {entry.id: getattr(entry, locale) for entry in catalog.entries}
            for locale in SETTINGS_TRANSLATION_LOCALES
        },
        {entry.id: entry.zh for entry in catalog.entries},
        workflow,
        review_state,
        issues,
    )


def _validate_review_evidence(
    translations: dict[str, dict[str, TranslationValue]],
    originals: dict[str, str],
    workflow: WorkflowDefinition,
    review_state: ReviewStateDocument,
    issues: list[PublicationReviewIssue],
) -> PublicationReviewReport:
    required_locales = set(translations)
    required_ids = set(originals)
    known_stages = {stage.id for stage in workflow.stages}
    for locale in sorted(set(review_state.locales) - required_locales):
        issues.append(_issue("AETR101", "review-state contains an unknown locale", locale=locale))
    for locale, locale_state in review_state.locales.items():
        for stable_id, entry in locale_state.root.items():
            if locale in required_locales and stable_id not in required_ids:
                issues.append(
                    _issue(
                        "AETR102",
                        "review-state contains a Stable ID outside the current source layout",
                        locale=locale,
                        stable_id=stable_id,
                    )
                )
            if entry.stage not in known_stages:
                issues.append(
                    _issue(
                        "AETR103",
                        f"review-state references unknown stage: {entry.stage}",
                        locale=locale,
                        stable_id=stable_id,
                        arguments={"stage": entry.stage},
                    )
                )
            if entry.stage != workflow.completed_stage_id and entry.reviewed_against is not None:
                issues.append(
                    _issue(
                        "AETR104",
                        "non-completed review stage must not store a completed baseline",
                        locale=locale,
                        stable_id=stable_id,
                    )
                )

    completed = 0
    for locale, locale_values in translations.items():
        locale_state = review_state.locales.get(locale)
        state_entries = {} if locale_state is None else locale_state.root
        for stable_id in originals:
            entry = state_entries.get(stable_id)
            if entry is None:
                issues.append(
                    _issue(
                        "AETR201",
                        "publication review record is missing",
                        locale=locale,
                        stable_id=stable_id,
                    )
                )
                continue
            if entry.stage != workflow.completed_stage_id:
                issues.append(
                    _issue(
                        "AETR202",
                        f"review stage is not completed: {entry.stage}",
                        locale=locale,
                        stable_id=stable_id,
                        arguments={"stage": entry.stage},
                    )
                )
                continue
            value = locale_values.get(stable_id)
            translation_hash = (
                None if value is None else translation_fingerprint(locale, stable_id, value)
            )
            effective = effective_review_state(
                entry,
                workflow,
                source_fingerprint(stable_id, originals[stable_id]),
                translation_hash,
            )
            if effective.effective_stage != workflow.completed_stage_id:
                issues.append(
                    _issue(
                        "AETR203",
                        "completed review baseline is no longer effective: "
                        + ", ".join(effective.reasons),
                        locale=locale,
                        stable_id=stable_id,
                        arguments={"reasons": ", ".join(effective.reasons)},
                    )
                )
                continue
            completed += 1
    return PublicationReviewReport(
        total=len(translations) * len(originals),
        completed=completed,
        issues=issues,
    )
