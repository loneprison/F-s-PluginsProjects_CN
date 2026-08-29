from __future__ import annotations

from pathlib import Path

import pytest

from aetext.build.msbuild_manifest import read_manifest
from aetext.core.projects import ProjectDiscoveryService

REPOSITORY_ROOT = Path(__file__).resolve().parents[4]


def test_discovers_plugin_skeleton_from_evaluated_project() -> None:
    manifest = ProjectDiscoveryService(REPOSITORY_ROOT).discover("PluginSkeleton")

    assert manifest.name == "PluginSkeleton"
    assert manifest.catalog_path.name == "PluginSkeleton.json"
    assert manifest.family_definition_path.name == "generation.json"
    assert len(manifest.inputs) == 58


def test_lists_all_repository_projects_without_evaluating_them() -> None:
    projects = ProjectDiscoveryService(REPOSITORY_ROOT).list_projects()

    assert len(projects) == 116
    assert "PluginSkeleton" in {project.name for project in projects}


@pytest.mark.parametrize("name", ["", "..", "PluginSkeleton/Win", r"PluginSkeleton\Win"])
def test_rejects_path_like_plugin_names(name: str) -> None:
    with pytest.raises(ValueError):
        ProjectDiscoveryService(REPOSITORY_ROOT).discover(name)


def test_manifest_rejects_missing_real_project_input(tmp_path: Path) -> None:
    project = tmp_path / "Fixture.vcxproj"
    catalog = tmp_path / "Fixture.json"
    family = tmp_path / "generation.json"
    missing = tmp_path / "Missing.cpp"
    manifest = tmp_path / "manifest.txt"
    manifest.write_text(
        f"PROJECT|{project}|Fixture|{catalog}|FixtureText|Templates||{family}\nCOMPILE|{missing}\n",
        encoding="utf-8",
    )

    with pytest.raises(FileNotFoundError, match=r"Missing\.cpp"):
        read_manifest(manifest)
