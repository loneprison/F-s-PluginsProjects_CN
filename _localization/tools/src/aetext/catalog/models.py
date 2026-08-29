"""Strict Pydantic models for every JSON document shared by AeText tools."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, RootModel, StringConstraints, model_validator

StableAsciiId = Annotated[str, StringConstraints(min_length=1, pattern=r"^[\x21-\x7E]+$")]
StableTextId = Annotated[
    str,
    StringConstraints(pattern=r"^L10N_[A-Z0-9]+(?:_[A-Z0-9]+)*$"),
]
EncodingProfile = Literal[
    "windows-1252",
    "windows-932",
    "windows-936",
    "windows-936-ae-display",
    "utf-8",
]
TextRole = Literal["Param", "Label", "Popup", "Topic", "About", "Error"]
Disposition = Literal["translated", "verbatim"]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class SourceTextSource(StrictModel):
    kind: Literal["source"]


class TranslationTextSource(StrictModel):
    kind: Literal["translation"]
    locale: StableAsciiId


TextSource = Annotated[
    SourceTextSource | TranslationTextSource,
    Field(discriminator="kind"),
]


class VariantDefinition(StrictModel):
    id: StableAsciiId
    text_source: TextSource = Field(alias="textSource")
    encoding_profile: EncodingProfile = Field(alias="encodingProfile")


class FamilyDefinition(StrictModel):
    schema_version: Literal[1] = Field(alias="schemaVersion")
    family_id: StableAsciiId = Field(alias="familyId")
    source_variant_id: StableAsciiId = Field(alias="sourceVariantId")
    variants: list[VariantDefinition] = Field(min_length=1)

    def translation_locales(self) -> list[str]:
        result: list[str] = []
        for variant in self.variants:
            source = variant.text_source
            if isinstance(source, TranslationTextSource) and source.locale not in result:
                result.append(source.locale)
        return result


class UseSource(StrictModel):
    use_source: Literal[True] = Field(alias="useSource")


TranslationValue = str | UseSource | None
TranslationSections = dict[TextRole, dict[StableTextId, TranslationValue]]
WorkflowSections = dict[TextRole, dict[StableTextId, StableAsciiId]]


class WorkflowStateMap(RootModel[dict[StableAsciiId, WorkflowSections]]):
    pass


class EffectCatalog(StrictModel):
    schema_version: Literal[1] = Field(alias="schemaVersion")
    translations: dict[StableAsciiId, TranslationSections]
    workflow: WorkflowStateMap | None = None

    @staticmethod
    def _flatten_sections(sections: dict[str, dict[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for role_map in sections.values():
            for stable_id, value in role_map.items():
                if stable_id in result:
                    raise ValueError(f"stable ID appears in multiple Role sections: {stable_id}")
                result[stable_id] = value
        return result

    @model_validator(mode="after")
    def validate_unique_role_placement(self) -> EffectCatalog:
        for sections in self.translations.values():
            self._flatten_sections(sections)
        if self.workflow is not None:
            for sections in self.workflow.root.values():
                self._flatten_sections(sections)
        return self

    def flatten_locale(self, locale: str) -> dict[str, TranslationValue]:
        return self._flatten_sections(self.translations[locale])  # type: ignore[return-value]

    def flatten_workflow(self, locale: str) -> dict[str, str]:
        if self.workflow is None or locale not in self.workflow.root:
            return {}
        return self._flatten_sections(self.workflow.root[locale])  # type: ignore[return-value]


class WorkflowStage(StrictModel):
    id: StableAsciiId
    label: Annotated[str, StringConstraints(min_length=1)]
    color: StableAsciiId
    enabled: bool = True


class WorkflowDefaults(StrictModel):
    manual_edit: StableAsciiId | None = Field(alias="manualEdit", default=None)
    pretranslation: StableAsciiId | None = None


class WorkflowDefinition(StrictModel):
    schema_version: Literal[1] = Field(alias="schemaVersion")
    enabled: bool
    stages: list[WorkflowStage] = Field(min_length=1)
    completed_stage_id: StableAsciiId = Field(alias="completedStageId")
    defaults: WorkflowDefaults
    source_change: dict[StableAsciiId, StableAsciiId] = Field(alias="sourceChange")

    @model_validator(mode="after")
    def validate_stage_references(self) -> WorkflowDefinition:
        stage_ids = [stage.id for stage in self.stages]
        if len(stage_ids) != len(set(stage_ids)):
            raise ValueError("workflow stage IDs must be unique")
        known = set(stage_ids)
        references = [
            self.completed_stage_id,
            self.defaults.manual_edit,
            self.defaults.pretranslation,
            *self.source_change.keys(),
            *self.source_change.values(),
        ]
        unknown = sorted({value for value in references if value is not None} - known)
        if unknown:
            raise ValueError(f"workflow references unknown stages: {', '.join(unknown)}")
        return self


class SourceLocation(StrictModel):
    path: str
    line: int = Field(ge=1)
    column: int = Field(ge=1)


class BindingRecord(StrictModel):
    role: TextRole
    stable_id: StableTextId = Field(alias="stableId")
    disposition: Disposition
    index: int = Field(ge=0)
    original: str | None = None
    definition: SourceLocation | None = None
    uses: list[SourceLocation] = Field(default_factory=list)
