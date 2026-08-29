from __future__ import annotations

import copy

import pytest
from pydantic import ValidationError

from aetext.catalog import EffectCatalog, FamilyDefinition, WorkflowDefinition

FS_FAMILY = {
    "schemaVersion": 1,
    "familyId": "fs",
    "sourceVariantId": "source",
    "variants": [
        {
            "id": "en",
            "textSource": {"kind": "translation", "locale": "en"},
            "encodingProfile": "windows-1252",
        },
        {
            "id": "source",
            "textSource": {"kind": "source"},
            "encodingProfile": "windows-932",
        },
        {
            "id": "zh",
            "textSource": {"kind": "translation", "locale": "zh"},
            "encodingProfile": "windows-936",
        },
    ],
}


def test_family_model_preserves_aliases_and_locale_order() -> None:
    model = FamilyDefinition.model_validate(FS_FAMILY, strict=True)

    assert model.translation_locales() == ["en", "zh"]
    assert model.model_dump(by_alias=True) == FS_FAMILY


def test_effect_catalog_round_trips_language_first_shape() -> None:
    document = {
        "schemaVersion": 1,
        "translations": {
            "en": {"Param": {"L10N_VALUE": {"useSource": True}}},
            "zh": {"Param": {"L10N_VALUE": "值"}},
        },
    }

    model = EffectCatalog.model_validate(document, strict=True)

    assert model.model_dump(by_alias=True, exclude_none=True) == document


def test_effect_catalog_accepts_optional_language_first_workflow() -> None:
    document = {
        "schemaVersion": 1,
        "translations": {
            "en": {"Param": {"L10N_VALUE": {"useSource": True}}},
            "zh": {"Param": {"L10N_VALUE": "值"}},
        },
        "workflow": {"zh": {"Param": {"L10N_VALUE": "reviewed"}}},
    }

    model = EffectCatalog.model_validate(document, strict=True)

    assert model.model_dump(by_alias=True, exclude_none=True) == document


def test_workflow_definition_is_data_driven_and_rejects_unknown_references() -> None:
    document = {
        "schemaVersion": 1,
        "enabled": True,
        "stages": [
            {"id": "draft", "label": "草稿", "color": "gray", "enabled": True},
            {"id": "reviewed", "label": "已校对", "color": "green", "enabled": True},
        ],
        "completedStageId": "reviewed",
        "defaults": {"manualEdit": "draft", "pretranslation": None},
        "sourceChange": {"reviewed": "draft"},
    }
    model = WorkflowDefinition.model_validate(document, strict=True)
    assert model.model_dump(by_alias=True) == document

    invalid = copy.deepcopy(document)
    invalid["defaults"]["manualEdit"] = "missing"
    with pytest.raises(ValidationError):
        WorkflowDefinition.model_validate(invalid, strict=True)

    invalid = copy.deepcopy(document)
    invalid["completedStageId"] = "missing"
    with pytest.raises(ValidationError):
        WorkflowDefinition.model_validate(invalid, strict=True)


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: value.update({"original": "Value"}),
        lambda value: value["translations"]["en"]["Param"]["L10N_VALUE"].update({"extra": True}),
        lambda value: value["translations"].update({"": {}}),
    ],
)
def test_effect_catalog_rejects_non_contract_structure(mutation) -> None:
    document = {
        "schemaVersion": 1,
        "translations": {
            "en": {"Param": {"L10N_VALUE": {"useSource": True}}},
            "zh": {"Param": {"L10N_VALUE": "值"}},
        },
    }
    invalid = copy.deepcopy(document)
    mutation(invalid)

    with pytest.raises(ValidationError):
        EffectCatalog.model_validate(invalid, strict=True)
