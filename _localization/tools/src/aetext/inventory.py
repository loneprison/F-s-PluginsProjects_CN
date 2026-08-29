"""Read-only repository migration inventory from evaluated MSBuild manifests."""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from collections.abc import Iterable
from pathlib import Path

from .build.msbuild_manifest import read_manifest
from .migration import _legacy_bindings, _plan_file_edits
from .scanner import scan_sources

_INTERNAL_NAMES = {
    "catalogview.h",
    "effecttext.h",
    "textsuite.h",
    "effecttext.cpp",
    "generatetextcatalog.ps1",
}


def _relative(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _explicit_localization_items(project_path: Path) -> list[dict[str, str]]:
    root = ET.parse(project_path).getroot()
    result: list[dict[str, str]] = []
    for element in root.iter():
        include = element.attrib.get("Include")
        if not include:
            continue
        normalized = include.replace("/", "\\").lower()
        name = Path(normalized).name.lower()
        localization_item = "_localization\\" in normalized and (
            name in _INTERNAL_NAMES or "\\catalog\\" in normalized
        )
        if localization_item:
            result.append({"itemType": element.tag.rsplit("}", 1)[-1], "include": include})
    return result


def _line_locations(text: str, pattern: re.Pattern[str], path: str) -> list[dict[str, object]]:
    starts = [0]
    starts.extend(index + 1 for index, character in enumerate(text) if character == "\n")
    result: list[dict[str, object]] = []
    for match in pattern.finditer(text):
        offset = match.start()
        line = 1
        for index, start in enumerate(starts):
            if start > offset:
                break
            line = index + 1
        result.append({"path": path, "line": line})
    return result


def build_inventory(
    manifest_paths: Iterable[str | Path], project_root: str | Path
) -> dict[str, object]:
    root = Path(project_root).resolve()
    projects: list[dict[str, object]] = []
    text_cache: dict[Path, str | None] = {}

    def source_text(path: Path) -> str | None:
        if path not in text_cache:
            try:
                text_cache[path] = path.read_text(encoding="utf-8-sig")
            except (OSError, UnicodeError):
                text_cache[path] = None
        return text_cache[path]

    for manifest_path in sorted(Path(path) for path in manifest_paths):
        manifest = read_manifest(manifest_path)
        project_path = manifest.project_path
        catalog_path = manifest.catalog_path
        inputs = manifest.inputs
        namespace = manifest.namespace
        explicit_items = _explicit_localization_items(project_path)

        catalog_state = "missing"
        catalog: object = None
        catalog_error: str | None = None
        if catalog_path.exists():
            try:
                catalog = json.loads(catalog_path.read_text(encoding="utf-8-sig"))
                catalog_state = (
                    "legacy-bindings"
                    if isinstance(catalog, dict) and "bindings" in catalog
                    else "source-derived"
                )
            except (OSError, UnicodeError, json.JSONDecodeError) as error:
                catalog_state = "invalid"
                catalog_error = str(error)

        edits: list[dict[str, object]] = []
        migration_diagnostics: list[dict[str, object]] = []
        binding_roles: set[str] = set()
        if catalog_state == "legacy-bindings":
            bindings, binding_diagnostics = _legacy_bindings(catalog)
            migration_diagnostics.extend(binding_diagnostics)
            binding_roles = {role for role, _ in bindings}
            namespace_marker = namespace + "::"
            for path in inputs:
                text = source_text(path)
                if text is None or namespace_marker not in text:
                    continue
                file_edits, diagnostics = _plan_file_edits(
                    text, _relative(path, root), namespace, bindings
                )
                edits.extend(file_edits)
                migration_diagnostics.extend(diagnostics)
        elif catalog_state == "source-derived":
            scanner = scan_sources(inputs, project_root=root)
            binding_roles = {str(entry["role"]) for entry in scanner["bindings"]}
            migration_diagnostics.extend(scanner["diagnostics"])

        options: list[dict[str, object]] = []
        about_fields: list[dict[str, object]] = []
        do_dialog: list[dict[str, object]] = []
        for path in inputs:
            text = source_text(path)
            if text is None:
                continue
            display = _relative(path, root)
            if "strings.Options" in text:
                options.extend(
                    _line_locations(text, re.compile(r"\bstrings\s*\.\s*Options\s*\("), display)
                )
            if ".script_utf8" in text:
                about_fields.extend(
                    _line_locations(
                        text,
                        re.compile(r"\.\s*script_utf8\b"),
                        display,
                    )
                )
            if "PF_Cmd_DO_DIALOG" in text:
                do_dialog.extend(
                    _line_locations(
                        text,
                        re.compile(r"\bcase\s+PF_Cmd_DO_DIALOG\s*:"),
                        display,
                    )
                )

        edit_paths = sorted({str(edit["path"]) for edit in edits})
        api_paths = sorted({str(item["path"]) for item in options + about_fields})
        files_to_modify = set(edit_paths + api_paths)
        if explicit_items:
            files_to_modify.add(_relative(project_path, root))
        if catalog_state == "legacy-bindings":
            files_to_modify.add(_relative(catalog_path, root))

        popup_topic = bool(binding_roles & {"Popup", "Topic"})
        has_about = "About" in binding_roles or bool(about_fields)
        has_error = "Error" in binding_roles
        has_options = bool(options)
        effect_roles = binding_roles - {"About"}
        only_param_label = bool(effect_roles) and effect_roles <= {"Param", "Label"}
        special = (
            manifest.name == "FsLanguageSettings"
            or catalog_state in ("missing", "invalid")
            or bool(migration_diagnostics)
            or (
                catalog_state == "legacy-bindings"
                and (not do_dialog or ("About" in binding_roles and not about_fields))
            )
        )

        projects.append(
            {
                "name": manifest.name,
                "projectPath": _relative(project_path, root),
                "catalogPath": _relative(catalog_path, root),
                "catalogState": catalog_state,
                "catalogError": catalog_error,
                "role": manifest.role,
                "category": manifest.category,
                "evaluatedInputCount": len(inputs),
                "explicitLocalizationItems": explicit_items,
                "legacyAccessorReplacements": len(edits),
                "legacyAccessorFiles": edit_paths,
                "optionsCalls": options,
                "aboutDualFieldUses": about_fields,
                "doDialogCases": do_dialog,
                "migrationDiagnostics": migration_diagnostics,
                "risk": {
                    "onlyParamLabel": only_param_label,
                    "popupTopic": popup_topic,
                    "about": has_about,
                    "error": has_error,
                    "options": has_options,
                    "doDialog": bool(do_dialog),
                    "specialProjectStructure": special,
                },
                "dryRun": {
                    "filesToModify": sorted(files_to_modify),
                    "projectItemsToRemove": explicit_items,
                    "legacyCallsToReplace": len(edits),
                    "optionsCallsToSeparate": len(options),
                    "aboutFieldUsesToHide": len(about_fields),
                    "changesNonLocalizationContent": False,
                },
            }
        )

    groups = {
        key: [str(project["name"]) for project in projects if project["risk"][key]]
        for key in (
            "onlyParamLabel",
            "popupTopic",
            "about",
            "error",
            "options",
            "doDialog",
            "specialProjectStructure",
        )
    }
    summary = {
        "projectCount": len(projects),
        "catalogMissing": sum(project["catalogState"] == "missing" for project in projects),
        "catalogInvalid": sum(project["catalogState"] == "invalid" for project in projects),
        "legacyCatalogs": sum(project["catalogState"] == "legacy-bindings" for project in projects),
        "sourceDerivedCatalogs": sum(
            project["catalogState"] == "source-derived" for project in projects
        ),
        "projectsWithExplicitLocalizationItems": sum(
            bool(project["explicitLocalizationItems"]) for project in projects
        ),
        "explicitLocalizationItemCount": sum(
            len(project["explicitLocalizationItems"]) for project in projects
        ),
        "legacyAccessorReplacementCount": sum(
            int(project["legacyAccessorReplacements"]) for project in projects
        ),
        "optionsCallCount": sum(len(project["optionsCalls"]) for project in projects),
        "aboutDualFieldUseCount": sum(len(project["aboutDualFieldUses"]) for project in projects),
        "doDialogCaseCount": sum(len(project["doDialogCases"]) for project in projects),
    }
    return {
        "schemaVersion": 1,
        "mode": "dry-run",
        "writesProductFiles": False,
        "sourceSelection": "evaluated MSBuild ClCompile and ClInclude items",
        "summary": summary,
        "riskGroups": groups,
        "projects": projects,
    }


def render_markdown(report: dict[str, object]) -> str:
    summary = report["summary"]
    groups = report["riskGroups"]
    projects = report["projects"]
    assert isinstance(summary, dict)
    assert isinstance(groups, dict)
    assert isinstance(projects, list)
    lines = [
        "# AeText repository migration dry run",
        "",
        (
            "This report is read-only. It was derived from evaluated MSBuild `ClCompile` "
            "and `ClInclude` items and did not modify product files."
        ),
        "",
        "## Summary",
        "",
        f"- Projects: {summary['projectCount']}",
        (
            "- Legacy catalogs / source-derived catalogs: "
            f"{summary['legacyCatalogs']} / {summary['sourceDerivedCatalogs']}"
        ),
        f"- Missing / invalid catalogs: {summary['catalogMissing']} / {summary['catalogInvalid']}",
        (
            "- Projects with explicit localization internals: "
            f"{summary['projectsWithExplicitLocalizationItems']} "
            f"({summary['explicitLocalizationItemCount']} items)"
        ),
        f"- Legacy accessor calls to replace: {summary['legacyAccessorReplacementCount']}",
        f"- `strings.Options()` calls: {summary['optionsCallCount']}",
        f"- Direct About representation field uses: {summary['aboutDualFieldUseCount']}",
        f"- `PF_Cmd_DO_DIALOG` cases: {summary['doDialogCaseCount']}",
        "",
        "## Risk groups",
        "",
    ]
    labels = {
        "onlyParamLabel": "Only Param / Label",
        "popupTopic": "Popup / Topic",
        "about": "About",
        "error": "Error",
        "options": "Options",
        "doDialog": "PF_Cmd_DO_DIALOG",
        "specialProjectStructure": "Special structure / review",
    }
    for key, label in labels.items():
        names = groups[key]
        lines.append(f"### {label} ({len(names)})")
        lines.append("")
        lines.append(", ".join(names) if names else "None")
        lines.append("")

    explicit_names = [
        str(project["name"]) for project in projects if project["explicitLocalizationItems"]
    ]
    lines.extend(
        [
            "## Projects with explicit localization project items",
            "",
            ", ".join(explicit_names) if explicit_names else "None",
            "",
        ]
    )

    lines.extend(["## Projects requiring special review", ""])
    special_names = set(groups["specialProjectStructure"])
    for project in projects:
        if project["name"] not in special_names:
            continue
        lines.append(
            f"- **{project['name']}** — catalog `{project['catalogState']}`, "
            f"diagnostics {len(project['migrationDiagnostics'])}, "
            f"DO_DIALOG {len(project['doDialogCases'])}, Options {len(project['optionsCalls'])}"
        )
    if not special_names:
        lines.append("None")
    lines.extend(
        [
            "",
            "## Write boundary",
            "",
            (
                "No batch migration was executed. A future write run must be separately invoked "
                "with the explicit `-Migrate` switch and must retain the per-project equivalence "
                "gates."
            ),
            "",
        ]
    )
    return "\n".join(lines)
