"""MSBuild integration for explicit AeText project inputs."""

from .msbuild_manifest import ProjectManifest, read_manifest, write_project_manifest

__all__ = ["ProjectManifest", "read_manifest", "write_project_manifest"]
