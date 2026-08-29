"""Discover a reviewable plugin from repository projects and evaluated MSBuild inputs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from aetext.build import ProjectManifest, write_project_manifest

_IGNORED_PARTS = {
    ".git",
    ".vs",
    ".venv",
    "debug",
    "release",
    "x64",
    "x86",
}


@dataclass(frozen=True)
class ProjectCandidate:
    name: str
    project_path: Path


def repository_root(start: str | Path | None = None) -> Path:
    candidates = [Path(start).resolve() if start is not None else Path.cwd().resolve()]
    candidates.append(Path(__file__).resolve())
    for candidate in candidates:
        for parent in [candidate, *candidate.parents]:
            if (parent / "AGENTS.md").is_file() and (
                parent / "_localization" / "AeText.Build.targets"
            ).is_file():
                return parent
    raise FileNotFoundError("AeText repository root was not found")


class ProjectDiscoveryService:
    def __init__(self, root: str | Path | None = None) -> None:
        self.root = repository_root(root)

    def list_projects(self) -> list[ProjectCandidate]:
        result: list[ProjectCandidate] = []
        for path in self.root.rglob("*.vcxproj"):
            relative = path.relative_to(self.root)
            if any(part.casefold() in _IGNORED_PARTS for part in relative.parts):
                continue
            result.append(ProjectCandidate(name=path.stem, project_path=path.resolve()))
        return sorted(result, key=lambda item: (item.name.casefold(), item.project_path))

    def _candidates(self, plugin_name: str) -> list[Path]:
        if (
            not plugin_name
            or plugin_name in {".", ".."}
            or Path(plugin_name).name != plugin_name
            or "/" in plugin_name
            or "\\" in plugin_name
        ):
            raise ValueError("plugin name must be one project name, not a path")
        result = [
            item.project_path
            for item in self.list_projects()
            if item.name.casefold() == plugin_name.casefold()
        ]
        exact = [path for path in result if path.stem == plugin_name]
        return sorted(exact or result)

    def discover(self, plugin_name: str) -> ProjectManifest:
        candidates = self._candidates(plugin_name)
        if not candidates:
            raise FileNotFoundError(f"no vcxproj found for plugin: {plugin_name}")
        if len(candidates) != 1:
            values = ", ".join(path.as_posix() for path in candidates)
            raise ValueError(f"plugin name is ambiguous: {plugin_name}: {values}")
        manifest = write_project_manifest(candidates[0])
        self._validate_manifest(manifest)
        return manifest

    def _validate_manifest(self, manifest: ProjectManifest) -> None:
        catalog_root = (self.root / "_localization" / "catalog").resolve()
        family_root = (self.root / "_localization" / "families").resolve()
        if not manifest.catalog_path.is_relative_to(catalog_root):
            raise ValueError(f"catalog escaped repository catalog root: {manifest.catalog_path}")
        if not manifest.family_definition_path.is_relative_to(family_root):
            raise ValueError(
                "family definition escaped repository family root: "
                f"{manifest.family_definition_path}"
            )
        if not manifest.catalog_path.is_file():
            raise FileNotFoundError(f"project catalog does not exist: {manifest.catalog_path}")
        if not manifest.family_definition_path.is_file():
            raise FileNotFoundError(
                f"family definition does not exist: {manifest.family_definition_path}"
            )
