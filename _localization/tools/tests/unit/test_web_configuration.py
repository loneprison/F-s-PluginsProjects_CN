from __future__ import annotations

from aetext.catalog.models import WorkflowDefinition
from aetext.catalog.review import ReviewRow
from aetext.web.app import ReviewRun
from aetext.web.translation_grid import (
    community_stage_filter,
    community_text_filter,
    grid_options_for_section,
    section_summary,
)


def test_review_run_is_loopback_with_token_path() -> None:
    run = ReviewRun(host="127.0.0.1", port=8123, token="secret-token")

    assert run.path == "/secret-token"
    assert run.url == "http://127.0.0.1:8123/secret-token"


def test_grid_uses_only_expected_editable_fields() -> None:
    class Session:
        def __init__(self) -> None:
            self.rows: list[object] = []
            self.workflow = WorkflowDefinition.model_validate(
                {
                    "schemaVersion": 1,
                    "enabled": True,
                    "stages": [
                        {
                            "id": "reviewed",
                            "label": "已校对",
                            "color": "green",
                            "enabled": True,
                        }
                    ],
                    "completedStageId": "reviewed",
                    "defaults": {"manualEdit": "reviewed", "pretranslation": None},
                    "sourceChange": {},
                },
                strict=True,
            )

    options = grid_options_for_section(Session(), "Param")
    editable = {
        column["field"] for column in options["columnDefs"] if column.get("editable") is True
    }

    assert editable == {"use_source"}


def test_grid_hides_workflow_column_when_disabled_and_labels_disabled_stage() -> None:
    class Session:
        def __init__(self) -> None:
            self.rows: list[object] = []
            self.workflow = WorkflowDefinition.model_validate(
                {
                    "schemaVersion": 1,
                    "enabled": False,
                    "stages": [
                        {
                            "id": "retired",
                            "label": "旧阶段",
                            "color": "grey",
                            "enabled": False,
                        }
                    ],
                    "completedStageId": "retired",
                    "defaults": {"manualEdit": None, "pretranslation": None},
                    "sourceChange": {},
                },
                strict=True,
            )

    disabled = grid_options_for_section(Session(), "Param")
    assert "workflow_stage" not in {column["field"] for column in disabled["columnDefs"]}

    session = Session()
    session.workflow = session.workflow.model_copy(update={"enabled": True})
    enabled = grid_options_for_section(session, "Param")
    workflow = next(
        column for column in enabled["columnDefs"] if column["field"] == "workflow_stage"
    )
    assert "已停用：旧阶段" in workflow[":cellRenderer"]  # noqa: RUF001
    assert "<select>" not in workflow[":cellRenderer"]


def test_status_chips_use_community_text_filter_models() -> None:
    assert community_text_filter([]) is None
    assert community_text_filter(["有效"]) == {
        "filterType": "text",
        "type": "equals",
        "filter": "有效",
    }
    assert community_text_filter(["有效", "错误"]) == {
        "filterType": "text",
        "operator": "OR",
        "conditions": [
            {"filterType": "text", "type": "equals", "filter": "有效"},
            {"filterType": "text", "type": "equals", "filter": "错误"},
        ],
    }
    assert community_stage_filter({""}) == {"filterType": "text", "type": "blank"}
    assert community_stage_filter({"", "reviewed"}) == {
        "filterType": "text",
        "operator": "OR",
        "conditions": [
            {"filterType": "text", "type": "blank"},
            {"filterType": "text", "type": "equals", "filter": "reviewed"},
        ],
    }


def test_role_grid_exposes_ae_order_and_multiple_role_badges() -> None:
    class Session:
        def __init__(self) -> None:
            self.rows = [
                ReviewRow(
                    content_status="valid",
                    workflow_stage=None,
                    original="Value",
                    translation="值",
                    use_source=False,
                    primary_role="Param",
                    roles=["Param", "Label"],
                    panel_order=0,
                    stable_id="L10N_VALUE",
                    definition_path="Fixture.cpp",
                    definition_line=1,
                    use_count=2,
                )
            ]
            self.workflow = WorkflowDefinition.model_validate(
                {
                    "schemaVersion": 1,
                    "enabled": False,
                    "stages": [
                        {
                            "id": "reviewed",
                            "label": "已校对",
                            "color": "green",
                            "enabled": True,
                        }
                    ],
                    "completedStageId": "reviewed",
                    "defaults": {"manualEdit": None, "pretranslation": None},
                    "sourceChange": {},
                },
                strict=True,
            )

    session = Session()
    options = grid_options_for_section(session, "Param")
    fields = [column["field"] for column in options["columnDefs"]]

    assert fields[0] == "panel_order_display"
    assert options["columnDefs"][0]["pinned"] == "left"
    original = next(column for column in options["columnDefs"] if column["field"] == "original")
    translation = next(
        column for column in options["columnDefs"] if column["field"] == "translation"
    )
    assert original["pinned"] == "left"
    assert "已复制原文" in original[":cellRenderer"]
    assert "aetext-translation-input" in translation[":cellRenderer"]
    assert "popupEditRequested" in translation[":cellRenderer"]
    assert fields.index("roles_label") < fields.index("stable_id")
    assert options["rowData"][0]["panel_order_display"] == 1
    assert options["rowData"][0]["roles_label"] == "参数名称 · 控件文字"
    assert grid_options_for_section(session, "Label")["rowData"] == []
    assert section_summary(session, "Param") == "1 / 1"
