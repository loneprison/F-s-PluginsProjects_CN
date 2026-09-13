"""Strict Pydantic models for every JSON document shared by AeText tools."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

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

    @model_validator(mode="after")
    def validate_variant_references(self) -> FamilyDefinition:
        variants = {variant.id: variant for variant in self.variants}
        if len(variants) != len(self.variants):
            raise ValueError("Variant IDs must be unique")
        source = variants.get(self.source_variant_id)
        if source is None or not isinstance(source.text_source, SourceTextSource):
            raise ValueError("sourceVariantId must name a source Variant")
        return self

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


class EffectCatalog(StrictModel):
    schema_version: Literal[1] = Field(alias="schemaVersion")
    translations: dict[StableAsciiId, TranslationSections]

    @model_validator(mode="after")
    def validate_unique_role_placement(self) -> EffectCatalog:
        for sections in self.translations.values():
            seen: set[str] = set()
            for role_map in sections.values():
                for stable_id in role_map:
                    if stable_id in seen:
                        raise ValueError(
                            f"stable ID appears in multiple Role sections: {stable_id}"
                        )
                    seen.add(stable_id)
        return self

    def flatten_locale(self, locale: str) -> dict[str, TranslationValue]:
        return {
            stable_id: value
            for role_map in self.translations[locale].values()
            for stable_id, value in role_map.items()
        }


class WorkflowStage(StrictModel):
    id: StableAsciiId
    labels: dict[
        StableAsciiId,
        Annotated[str, StringConstraints(min_length=1)],
    ]
    color: StableAsciiId
    enabled: bool = True

    @model_validator(mode="after")
    def validate_english_label(self) -> WorkflowStage:
        if "en" not in self.labels:
            raise ValueError("workflow stage labels must include English")
        return self


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
    original: str
    definition: SourceLocation | None = None
    uses: list[SourceLocation] = Field(default_factory=list)
