"""Test-only NiceGUI server backed by a temporary repository fixture."""

from __future__ import annotations

import sys
from pathlib import Path

from aetext.build import ProjectManifest
from aetext.catalog.review import ReviewWorkspaceService
from aetext.web import run_review


class FixtureDiscovery:
    def __init__(self, manifest: ProjectManifest) -> None:
        self.manifest = manifest

    def discover(self, plugin_name: str) -> ProjectManifest:
        if plugin_name != self.manifest.name:
            raise ValueError(plugin_name)
        return self.manifest


def main() -> None:
    root = Path(sys.argv[1]).resolve()
    port = int(sys.argv[2])
    manifest = ProjectManifest(
        project_path=root / "Fixture.vcxproj",
        name="Fixture",
        catalog_path=root / "_localization" / "catalog" / "(Templates)" / "Fixture.json",
        namespace="FixtureText",
        role="Templates",
        category="",
        family_definition_path=(root / "_localization" / "families" / "fs" / "generation.json"),
        inputs=[root / "Fixture.cpp"],
    )
    service = ReviewWorkspaceService(root, discovery=FixtureDiscovery(manifest))
    run_review(service, "Fixture", locale="zh", port=port, show_browser=False)


if __name__ == "__main__":
    main()
