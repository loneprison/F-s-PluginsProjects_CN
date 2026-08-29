"""Evaluate the repository MSBuild target and load its explicit project-input manifest."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from pydantic import BaseModel, ConfigDict


class ProjectManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    project_path: Path
    name: str
    catalog_path: Path
    namespace: str
    role: str
    category: str
    family_definition_path: Path
    inputs: list[Path]


def read_manifest(path: str | Path) -> ProjectManifest:
    project: dict[str, object] | None = None
    inputs: list[Path] = []
    manifest_path = Path(path)
    for line in manifest_path.read_text(encoding="utf-8-sig").splitlines():
        kind, separator, value = line.partition("|")
        if not separator:
            continue
        if kind == "PROJECT":
            fields = value.split("|", 6)
            if len(fields) != 7:
                raise ValueError(f"malformed PROJECT manifest line: {manifest_path}")
            project = {
                "project_path": Path(fields[0]).resolve(),
                "name": fields[1],
                "catalog_path": Path(fields[2]).resolve(),
                "namespace": fields[3],
                "role": fields[4],
                "category": fields[5],
                "family_definition_path": Path(fields[6]).resolve(),
            }
        elif kind in {"COMPILE", "INCLUDE"}:
            candidate = Path(value).resolve()
            if not candidate.is_file():
                raise FileNotFoundError(f"manifest {kind} input does not exist: {candidate}")
            if candidate not in inputs:
                inputs.append(candidate)
    if project is None:
        raise ValueError(f"manifest has no PROJECT record: {manifest_path}")
    project["inputs"] = inputs
    return ProjectManifest.model_validate(project, strict=True)


def _normalized_environment() -> dict[str, str]:
    result: dict[str, str] = {}
    path_value: str | None = None
    for key, value in os.environ.items():
        if key.casefold() == "path":
            if path_value is None or key == "Path":
                path_value = value
            continue
        result[key] = value
    if path_value is not None:
        result["Path"] = path_value
    return result


def _msbuild_path() -> Path:
    discovered = shutil.which("MSBuild.exe") or shutil.which("MSBuild")
    if discovered:
        return Path(discovered).resolve()
    validated = Path(
        r"C:\Program Files\Microsoft Visual Studio\18\Community\MSBuild\Current\Bin\MSBuild.exe"
    )
    if validated.is_file():
        return validated
    raise FileNotFoundError("MSBuild was not found in PATH or at the validated VS 18 location")


def write_project_manifest(
    project_path: str | Path,
    *,
    configuration: str = "Debug",
    platform: str = "x64",
) -> ProjectManifest:
    project = Path(project_path).resolve()
    with TemporaryDirectory(prefix="AeTextProject-") as directory:
        manifest = Path(directory) / "project.txt"
        command = [
            str(_msbuild_path()),
            str(project),
            "/t:WriteAeTextInventoryManifest",
            f"/p:Configuration={configuration}",
            f"/p:Platform={platform}",
            f"/p:AeTextInventoryOutput={manifest}",
            "/nologo",
            "/v:quiet",
        ]
        completed = subprocess.run(
            command,
            cwd=project.parent,
            env=_normalized_environment(),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if completed.returncode != 0:
            output = "\n".join(value for value in (completed.stdout, completed.stderr) if value)
            raise RuntimeError(f"MSBuild project discovery failed for {project}:\n{output}")
        return read_manifest(manifest)
