from __future__ import annotations

from pathlib import Path

from aetext.catalog.models import WorkflowDefinition
from aetext.catalog.review import ReviewProgress, ReviewProject, ReviewWorkspace
from aetext.web.project_tree import project_name_from_node, project_tree_nodes


def _workflow() -> WorkflowDefinition:
    return WorkflowDefinition.model_validate(
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


def _project(
    name: str,
    role: str,
    role_label: str,
    category: str,
    *,
    deferred: bool = False,
) -> ReviewProject:
    return ReviewProject(
        name=name,
        role=role,
        role_label=role_label,
        category=category,
        category_label=category,
        catalog_path=Path(f"{name}.json"),
        locales=["en", "zh"],
        catalog_kind="source-derived",
        scan_state="ready",
        deferred=deferred,
        progress={
            "en": ReviewProgress(
                total=2,
                valid=1,
                missing=1,
                use_source=0,
                errors=0,
                reviewed=0,
                pending_review=1,
            ),
            "zh": ReviewProgress(
                total=2,
                valid=2,
                missing=0,
                use_source=0,
                errors=0,
                reviewed=2,
                pending_review=0,
            ),
        },
    )


def test_project_tree_preserves_role_category_and_language_progress() -> None:
    workspace = ReviewWorkspace(
        projects=[
            _project("AlphaFix", "Production", "正式插件", "Channel"),
            _project("MaxBlur", "Production", "正式插件", "Filter"),
            _project("PluginSkeleton", "Templates", "模板", ""),
        ],
        locales=["en", "zh"],
        workflow=_workflow(),
    )

    english = project_tree_nodes(workspace, "en")
    chinese = project_tree_nodes(workspace, "zh")

    assert [node["id"] for node in english] == ["role:Production", "role:Templates"]
    assert "4 / 4" in str(chinese[0]["label"])
    assert "1 / 2" in str(english[0]["children"][0]["label"])
    assert str(chinese[1]["children"][0]["label"]).endswith("2 / 2")


def test_project_tree_search_keeps_parents_and_each_plugin_once() -> None:
    workspace = ReviewWorkspace(
        projects=[
            _project("AlphaFix", "Production", "正式插件", "Channel"),
            _project("PluginSkeleton", "Templates", "模板", ""),
        ],
        locales=["en", "zh"],
        workflow=_workflow(),
    )

    nodes = project_tree_nodes(workspace, "zh", "skeleton")
    assert len(nodes) == 1
    assert nodes[0]["id"] == "role:Templates"
    leaves = nodes[0]["children"]
    assert [leaf["id"] for leaf in leaves] == ["project:PluginSkeleton"]
    assert project_name_from_node("project:PluginSkeleton") == "PluginSkeleton"
    assert project_name_from_node("role:Templates") is None


def test_deferred_project_is_labelled_and_excluded_from_main_progress() -> None:
    workspace = ReviewWorkspace(
        projects=[
            _project("PluginSkeleton", "Templates", "模板", ""),
            _project("HistoricalFixture", "Templates", "模板", "", deferred=True),
        ],
        locales=["en", "zh"],
        workflow=_workflow(),
    )

    templates = project_tree_nodes(workspace, "zh")[0]

    assert "2 / 2" in str(templates["label"])
    assert "4 / 4" not in str(templates["label"])
    deferred = next(
        leaf for leaf in templates["children"] if leaf["id"] == "project:HistoricalFixture"
    )
    assert "历史骨架 · 当前迁移非重点" in str(deferred["label"])
