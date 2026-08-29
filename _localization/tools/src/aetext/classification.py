"""Derive repository classification views from project source and catalog placement."""

from __future__ import annotations

import copy
import html
import json
import os
import re
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, replace
from pathlib import Path

_IGNORED_PARTS = {".git", ".vs", ".venv", "debug", "release", "x64", "x86"}
_ROLE_ROOTS = {
    "(Templates)": "Templates",
    "(Tests)": "Tests",
    "(Abandoned)": "Abandoned",
    "_Support": "Support",
}
_ROLE_DIRECTORIES = {value: key for key, value in _ROLE_ROOTS.items()}
_COMMENT_BLOCK = re.compile(r"/\*.*?\*/", re.DOTALL)
_COMMENT_LINE = re.compile(r"//[^\r\n]*")
_CATEGORY = re.compile(
    r"\bCategory\s*\{\s*(?P<value>\"(?:\\.|[^\"])*\"|[A-Za-z_][A-Za-z0-9_]*)\s*\}",
    re.DOTALL,
)
_QUOTED_INCLUDE = re.compile(r'^\s*#\s*include\s+"(?P<path>[^"]+)"', re.MULTILINE)


class ClassificationError(ValueError):
    """The repository does not express one unambiguous classification."""


@dataclass(frozen=True)
class ProjectClassification:
    name: str
    project_path: Path
    catalog_path: Path
    expected_catalog_path: Path
    category: str
    role: str
    isolation: str
    solution_folder: str


@dataclass(frozen=True)
class ClassificationPlan:
    root: Path
    plugin_map_path: Path
    solution_path: Path
    projects: list[ProjectClassification]
    plugin_map_text: str
    solution_text: str
    catalog_moves: list[tuple[Path, Path]]
    plugin_map_changed: bool
    solution_changed: bool

    @property
    def changed(self) -> bool:
        return self.plugin_map_changed or self.solution_changed or bool(self.catalog_moves)


def _local_name(value: str) -> str:
    return value.rsplit("}", 1)[-1]


def _strip_comments(value: str) -> str:
    return _COMMENT_LINE.sub("", _COMMENT_BLOCK.sub("", value))


def _xml_items(root: ET.Element, kind: str) -> list[str]:
    return [
        value
        for element in root.iter()
        if _local_name(element.tag) == kind and (value := element.attrib.get("Include")) is not None
    ]


def _resolved_item(project: Path, include: str) -> Path:
    return (project.parent / include.replace("\\", os.sep)).resolve()


def _quoted_include_closure(start: Path) -> list[tuple[Path, str]]:
    pending = [start.resolve()]
    visited: set[Path] = set()
    result: list[tuple[Path, str]] = []
    while pending:
        path = pending.pop()
        if path in visited or not path.is_file():
            continue
        visited.add(path)
        text = path.read_text(encoding="utf-8-sig", errors="strict")
        stripped = _strip_comments(text)
        result.append((path, stripped))
        for match in _QUOTED_INCLUDE.finditer(stripped):
            included = (path.parent / match.group("path").replace("\\", os.sep)).resolve()
            if included.is_file():
                pending.append(included)
    return result


def _source_category(project: Path, project_xml: ET.Element) -> str:
    pipl_items = [
        _resolved_item(project, value)
        for value in _xml_items(project_xml, "CustomBuild")
        if value.casefold().endswith("pipl.r")
    ]
    if len(pipl_items) != 1 or not pipl_items[0].is_file():
        raise ClassificationError(
            f"{project}: expected exactly one existing PiPL CustomBuild input, "
            f"got {len(pipl_items)}"
        )
    sources = _quoted_include_closure(pipl_items[0])
    category_uses = [
        match.group("value") for _, text in sources for match in _CATEGORY.finditer(text)
    ]
    if len(category_uses) != 1:
        raise ClassificationError(
            f"{project}: expected exactly one PiPL Category value, got {len(category_uses)}"
        )
    category_use = category_uses[0]
    if category_use.startswith('"'):
        category = json.loads(category_use)
    else:
        # The PiPL token owns the lookup; similarly named category macros are not candidates.
        definitions: list[str] = []
        for _, text in sources:
            for line in text.splitlines():
                match = re.match(
                    rf"^\s*#\s*define\s+{re.escape(category_use)}\s+"
                    rf'(?P<value>"(?:\\.|[^"\\])*")\s*$',
                    line,
                )
                if match:
                    definitions.append(json.loads(match.group("value")))
        if len(definitions) != 1:
            raise ClassificationError(
                f"{project}: category macro {category_use} must have exactly one "
                "active definition; "
                f"found {len(definitions)}"
            )
        category = definitions[0]
    if not isinstance(category, str) or not category:
        raise ClassificationError(f"{project}: AE category must be one nonempty string")
    if re.search(r'[\\/:*?"<>|]', category):
        raise ClassificationError(
            f"{project}: AE category is not a safe directory segment: {category}"
        )
    return category


def _catalog_for_project(
    project: Path,
    project_xml: ET.Element,
    catalog_root: Path,
    catalogs_by_name: dict[str, list[Path]],
) -> Path:
    explicit = {
        candidate
        for value in _xml_items(project_xml, "None")
        if (candidate := _resolved_item(project, value)).is_relative_to(catalog_root)
    }
    missing = sorted(path for path in explicit if not path.is_file())
    if missing:
        raise ClassificationError(f"{project}: explicit catalog does not exist: {missing[0]}")
    candidates = explicit | set(catalogs_by_name.get(project.stem.casefold(), []))
    if not candidates:
        raise ClassificationError(
            f"{project}: no catalog matches MSBuildProjectName {project.stem}"
        )
    if len(candidates) != 1:
        values = ", ".join(path.as_posix() for path in sorted(candidates))
        raise ClassificationError(f"{project}: multiple catalogs match one project: {values}")
    return next(iter(candidates))


def _catalog_scope(catalog_root: Path, catalog: Path) -> tuple[str, str, Path]:
    relative = catalog.relative_to(catalog_root)
    if len(relative.parts) < 2:
        raise ClassificationError(f"catalog must be below one role/category directory: {catalog}")
    first = relative.parts[0]
    role = _ROLE_ROOTS.get(first, "Production")
    isolation_parts = relative.parent.parts[1:]
    for part in isolation_parts:
        if not part or part in {".", ".."} or re.search(r'[\\/:*?"<>|]', part):
            raise ClassificationError(f"catalog has an invalid isolation segment: {catalog}")
    return role, "\\".join(isolation_parts), relative


def _expected_catalog_path(
    catalog_root: Path,
    relative: Path,
    role: str,
    category: str,
) -> Path:
    isolation_parts = relative.parent.parts[1:]
    expected_root = category if role == "Production" else _ROLE_DIRECTORIES[role]
    expected = catalog_root.joinpath(expected_root, *isolation_parts, relative.name).resolve()
    return expected


def _plugin_map(projects: list[ProjectClassification]) -> str:
    lines = [
        '<?xml version="1.0" encoding="utf-8"?>',
        '<Project xmlns="http://schemas.microsoft.com/developer/msbuild/2003">',
        "  <!-- Generated by `uv run aetext sync-classification`; do not edit by hand. -->",
    ]
    for project in projects:
        name = html.escape(project.name, quote=True)
        lines.append(f"  <PropertyGroup Condition=\"'$(MSBuildProjectName)'=='{name}'\">")
        if project.category:
            lines.append(
                f"    <FsAeCategory>{html.escape(project.category, quote=False)}</FsAeCategory>"
            )
        lines.append(f"    <FsProjectRole>{project.role}</FsProjectRole>")
        if project.isolation:
            escaped_isolation = html.escape(project.isolation, quote=False)
            lines.append(f"    <FsOutputIsolation>{escaped_isolation}</FsOutputIsolation>")
        lines.append("  </PropertyGroup>")
    lines.extend(["</Project>", ""])
    return "\n".join(lines)


def _solution_folder(project: ProjectClassification) -> str:
    root = project.category if project.role == "Production" else _ROLE_DIRECTORIES[project.role]
    suffix = project.isolation.replace("\\", "/")
    return f"/{root}/{suffix + '/' if suffix else ''}"


def _folder_order(name: str) -> tuple[int, str]:
    fixed = {
        "/_Support/": 0,
        "/(Abandoned)/": 1,
        "/(Templates)/": 2,
        "/(Tests)/": 3,
    }
    return fixed.get(name, 4), name.casefold()


def _solution(path: Path, projects: list[ProjectClassification]) -> str:
    try:
        existing_root = ET.parse(path).getroot()
    except (OSError, ET.ParseError) as error:
        raise ClassificationError(f"cannot read solution {path}: {error}") from error
    new_root = ET.Element("Solution")
    configurations = [
        element for element in existing_root if _local_name(element.tag) == "Configurations"
    ]
    if len(configurations) != 1:
        raise ClassificationError(
            f"solution must contain exactly one Configurations element: {path}"
        )
    new_root.append(copy.deepcopy(configurations[0]))
    for element in existing_root:
        if _local_name(element.tag) == "Folder" and element.attrib.get("Name", "").startswith(
            "/AeText Infrastructure/"
        ):
            new_root.append(copy.deepcopy(element))

    existing_projects: dict[str, ET.Element] = {}
    for element in existing_root.iter():
        if _local_name(element.tag) != "Project" or "Path" not in element.attrib:
            continue
        key = element.attrib["Path"].replace("\\", "/").casefold()
        if key in existing_projects:
            raise ClassificationError(
                f"solution lists project more than once: {element.attrib['Path']}"
            )
        existing_projects[key] = copy.deepcopy(element)

    grouped: dict[str, list[tuple[ProjectClassification, ET.Element]]] = {}
    for project in projects:
        relative = project.project_path.relative_to(path.parent).as_posix()
        element = existing_projects.pop(relative.casefold(), None)
        if element is None:
            raise ClassificationError(f"solution does not list project: {relative}")
        element.attrib["Path"] = relative
        grouped.setdefault(project.solution_folder, []).append((project, element))
    if existing_projects:
        raise ClassificationError(
            "solution contains projects without a catalog classification: "
            + ", ".join(sorted(existing_projects))
        )
    for folder_name in sorted(grouped, key=_folder_order):
        folder = ET.SubElement(new_root, "Folder", {"Name": folder_name})
        for _, element in sorted(grouped[folder_name], key=lambda item: item[0].name.casefold()):
            folder.append(element)
    ET.indent(new_root, space="  ")
    return ET.tostring(new_root, encoding="unicode", short_empty_elements=True) + "\n"


def _read_text_if_exists(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig") if path.is_file() else ""


def build_classification_plan(root: str | Path) -> ClassificationPlan:
    repository = Path(root).resolve()
    catalog_root = (repository / "_localization" / "catalog").resolve()
    if not catalog_root.is_dir():
        raise ClassificationError(f"catalog root does not exist: {catalog_root}")
    catalog_paths = sorted(path.resolve() for path in catalog_root.rglob("*.json"))
    catalogs_by_name: dict[str, list[Path]] = {}
    for catalog in catalog_paths:
        catalogs_by_name.setdefault(catalog.stem.casefold(), []).append(catalog)

    project_paths = []
    for path in repository.rglob("*.vcxproj"):
        relative = path.relative_to(repository)
        if any(part.casefold() in _IGNORED_PARTS for part in relative.parts):
            continue
        project_paths.append(path.resolve())
    projects: list[ProjectClassification] = []
    used_catalogs: set[Path] = set()
    for project in sorted(project_paths, key=lambda value: (value.stem.casefold(), value)):
        try:
            project_xml = ET.parse(project).getroot()
        except ET.ParseError as error:
            raise ClassificationError(f"cannot parse project {project}: {error}") from error
        catalog = _catalog_for_project(project, project_xml, catalog_root, catalogs_by_name)
        if catalog in used_catalogs:
            raise ClassificationError(f"multiple projects resolve to catalog: {catalog}")
        role, isolation, relative_catalog = _catalog_scope(catalog_root, catalog)
        category = "" if role == "Support" else _source_category(project, project_xml)
        expected_catalog = _expected_catalog_path(catalog_root, relative_catalog, role, category)
        classification = ProjectClassification(
            name=project.stem,
            project_path=project,
            catalog_path=catalog,
            expected_catalog_path=expected_catalog,
            category=category,
            role=role,
            isolation=isolation,
            solution_folder="",
        )
        classification = replace(classification, solution_folder=_solution_folder(classification))
        projects.append(classification)
        used_catalogs.add(catalog)
    orphaned = sorted(set(catalog_paths) - used_catalogs)
    if orphaned:
        raise ClassificationError(
            "catalogs do not match any MSBuildProjectName: "
            + ", ".join(path.as_posix() for path in orphaned)
        )
    destinations = [project.expected_catalog_path for project in projects]
    if len(destinations) != len(set(destinations)):
        raise ClassificationError("multiple projects derive the same expected catalog path")
    moves = [
        (project.catalog_path, project.expected_catalog_path)
        for project in projects
        if project.catalog_path != project.expected_catalog_path
    ]
    for _source, destination in moves:
        if destination.is_file() and destination not in {item[0] for item in moves}:
            raise ClassificationError(
                f"catalog move would overwrite an existing file: {destination}"
            )

    projects = sorted(projects, key=lambda item: (item.name.casefold(), item.project_path))
    plugin_map_path = repository / "Directory.Build.PluginMap.props"
    solution_path = repository / "F's PluginsProjects.slnx"
    plugin_map_text = _plugin_map(projects)
    solution_text = _solution(solution_path, projects)
    return ClassificationPlan(
        root=repository,
        plugin_map_path=plugin_map_path,
        solution_path=solution_path,
        projects=projects,
        plugin_map_text=plugin_map_text,
        solution_text=solution_text,
        catalog_moves=moves,
        plugin_map_changed=_read_text_if_exists(plugin_map_path) != plugin_map_text,
        solution_changed=_read_text_if_exists(solution_path) != solution_text,
    )


def check_project_classification(
    root: str | Path, project_path: str | Path
) -> ProjectClassification:
    repository = Path(root).resolve()
    project = Path(project_path).resolve()
    if not project.is_relative_to(repository) or not project.is_file():
        raise ClassificationError(f"project is not an existing repository file: {project}")
    catalog_root = (repository / "_localization" / "catalog").resolve()
    catalogs_by_name: dict[str, list[Path]] = {}
    for catalog in catalog_root.rglob("*.json"):
        catalogs_by_name.setdefault(catalog.stem.casefold(), []).append(catalog.resolve())
    try:
        project_xml = ET.parse(project).getroot()
    except ET.ParseError as error:
        raise ClassificationError(f"cannot parse project {project}: {error}") from error
    catalog = _catalog_for_project(project, project_xml, catalog_root, catalogs_by_name)
    role, isolation, relative_catalog = _catalog_scope(catalog_root, catalog)
    category = "" if role == "Support" else _source_category(project, project_xml)
    expected_catalog = _expected_catalog_path(catalog_root, relative_catalog, role, category)
    classification = ProjectClassification(
        name=project.stem,
        project_path=project,
        catalog_path=catalog,
        expected_catalog_path=expected_catalog,
        category=category,
        role=role,
        isolation=isolation,
        solution_folder="",
    )
    classification = replace(classification, solution_folder=_solution_folder(classification))
    if catalog != expected_catalog:
        raise ClassificationError(
            f"{classification.name}: catalog classification is stale; expected {expected_catalog}"
        )

    plugin_map_path = repository / "Directory.Build.PluginMap.props"
    try:
        plugin_map = ET.parse(plugin_map_path).getroot()
    except (OSError, ET.ParseError) as error:
        raise ClassificationError(
            f"cannot read generated PluginMap {plugin_map_path}: {error}"
        ) from error
    condition = f"'$(MSBuildProjectName)'=='{classification.name}'"
    groups = [
        element
        for element in plugin_map
        if _local_name(element.tag) == "PropertyGroup"
        and element.attrib.get("Condition") == condition
    ]
    if len(groups) != 1:
        raise ClassificationError(
            f"{classification.name}: generated PluginMap must contain exactly one project entry"
        )
    values = {_local_name(child.tag): child.text or "" for child in groups[0]}
    expected_values = {
        "FsAeCategory": classification.category,
        "FsProjectRole": classification.role,
        "FsOutputIsolation": classification.isolation,
    }
    actual_values = {
        "FsAeCategory": values.get("FsAeCategory", ""),
        "FsProjectRole": values.get("FsProjectRole", ""),
        "FsOutputIsolation": values.get("FsOutputIsolation", ""),
    }
    if actual_values != expected_values:
        raise ClassificationError(
            f"{classification.name}: generated PluginMap is stale: "
            f"expected {expected_values}, got {actual_values}"
        )

    solution_path = repository / "F's PluginsProjects.slnx"
    try:
        solution = ET.parse(solution_path).getroot()
    except (OSError, ET.ParseError) as error:
        raise ClassificationError(f"cannot read solution {solution_path}: {error}") from error
    relative_project = project.relative_to(repository).as_posix().casefold()
    folders = []
    for folder in solution:
        if _local_name(folder.tag) != "Folder":
            continue
        for element in folder:
            if (
                _local_name(element.tag) == "Project"
                and element.attrib.get("Path", "").replace("\\", "/").casefold() == relative_project
            ):
                folders.append(folder.attrib.get("Name", ""))
    if folders != [classification.solution_folder]:
        raise ClassificationError(
            f"{classification.name}: solution classification is stale: "
            f"expected {classification.solution_folder}, got {folders}"
        )
    return classification


def _atomic_write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=path.name + ".tmp.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as output:
            output.write(value)
        os.replace(temporary, path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def apply_classification_plan(plan: ClassificationPlan) -> None:
    moving_sources = {source for source, _ in plan.catalog_moves}
    for _, destination in plan.catalog_moves:
        if destination.exists() and destination not in moving_sources:
            raise ClassificationError(
                f"catalog move would overwrite an existing path: {destination}"
            )
    for source, destination in plan.catalog_moves:
        destination.parent.mkdir(parents=True, exist_ok=True)
        source.replace(destination)
    _atomic_write(plan.plugin_map_path, plan.plugin_map_text)
    _atomic_write(plan.solution_path, plan.solution_text)
