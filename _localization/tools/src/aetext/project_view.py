"""Synchronize one effect project's explicit AeText project view."""

from __future__ import annotations

import os
import re
import tempfile
import uuid
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from .classification import ClassificationError, build_classification_plan

_LEGACY_RELATIVE_PATHS = {
    "CatalogView.h",
    "EffectText.h",
    "TextSuite.h",
    "EffectText.cpp",
    "GenerateTextCatalog.ps1",
}
_MANAGED_FILENAMES = {
    "aetext.h",
    "aetextclient.cpp",
    *(value.casefold() for value in _LEGACY_RELATIVE_PATHS),
}
_FILTER_NAMESPACE = uuid.UUID("b4e20958-4f3d-4fc6-90f2-ae1b67fabd7f")
_START_ELEMENT = re.compile(
    r"(?:(?<=\n)|(?<=\r)|\A)"
    r"(?P<indent>[ \t]*)<(?P<tag>[A-Za-z_][A-Za-z0-9_.-]*)\b[^>]*"
    r'\bInclude="(?P<include>[^"]+)"[^>]*>'
)


class ProjectViewError(ValueError):
    """The project view cannot be changed without risking unrelated content."""


@dataclass(frozen=True)
class _Block:
    start: int
    end: int
    tag: str
    include: str
    indent: str
    text: str


@dataclass(frozen=True)
class ProjectViewPlan:
    root: Path
    project_path: Path
    filters_path: Path
    catalog_path: Path
    project_text: str
    filters_text: str
    original_project_text: str
    original_filters_text: str
    project_bom: bool
    filters_bom: bool
    changes: tuple[str, ...]

    @property
    def changed(self) -> bool:
        return (
            self.project_text != self.original_project_text
            or self.filters_text != self.original_filters_text
        )


def _read_xml(path: Path) -> tuple[str, bool]:
    data = path.read_bytes()
    bom = data.startswith(b"\xef\xbb\xbf")
    try:
        return data.decode("utf-8-sig"), bom
    except UnicodeDecodeError as error:
        raise ProjectViewError(f"project XML is not UTF-8: {path}: {error}") from error


def _parse_xml(text: str, path: Path) -> ET.Element:
    try:
        return ET.fromstring(text)
    except ET.ParseError as error:
        raise ProjectViewError(f"cannot parse project XML {path}: {error}") from error


def _blocks(text: str, path: Path) -> list[_Block]:
    result: list[_Block] = []
    occupied_until = 0
    for match in _START_ELEMENT.finditer(text):
        if match.start() < occupied_until:
            continue
        end = match.end()
        if not match.group(0).rstrip().endswith("/>"):
            closing = f"</{match.group('tag')}>"
            closing_start = text.find(closing, end)
            if closing_start < 0:
                raise ProjectViewError(f"unterminated {match.group('tag')} Include item in {path}")
            end = closing_start + len(closing)
        line_ending = re.match(r"[ \t]*(?:\r\n|\r|\n)", text[end:])
        if line_ending:
            end += line_ending.end()
        elif not text[end:].strip():
            end = len(text)
        result.append(
            _Block(
                start=match.start(),
                end=end,
                tag=match.group("tag"),
                include=match.group("include"),
                indent=match.group("indent"),
                text=text[match.start() : end],
            )
        )
        occupied_until = end
    return result


def _resolved(project_path: Path, include: str) -> Path | None:
    if "$" in include or "%" in include:
        return None
    return (project_path.parent / include.replace("\\", os.sep).replace("/", os.sep)).resolve()


def _relative_include(project_path: Path, target: Path) -> str:
    return os.path.relpath(target, project_path.parent).replace("/", "\\")


def _newline(text: str) -> str:
    return "\r\n" if "\r\n" in text else "\n"


def _item_element(block: _Block, path: Path) -> ET.Element:
    try:
        return ET.fromstring(block.text.strip())
    except ET.ParseError as error:
        raise ProjectViewError(f"cannot parse Include item in {path}: {error}") from error


def _filter_value(block: _Block, path: Path) -> str | None:
    element = _item_element(block, path)
    values = [child.text or "" for child in element if child.tag.rsplit("}", 1)[-1] == "Filter"]
    if len(values) > 1:
        raise ProjectViewError(f"project item has multiple Filter values: {path}: {block.include}")
    return values[0] if values else None


def _canonical_project_item(tag: str, include: str, indent: str, newline: str) -> str:
    return f'{indent}<{tag} Include="{include}" />{newline}'


def _canonical_filter_item(tag: str, include: str, indent: str, newline: str) -> str:
    child_indent = indent + "  "
    return (
        f'{indent}<{tag} Include="{include}">{newline}'
        f"{child_indent}<Filter>Localization</Filter>{newline}"
        f"{indent}</{tag}>{newline}"
    )


def _canonical_filter_definition(project_path: Path, indent: str, newline: str) -> str:
    identifier = str(uuid.uuid5(_FILTER_NAMESPACE, project_path.as_posix().casefold()))
    child_indent = indent + "  "
    return (
        f'{indent}<Filter Include="Localization">{newline}'
        f"{child_indent}<UniqueIdentifier>{{{identifier}}}</UniqueIdentifier>{newline}"
        f"{indent}</Filter>{newline}"
    )


def _replace(text: str, replacements: list[tuple[int, int, str]]) -> str:
    result = text
    for start, end, value in sorted(replacements, reverse=True):
        result = result[:start] + value + result[end:]
    return result


def _insert_missing(
    text: str,
    blocks: list[_Block],
    tag: str,
    value: str,
) -> str:
    same_tag = [block for block in blocks if block.tag == tag]
    if same_tag:
        last = max(same_tag, key=lambda item: item.end)
        return text[: last.end] + value + text[last.end :]
    closing = text.find("</ItemGroup>")
    if closing < 0:
        raise ProjectViewError(f"project XML has no ItemGroup for required {tag} item")
    return text[:closing] + value + text[closing:]


def _managed_kind(
    project_path: Path,
    block: _Block,
    localization_root: Path,
    desired: dict[Path, tuple[str, str]],
    legacy: set[Path],
) -> tuple[str, Path] | None:
    resolved = _resolved(project_path, block.include)
    name = Path(block.include.replace("\\", "/")).name.casefold()
    if resolved is None:
        if name in _MANAGED_FILENAMES:
            raise ProjectViewError(
                f"managed filename uses an unexpected path: {project_path}: {block.include}"
            )
        return None
    if resolved in desired:
        return "desired", resolved
    if resolved in legacy:
        return "legacy", resolved
    if resolved.is_relative_to(localization_root):
        raise ProjectViewError(
            f"unexpected localization project item: {project_path}: {block.include}"
        )
    if name in _MANAGED_FILENAMES:
        raise ProjectViewError(
            f"managed filename uses an unexpected path: {project_path}: {block.include}"
        )
    return None


def _business_blocks(
    text: str,
    path: Path,
    project_path: Path,
    localization_root: Path,
    desired: dict[Path, tuple[str, str]],
    legacy: set[Path],
) -> list[str]:
    result: list[str] = []
    for block in _blocks(text, path):
        if block.tag == "Filter" and (
            block.include == "Localization" or block.include.startswith("Localization\\")
        ):
            continue
        if _managed_kind(project_path, block, localization_root, desired, legacy):
            continue
        result.append(block.text)
    return result


def _sync_project_text(
    text: str,
    path: Path,
    project_path: Path,
    localization_root: Path,
    desired: dict[Path, tuple[str, str]],
    legacy: set[Path],
) -> tuple[str, set[str]]:
    blocks = _blocks(text, path)
    newline = _newline(text)
    managed: dict[Path, list[_Block]] = {}
    legacy_blocks: list[_Block] = []
    for block in blocks:
        kind = _managed_kind(project_path, block, localization_root, desired, legacy)
        if kind is None:
            continue
        state, resolved = kind
        if state == "desired":
            managed.setdefault(resolved, []).append(block)
        else:
            legacy_blocks.append(block)
    duplicates = [items for items in managed.values() if len(items) > 1]
    if duplicates:
        duplicate = duplicates[0][0]
        raise ProjectViewError(
            f"duplicate managed project item: {project_path}: {duplicate.include}"
        )

    changes: set[str] = set()
    replacements: list[tuple[int, int, str]] = []
    legacy_indent: dict[str, str] = {}
    for block in legacy_blocks:
        legacy_indent.setdefault(block.tag, block.indent)
        replacements.append((block.start, block.end, ""))
    if legacy_blocks:
        changes.add("remove legacy localization project items")

    for target, (tag, include) in desired.items():
        existing = managed.get(target, [])
        if not existing:
            continue
        block = existing[0]
        element = _item_element(block, path)
        correct = block.tag == tag and element.attrib == {"Include": include} and len(element) == 0
        if not correct:
            replacements.append(
                (
                    block.start,
                    block.end,
                    _canonical_project_item(tag, include, block.indent, newline),
                )
            )
            changes.add("normalize localization project items")

    result = _replace(text, replacements)
    for target, (tag, include) in desired.items():
        if managed.get(target):
            continue
        current_blocks = _blocks(result, path)
        indentation = legacy_indent.get(tag, current_blocks[0].indent if current_blocks else "    ")
        value = _canonical_project_item(tag, include, indentation, newline)
        result = _insert_missing(result, current_blocks, tag, value)
        changes.add("add missing localization project items")
    return result, changes


def _sync_filters_text(
    text: str,
    path: Path,
    project_path: Path,
    localization_root: Path,
    desired: dict[Path, tuple[str, str]],
    legacy: set[Path],
) -> tuple[str, set[str]]:
    blocks = _blocks(text, path)
    newline = _newline(text)
    managed: dict[Path, list[_Block]] = {}
    legacy_blocks: list[_Block] = []
    localization_definitions: list[_Block] = []
    nested_definitions: list[_Block] = []
    for block in blocks:
        if block.tag == "Filter":
            if block.include == "Localization":
                localization_definitions.append(block)
            elif block.include.startswith("Localization\\"):
                nested_definitions.append(block)
            continue
        kind = _managed_kind(project_path, block, localization_root, desired, legacy)
        filter_value = _filter_value(block, path)
        if kind is None:
            if filter_value == "Localization" or (
                filter_value and filter_value.startswith("Localization\\")
            ):
                raise ProjectViewError(
                    f"unrelated item uses the Localization filter: {path}: {block.include}"
                )
            continue
        state, resolved = kind
        if state == "desired":
            managed.setdefault(resolved, []).append(block)
        else:
            legacy_blocks.append(block)
    duplicates = [items for items in managed.values() if len(items) > 1]
    if duplicates:
        duplicate = duplicates[0][0]
        raise ProjectViewError(f"duplicate managed filter item: {path}: {duplicate.include}")
    if len(localization_definitions) > 1:
        raise ProjectViewError(f"duplicate Localization filter definitions: {path}")

    changes: set[str] = set()
    replacements: list[tuple[int, int, str]] = []
    legacy_indent: dict[str, str] = {}
    for block in legacy_blocks:
        legacy_indent.setdefault(block.tag, block.indent)
        replacements.append((block.start, block.end, ""))
    if legacy_blocks:
        changes.add("remove legacy localization filter items")
    for block in nested_definitions:
        replacements.append((block.start, block.end, ""))
    if nested_definitions:
        changes.add("remove nested Localization filters")

    for target, (tag, include) in desired.items():
        existing = managed.get(target, [])
        if not existing:
            continue
        block = existing[0]
        element = _item_element(block, path)
        correct = (
            block.tag == tag
            and element.attrib == {"Include": include}
            and len(element) == 1
            and element[0].tag.rsplit("}", 1)[-1] == "Filter"
            and (element[0].text or "") == "Localization"
        )
        if not correct:
            replacements.append(
                (
                    block.start,
                    block.end,
                    _canonical_filter_item(tag, include, block.indent, newline),
                )
            )
            changes.add("normalize localization filter items")

    result = _replace(text, replacements)
    for target, (tag, include) in desired.items():
        if managed.get(target):
            continue
        current_blocks = _blocks(result, path)
        indentation = legacy_indent.get(tag, current_blocks[0].indent if current_blocks else "    ")
        value = _canonical_filter_item(tag, include, indentation, newline)
        result = _insert_missing(result, current_blocks, tag, value)
        changes.add("add missing localization filter items")

    if not localization_definitions:
        current_blocks = _blocks(result, path)
        filter_blocks = [block for block in current_blocks if block.tag == "Filter"]
        indentation = filter_blocks[-1].indent if filter_blocks else "    "
        value = _canonical_filter_definition(project_path, indentation, newline)
        result = _insert_missing(result, current_blocks, "Filter", value)
        changes.add("add Localization filter")
    return result, changes


def _validate_final(
    project_text: str,
    filters_text: str,
    project_path: Path,
    filters_path: Path,
    localization_root: Path,
    desired: dict[Path, tuple[str, str]],
    legacy: set[Path],
) -> None:
    _parse_xml(project_text, project_path)
    _parse_xml(filters_text, filters_path)
    project_counts = {target: 0 for target in desired}
    filter_counts = {target: 0 for target in desired}
    for block in _blocks(project_text, project_path):
        kind = _managed_kind(project_path, block, localization_root, desired, legacy)
        if kind and kind[0] == "desired":
            project_counts[kind[1]] += 1
        elif kind:
            raise ProjectViewError(
                f"legacy project item remained after synchronization: {block.include}"
            )
    localization_definitions = 0
    for block in _blocks(filters_text, filters_path):
        if block.tag == "Filter":
            if block.include == "Localization":
                localization_definitions += 1
            elif block.include.startswith("Localization\\"):
                raise ProjectViewError(f"nested Localization filter remained: {block.include}")
            continue
        kind = _managed_kind(project_path, block, localization_root, desired, legacy)
        if kind and kind[0] == "desired":
            filter_counts[kind[1]] += 1
            if _filter_value(block, filters_path) != "Localization":
                raise ProjectViewError(
                    f"managed filter item is not in Localization: {block.include}"
                )
        elif kind:
            raise ProjectViewError(
                f"legacy filter item remained after synchronization: {block.include}"
            )
    if any(value != 1 for value in project_counts.values()):
        raise ProjectViewError(
            f"project does not contain each required localization item once: {project_path}"
        )
    if any(value != 1 for value in filter_counts.values()):
        raise ProjectViewError(
            f"filters do not contain each required localization item once: {filters_path}"
        )
    if localization_definitions != 1:
        raise ProjectViewError(f"filters must define Localization exactly once: {filters_path}")


def build_project_view_plan(root: str | Path, project_name: str) -> ProjectViewPlan:
    repository = Path(root).resolve()
    if (
        not project_name
        or Path(project_name).name != project_name
        or any(separator in project_name for separator in ("/", "\\"))
    ):
        raise ProjectViewError("project must be one MSBuildProjectName, not a path")
    try:
        classification = build_classification_plan(repository)
    except ClassificationError as error:
        raise ProjectViewError(str(error)) from error
    if classification.changed:
        raise ProjectViewError("classification views are stale; run sync-classification first")
    matches = [item for item in classification.projects if item.name == project_name]
    if not matches:
        matches = [
            item
            for item in classification.projects
            if item.name.casefold() == project_name.casefold()
        ]
    if len(matches) != 1:
        raise ProjectViewError(
            f"expected exactly one effect project named {project_name}; found {len(matches)}"
        )
    item = matches[0]
    if item.role == "Support":
        raise ProjectViewError("sync-project-view applies only to effect projects")
    project_path = item.project_path
    filters_path = project_path.with_suffix(project_path.suffix + ".filters")
    if not filters_path.is_file():
        raise ProjectViewError(f"project filters file does not exist: {filters_path}")

    localization_root = (repository / "_localization").resolve()
    targets = {
        (localization_root / "AeText.h").resolve(): "ClInclude",
        (localization_root / "core" / "AeTextClient.cpp").resolve(): "ClCompile",
        item.catalog_path.resolve(): "None",
    }
    for target in targets:
        if not target.is_file():
            raise ProjectViewError(f"required localization input does not exist: {target}")
    desired = {
        target: (tag, _relative_include(project_path, target)) for target, tag in targets.items()
    }
    legacy = {(localization_root / relative).resolve() for relative in _LEGACY_RELATIVE_PATHS}

    project_text, project_bom = _read_xml(project_path)
    filters_text, filters_bom = _read_xml(filters_path)
    _parse_xml(project_text, project_path)
    _parse_xml(filters_text, filters_path)
    project_business = _business_blocks(
        project_text, project_path, project_path, localization_root, desired, legacy
    )
    filters_business = _business_blocks(
        filters_text, filters_path, project_path, localization_root, desired, legacy
    )
    new_project, project_changes = _sync_project_text(
        project_text, project_path, project_path, localization_root, desired, legacy
    )
    new_filters, filters_changes = _sync_filters_text(
        filters_text, filters_path, project_path, localization_root, desired, legacy
    )
    if project_business != _business_blocks(
        new_project, project_path, project_path, localization_root, desired, legacy
    ):
        raise ProjectViewError("project synchronization changed or reordered business items")
    if filters_business != _business_blocks(
        new_filters, filters_path, project_path, localization_root, desired, legacy
    ):
        raise ProjectViewError("filter synchronization changed or reordered business items")
    _validate_final(
        new_project,
        new_filters,
        project_path,
        filters_path,
        localization_root,
        desired,
        legacy,
    )
    return ProjectViewPlan(
        root=repository,
        project_path=project_path,
        filters_path=filters_path,
        catalog_path=item.catalog_path,
        project_text=new_project,
        filters_text=new_filters,
        original_project_text=project_text,
        original_filters_text=filters_text,
        project_bom=project_bom,
        filters_bom=filters_bom,
        changes=tuple(sorted(project_changes | filters_changes)),
    )


def _atomic_write(path: Path, text: str, bom: bool) -> None:
    data = (("\ufeff" if bom else "") + text).encode("utf-8")
    descriptor, temporary_name = tempfile.mkstemp(prefix=path.name + ".tmp.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(data)
        os.replace(temporary, path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def apply_project_view_plan(plan: ProjectViewPlan) -> None:
    current_project, current_project_bom = _read_xml(plan.project_path)
    current_filters, current_filters_bom = _read_xml(plan.filters_path)
    if (
        current_project != plan.original_project_text
        or current_filters != plan.original_filters_text
        or current_project_bom != plan.project_bom
        or current_filters_bom != plan.filters_bom
    ):
        raise ProjectViewError("project files changed after the synchronization plan was built")
    if plan.project_text != plan.original_project_text:
        _atomic_write(plan.project_path, plan.project_text, plan.project_bom)
    if plan.filters_text != plan.original_filters_text:
        _atomic_write(plan.filters_path, plan.filters_text, plan.filters_bom)
