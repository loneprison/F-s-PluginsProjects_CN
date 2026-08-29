from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from aetext.classification import apply_classification_plan, build_classification_plan
from aetext.project_view import (
    ProjectViewError,
    apply_project_view_plan,
    build_project_view_plan,
)


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _fixture(root: Path, *, migrated: bool) -> Path:
    localization = root / "_localization"
    (localization / "core").mkdir(parents=True)
    (localization / "catalog" / "NF's Plugins-Filter").mkdir(parents=True)
    for relative in (
        "AeText.h",
        "core/AeTextClient.cpp",
        "CatalogView.h",
        "EffectText.h",
        "TextSuite.h",
        "EffectText.cpp",
        "GenerateTextCatalog.ps1",
    ):
        path = localization / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"fixture {relative}\n", encoding="utf-8")
    (localization / "catalog" / "NF's Plugins-Filter" / "Alpha.json").write_text(
        '{"schemaVersion":1,"translations":{},"bindings":[]}\n', encoding="utf-8"
    )

    source = root / "Alpha"
    win = source / "Win"
    win.mkdir(parents=True)
    (source / "Alpha.h").write_text("#pragma once\n", encoding="utf-8")
    (source / "Alpha.cpp").write_text("int alpha;\n", encoding="utf-8")
    (source / "Fs_Target.h").write_text(
        '#define FS_CATEGORY "NF\'s Plugins-Filter"\n', encoding="utf-8"
    )
    (source / "AlphaPiPL.r").write_text(
        '#include "Fs_Target.h"\nCategory { FS_CATEGORY }\n', encoding="utf-8"
    )
    project = win / "Alpha.vcxproj"
    if migrated:
        localization_project_items = """    <ClInclude Include="..\\..\\_localization\\AeText.h" />
    <ClCompile Include="..\\..\\_localization\\core\\AeTextClient.cpp" />
    <None Include="..\\..\\_localization\\catalog\\NF's Plugins-Filter\\Alpha.json" />"""
        localization_filter_items = """    <ClInclude Include="..\\..\\_localization\\AeText.h">
      <Filter>Localization</Filter>
    </ClInclude>
    <ClCompile Include="..\\..\\_localization\\core\\AeTextClient.cpp">
      <Filter>Localization</Filter>
    </ClCompile>
    <None Include="..\\..\\_localization\\catalog\\NF's Plugins-Filter\\Alpha.json">
      <Filter>Localization</Filter>
    </None>"""
        filter_definitions = """    <Filter Include="Localization">
      <UniqueIdentifier>{b0b2d5bd-931f-4ad9-a4e4-b5f3a0cc2df9}</UniqueIdentifier>
    </Filter>"""
    else:
        localization_project_items = """    <ClInclude
      Include="..\\..\\_localization\\CatalogView.h" />
    <ClInclude Include="..\\..\\_localization\\EffectText.h" />
    <ClInclude Include="..\\..\\_localization\\TextSuite.h" />
    <ClCompile Include="..\\..\\_localization\\EffectText.cpp" />
    <None Include="..\\..\\_localization\\catalog\\NF's Plugins-Filter\\Alpha.json" />
    <None Include="..\\..\\_localization\\GenerateTextCatalog.ps1" />"""
        localization_filter_items = """    <ClInclude
      Include="..\\..\\_localization\\CatalogView.h">
      <Filter>Localization</Filter>
    </ClInclude>
    <ClInclude Include="..\\..\\_localization\\EffectText.h">
      <Filter>Localization</Filter>
    </ClInclude>
    <ClInclude Include="..\\..\\_localization\\TextSuite.h">
      <Filter>Localization</Filter>
    </ClInclude>
    <ClCompile Include="..\\..\\_localization\\EffectText.cpp">
      <Filter>Localization</Filter>
    </ClCompile>
    <None Include="..\\..\\_localization\\catalog\\NF's Plugins-Filter\\Alpha.json">
      <Filter>Localization\\Catalog\\NF's Plugins-Filter</Filter>
    </None>
    <None Include="..\\..\\_localization\\GenerateTextCatalog.ps1">
      <Filter>Localization</Filter>
    </None>"""
        filter_definitions = """    <Filter Include="Localization">
      <UniqueIdentifier>{D8EAB30F-5724-479B-8684-65D55E931371}</UniqueIdentifier>
    </Filter>
    <Filter Include="Localization\\Catalog">
      <UniqueIdentifier>{A9C64B39-4F89-47E1-A143-A40C2D682A61}</UniqueIdentifier>
    </Filter>
    <Filter Include="Localization\\Catalog\\NF's Plugins-Filter">
      <UniqueIdentifier>{BBDFCE4E-48C4-4973-A11F-1EC5F39E3809}</UniqueIdentifier>
    </Filter>"""

    project.write_text(
        f"""<?xml version="1.0" encoding="utf-8"?>
<Project xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <ItemGroup>
    <ClInclude Include="..\\Alpha.h" />
    <ClCompile Include="..\\Alpha.cpp">
      <Optimization>Disabled</Optimization>
    </ClCompile>
    <CustomBuild Include="..\\AlphaPiPL.r" />
{localization_project_items}
  </ItemGroup>
</Project>
""",
        encoding="utf-8",
    )
    project.with_suffix(project.suffix + ".filters").write_text(
        f"""<?xml version="1.0" encoding="utf-8"?>
<Project xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <ItemGroup>
    <Filter Include="Header Files">
      <UniqueIdentifier>{{11111111-1111-1111-1111-111111111111}}</UniqueIdentifier>
    </Filter>
{filter_definitions}
  </ItemGroup>
  <ItemGroup>
    <ClInclude Include="..\\Alpha.h">
      <Filter>Header Files</Filter>
    </ClInclude>
    <ClCompile Include="..\\Alpha.cpp" />
{localization_filter_items}
  </ItemGroup>
</Project>
""",
        encoding="utf-8",
    )
    (root / "F's PluginsProjects.slnx").write_text(
        """<Solution>
  <Configurations><Platform Name="x64" /></Configurations>
  <Folder Name="/Old/"><Project Path="Alpha/Win/Alpha.vcxproj" /></Folder>
</Solution>
""",
        encoding="utf-8",
    )
    apply_classification_plan(build_classification_plan(root))
    assert not build_classification_plan(root).changed
    return project


def _includes(path: Path, kind: str) -> list[str]:
    root = ET.parse(path).getroot()
    return [
        element.attrib["Include"]
        for element in root.iter()
        if _local_name(element.tag) == kind and "Include" in element.attrib
    ]


def _raw_text(path: Path) -> str:
    return path.read_bytes().decode("utf-8-sig")


def test_migrated_oracle_is_exactly_idempotent(tmp_path: Path) -> None:
    project = _fixture(tmp_path, migrated=True)

    plan = build_project_view_plan(tmp_path, "Alpha")

    assert not plan.changed
    assert plan.changes == ()
    assert plan.project_text == _raw_text(project)
    assert plan.filters_text == _raw_text(project.with_suffix(".vcxproj.filters"))


def test_legacy_view_is_rewritten_surgically_and_second_run_has_no_diff(
    tmp_path: Path,
) -> None:
    project = _fixture(tmp_path, migrated=False)
    original = project.read_text(encoding="utf-8")
    business_block = """    <ClCompile Include="..\\Alpha.cpp">
      <Optimization>Disabled</Optimization>
    </ClCompile>"""
    assert business_block in original

    plan = build_project_view_plan(tmp_path, "Alpha")

    assert plan.changed
    assert "remove legacy localization project items" in plan.changes
    apply_project_view_plan(plan)
    assert business_block in project.read_text(encoding="utf-8")
    assert _includes(project, "ClInclude").count("..\\..\\_localization\\AeText.h") == 1
    assert (
        _includes(project, "ClCompile").count("..\\..\\_localization\\core\\AeTextClient.cpp") == 1
    )
    assert _includes(project, "None") == [
        "..\\..\\_localization\\catalog\\NF's Plugins-Filter\\Alpha.json"
    ]
    filters = project.with_suffix(".vcxproj.filters")
    localization_filters = [
        value
        for value in _includes(filters, "Filter")
        if value == "Localization" or value.startswith("Localization\\")
    ]
    assert localization_filters == ["Localization"]
    filter_root = ET.parse(filters).getroot()
    managed_filter_values = []
    for element in filter_root.iter():
        include = element.attrib.get("Include", "")
        if "_localization" not in include:
            continue
        managed_filter_values.extend(
            child.text for child in element if _local_name(child.tag) == "Filter"
        )
    assert managed_filter_values == ["Localization", "Localization", "Localization"]

    applied_project = _raw_text(project)
    applied_filters = _raw_text(filters)
    second = build_project_view_plan(tmp_path, "Alpha")
    assert not second.changed
    assert second.project_text == applied_project
    assert second.filters_text == applied_filters


def test_legacy_view_accepts_a_standalone_carriage_return_between_items(
    tmp_path: Path,
) -> None:
    project = _fixture(tmp_path, migrated=False)
    data = project.read_bytes()
    marker = b'    <ClInclude Include="..\\Alpha.h" />'
    line_ending = b"\r\n" if marker + b"\r\n" in data else b"\n"
    assert marker + line_ending in data
    replacement = marker + b"\r  </ItemGroup>" + line_ending + b"  <ItemGroup>" + line_ending
    project.write_bytes(data.replace(marker + line_ending, replacement, 1))

    plan = build_project_view_plan(tmp_path, "Alpha")
    apply_project_view_plan(plan)

    assert _includes(project, "ClInclude").count("..\\..\\_localization\\AeText.h") == 1
    second = build_project_view_plan(tmp_path, "Alpha")
    assert not second.changed


def test_duplicate_or_wrong_managed_paths_are_rejected(tmp_path: Path) -> None:
    project = _fixture(tmp_path, migrated=True)
    text = project.read_text(encoding="utf-8")
    project.write_text(
        text.replace(
            '    <ClInclude Include="..\\..\\_localization\\AeText.h" />',
            '    <ClInclude Include="..\\..\\_localization\\AeText.h" />\n'
            '    <ClInclude Include="..\\..\\_localization\\AeText.h" />',
        ),
        encoding="utf-8",
    )
    with pytest.raises(ProjectViewError, match="duplicate managed project item"):
        build_project_view_plan(tmp_path, "Alpha")

    project = _fixture(tmp_path / "wrong", migrated=True)
    text = project.read_text(encoding="utf-8")
    project.write_text(
        text.replace("..\\..\\_localization\\AeText.h", "..\\not-localization\\AeText.h", 1),
        encoding="utf-8",
    )
    with pytest.raises(ProjectViewError, match="managed filename uses an unexpected path"):
        build_project_view_plan(tmp_path / "wrong", "Alpha")


def test_unrelated_item_in_localization_filter_is_rejected(tmp_path: Path) -> None:
    project = _fixture(tmp_path, migrated=True)
    filters = project.with_suffix(".vcxproj.filters")
    text = filters.read_text(encoding="utf-8")
    filters.write_text(
        text.replace(
            '    <ClCompile Include="..\\Alpha.cpp" />',
            '    <ClCompile Include="..\\Alpha.cpp">\n'
            "      <Filter>Localization</Filter>\n"
            "    </ClCompile>",
        ),
        encoding="utf-8",
    )

    with pytest.raises(ProjectViewError, match="unrelated item uses the Localization filter"):
        build_project_view_plan(tmp_path, "Alpha")
