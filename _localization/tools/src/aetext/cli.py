"""Command-line entry points for the bounded AeText tooling."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

from .catalog.formatting import format_catalog_json
from .classification import (
    ClassificationError,
    apply_classification_plan,
    build_classification_plan,
    check_project_classification,
)
from .inventory import build_inventory, render_markdown
from .legacy_retirement import assess_legacy_retirement
from .migration import (
    apply_legacy_migration,
    compare_legacy_baseline,
    materialize_legacy_migration,
    plan_legacy_migration,
)
from .project_view import (
    ProjectViewError,
    apply_project_view_plan,
    build_project_view_plan,
)
from .scanner import scan_sources
from .schema import flatten_role_sections, synchronize_effect_catalog


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=path.name + ".tmp.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as output:
            json.dump(value, output, ensure_ascii=False, indent=2)
            output.write("\n")
        os.replace(temporary, path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def _write_text(path: Path, value: str) -> None:
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


def _write_catalog_json(path: Path, value: object) -> None:
    _write_text(path, format_catalog_json(value))


def _scan(arguments: argparse.Namespace) -> int:
    source_list = Path(arguments.source_list)
    paths = [
        line.strip()
        for line in source_list.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    report = scan_sources(paths, project_root=Path(arguments.project_root))
    _write_json(Path(arguments.output), report)
    for diagnostic in report["diagnostics"]:
        print(
            f"{diagnostic['path']}({diagnostic['line']},{diagnostic['column']}): "
            f"{diagnostic['severity']} {diagnostic['code']}: {diagnostic['message']}",
            file=sys.stderr,
        )
    return 1 if any(item["severity"] == "error" for item in report["diagnostics"]) else 0


def _source_paths(source_list: str) -> list[str]:
    return [
        line.strip()
        for line in Path(source_list).read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]


def _migrate(arguments: argparse.Namespace) -> int:
    catalog_path = Path(arguments.catalog)
    catalog_bytes = catalog_path.read_bytes()
    catalog = json.loads(catalog_bytes.decode("utf-8-sig"))
    family = json.loads(Path(arguments.family).read_text(encoding="utf-8-sig"))
    paths = _source_paths(arguments.source_list)
    report = plan_legacy_migration(
        catalog,
        paths,
        namespace=arguments.namespace,
        project_root=arguments.project_root,
    )
    report["catalogSha256"] = hashlib.sha256(catalog_bytes).hexdigest().upper()
    if arguments.apply:
        if not arguments.equivalence_report:
            raise ValueError("--apply requires --equivalence-report")
        equivalence = json.loads(Path(arguments.equivalence_report).read_text(encoding="utf-8-sig"))
        report["applied"] = apply_legacy_migration(
            catalog_path,
            paths,
            namespace=arguments.namespace,
            project_root=arguments.project_root,
            equivalence_report=equivalence,
        )
    if arguments.prospective_directory and report["readyForByteComparison"]:
        report["prospectiveWorkspace"] = materialize_legacy_migration(
            catalog,
            family,
            paths,
            namespace=arguments.namespace,
            project_root=arguments.project_root,
            destination=arguments.prospective_directory,
        )
    _write_json(Path(arguments.output), report)
    return 0 if report["readyForByteComparison"] else 1


def _compare(arguments: argparse.Namespace) -> int:
    def load(path: str) -> object:
        return json.loads(Path(path).read_text(encoding="utf-8-sig"))

    baseline = load(arguments.baseline)
    generated = load(arguments.generated_bytes)
    bindings = load(arguments.generated_bindings)
    migration = load(arguments.migration_report)
    legacy_catalog = load(arguments.legacy_catalog)
    prospective_catalog = load(arguments.prospective_catalog)
    comparison = compare_legacy_baseline(baseline, generated)

    expected_indices: dict[tuple[str, str], int] = {}
    if isinstance(baseline, dict):
        baseline_bindings = baseline.get("bindings", {})
        if isinstance(baseline_bindings, dict):
            next_role_index: dict[str, int] = {}
            for entry in baseline_bindings.get("entries", []):
                if isinstance(entry, dict):
                    role = str(entry["role"])
                    legacy_index = int(entry.get("legacyIndex", next_role_index.get(role, 0)))
                    expected_indices[(role, str(entry["stableId"]))] = legacy_index
                    next_role_index[role] = legacy_index + 1
    actual_indices: dict[tuple[str, str], int] = {}
    if isinstance(bindings, dict):
        for entry in bindings.get("bindings", []):
            if isinstance(entry, dict):
                actual_indices[(str(entry["role"]), str(entry["stableId"]))] = int(entry["index"])
    index_changes = [
        {
            "role": role,
            "stableId": stable_id,
            "legacyIndex": expected,
            "derivedIndex": actual_indices[(role, stable_id)],
        }
        for (role, stable_id), expected in sorted(expected_indices.items())
        if (role, stable_id) in actual_indices and actual_indices[(role, stable_id)] != expected
    ]

    migration_legacy = migration.get("legacy", {}) if isinstance(migration, dict) else {}
    migration_prospective = migration.get("prospective", {}) if isinstance(migration, dict) else {}
    migration_api_edits = migration.get("apiEditCounts", {}) if isinstance(migration, dict) else {}
    migration_unrewritten = (
        migration.get("unrewrittenLegacyCalls", []) if isinstance(migration, dict) else []
    )
    generated_calls = bindings.get("calls", []) if isinstance(bindings, dict) else []
    generated_bindings = bindings.get("bindings", []) if isinstance(bindings, dict) else []
    old_translations = (
        legacy_catalog.get("translations") if isinstance(legacy_catalog, dict) else None
    )
    new_translations = (
        prospective_catalog.get("translations") if isinstance(prospective_catalog, dict) else None
    )
    translation_changes: list[dict[str, object]] = []
    explicit_source_selections: list[dict[str, str]] = []
    if isinstance(old_translations, dict) and isinstance(new_translations, dict):
        for locale in sorted(set(old_translations) | set(new_translations)):
            old_map = old_translations.get(locale)
            new_map = new_translations.get(locale)
            if not isinstance(old_map, dict) or not isinstance(new_map, dict):
                translation_changes.append(
                    {"locale": locale, "expected": old_map, "actual": new_map}
                )
                continue
            try:
                new_map = flatten_role_sections(new_map)
            except ValueError:
                translation_changes.append(
                    {"locale": locale, "expected": old_map, "actual": new_map}
                )
                continue
            for stable_id in sorted(set(old_map) | set(new_map)):
                if stable_id not in old_map:
                    value = new_map[stable_id]
                    if value == {"useSource": True}:
                        explicit_source_selections.append({"locale": locale, "stableId": stable_id})
                    else:
                        translation_changes.append(
                            {
                                "locale": locale,
                                "stableId": stable_id,
                                "expected": None,
                                "actual": value,
                            }
                        )
                elif stable_id not in new_map or old_map[stable_id] != new_map[stable_id]:
                    translation_changes.append(
                        {
                            "locale": locale,
                            "stableId": stable_id,
                            "expected": old_map[stable_id],
                            "actual": new_map.get(stable_id),
                        }
                    )
    elif old_translations != new_translations:
        translation_changes.append({"expected": old_translations, "actual": new_translations})

    result = {
        "schemaVersion": 1,
        "oldUniqueBindingCount": migration_legacy.get("bindingCount"),
        "migratedCallCount": migration_legacy.get("callCount"),
        "plannedBindingCount": migration_prospective.get("bindingCount"),
        "plannedCallCount": migration_prospective.get("callCount"),
        "scannedUniqueBindingCount": len(generated_bindings),
        "scannedCallCount": len(generated_calls),
        **comparison,
        "apiEditCounts": migration_api_edits,
        "unrewrittenLegacyCalls": migration_unrewritten,
        "translationChanges": translation_changes,
        "explicitSourceSelectionsAdded": explicit_source_selections,
        "indexChanges": index_changes,
        "indexChangePolicy": "informational: approved Role + stable-ID ASCII ordinal ordering",
        "catalogSha256": migration.get("catalogSha256"),
        "editedInputSha256": migration.get("editedInputSha256"),
        "reviewLayout": bindings.get("reviewLayout") if isinstance(bindings, dict) else None,
        "generatedBindings": generated_bindings,
    }
    counts_match = (
        result["oldUniqueBindingCount"] == result["scannedUniqueBindingCount"]
        and result["migratedCallCount"] == result["scannedCallCount"]
    )
    result["readyForBindingRemoval"] = bool(
        comparison["ok"]
        and counts_match
        and not translation_changes
        and not result["unrewrittenLegacyCalls"]
    )
    _write_json(Path(arguments.output), result)
    return 0 if result["readyForBindingRemoval"] else 1


def _inventory(arguments: argparse.Namespace) -> int:
    manifests = sorted(Path(arguments.manifest_directory).glob("*.txt"))
    report = build_inventory(manifests, arguments.project_root)
    _write_json(Path(arguments.output), report)
    if arguments.markdown_output:
        _write_text(Path(arguments.markdown_output), render_markdown(report))
    return 0


def _sync(arguments: argparse.Namespace) -> int:
    catalog_path = Path(arguments.catalog)
    catalog = json.loads(catalog_path.read_text(encoding="utf-8-sig"))
    family = json.loads(Path(arguments.family).read_text(encoding="utf-8-sig"))
    binding_report = json.loads(Path(arguments.bindings).read_text(encoding="utf-8-sig"))
    bindings = binding_report.get("bindings") if isinstance(binding_report, dict) else None
    review_layout = binding_report.get("reviewLayout") if isinstance(binding_report, dict) else None
    result = synchronize_effect_catalog(
        catalog,
        family,
        bindings,
        prune=arguments.prune,
        review_layout=review_layout,
    )
    errors = [
        item
        for item in result["diagnostics"]
        if isinstance(item, dict) and item.get("severity") == "error"
    ]
    changed = result["catalog"] != catalog
    report = {key: value for key, value in result.items() if key != "catalog"}
    report["changed"] = changed
    report["wroteCatalog"] = bool(arguments.write and changed and not errors)
    _write_json(Path(arguments.output), report)
    if arguments.write and changed and not errors:
        _write_catalog_json(catalog_path, result["catalog"])
    return 1 if errors else 0


def _review(arguments: argparse.Namespace) -> int:
    from .catalog.review import ReviewWorkspaceService
    from .core.projects import repository_root
    from .web import run_review

    root = repository_root()
    service = ReviewWorkspaceService(root)
    run_review(
        service,
        arguments.plugin,
        locale=arguments.locale,
        port=arguments.port,
        show_browser=not arguments.no_browser,
    )
    return 0


def _classification_root(value: str | None) -> Path:
    if value:
        return Path(value).resolve()
    from .core.projects import repository_root

    return repository_root()


def _sync_classification(arguments: argparse.Namespace) -> int:
    root = _classification_root(arguments.repository)
    try:
        plan = build_classification_plan(root)
        report = {
            "projectCount": len(plan.projects),
            "changed": plan.changed,
            "pluginMapChanged": plan.plugin_map_changed,
            "solutionChanged": plan.solution_changed,
            "catalogMoves": [
                {
                    "from": source.relative_to(root).as_posix(),
                    "to": destination.relative_to(root).as_posix(),
                }
                for source, destination in plan.catalog_moves
            ],
            "applied": bool(arguments.apply and plan.changed),
        }
        if arguments.apply and plan.changed:
            apply_classification_plan(plan)
            verification = build_classification_plan(root)
            if verification.changed:
                raise ClassificationError("classification apply was not idempotent")
        if arguments.output:
            _write_json(Path(arguments.output), report)
        print(json.dumps(report, ensure_ascii=False, separators=(",", ":")))
        return 1 if plan.changed and not arguments.apply else 0
    except ClassificationError as error:
        print(f"classification error: {error}", file=sys.stderr)
        return 2


def _check_classification(arguments: argparse.Namespace) -> int:
    try:
        classification = check_project_classification(
            _classification_root(arguments.repository), arguments.project
        )
        print(
            f"classification current: {classification.name} | {classification.role} | "
            f"{classification.category or 'not-applicable'}"
        )
        return 0
    except ClassificationError as error:
        print(f"classification error: {error}", file=sys.stderr)
        return 2


def _check_legacy_retirement(arguments: argparse.Namespace) -> int:
    root = _classification_root(arguments.repository)
    report = assess_legacy_retirement(root)
    value = {
        "ready": report.ready,
        "effectCatalogCount": report.effect_catalog_count,
        "legacyCatalogCount": len(report.legacy_catalogs),
        "legacyCatalogs": report.legacy_catalogs,
        "currentTargetLegacyCatalogCount": len(report.current_target_legacy_catalogs),
        "currentTargetLegacyCatalogs": report.current_target_legacy_catalogs,
        "deferredLegacyCatalogCount": len(report.deferred_legacy_catalogs),
        "deferredLegacyCatalogs": report.deferred_legacy_catalogs,
        "sourceDerivedCatalogCount": len(report.source_derived_catalogs),
        "sourceDerivedCatalogs": report.source_derived_catalogs,
        "invalidCatalogs": report.invalid_catalogs,
        "removePaths": list(report.remove_paths),
        "removeSymbols": list(report.remove_symbols),
    }
    if arguments.output:
        _write_json(Path(arguments.output), value)
    print(json.dumps(value, ensure_ascii=False, separators=(",", ":")))
    return 0 if report.ready else 1


def _sync_project_view(arguments: argparse.Namespace) -> int:
    root = _classification_root(arguments.repository)
    try:
        plan = build_project_view_plan(root, arguments.project)
        report = {
            "project": plan.project_path.relative_to(root).as_posix(),
            "filters": plan.filters_path.relative_to(root).as_posix(),
            "catalog": plan.catalog_path.relative_to(root).as_posix(),
            "changed": plan.changed,
            "changes": list(plan.changes),
            "applied": bool(arguments.apply and plan.changed),
        }
        if arguments.apply and plan.changed:
            apply_project_view_plan(plan)
            verification = build_project_view_plan(root, arguments.project)
            if verification.changed:
                raise ProjectViewError("sync-project-view apply was not idempotent")
        if arguments.output:
            _write_json(Path(arguments.output), report)
        print(json.dumps(report, ensure_ascii=False, separators=(",", ":")))
        return 1 if plan.changed and not arguments.apply else 0
    except ProjectViewError as error:
        print(f"project-view error: {error}", file=sys.stderr)
        return 2


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m aetext.cli")
    commands = parser.add_subparsers(dest="command", required=True)
    scan = commands.add_parser("scan", help="scan explicit C/C++ project inputs")
    scan.add_argument("--source-list", required=True)
    scan.add_argument("--project-root", required=True)
    scan.add_argument("--output", required=True)
    scan.set_defaults(handler=_scan)
    migrate = commands.add_parser(
        "migrate", help="plan a legacy migration without editing product files"
    )
    migrate.add_argument("--catalog", required=True)
    migrate.add_argument("--source-list", required=True)
    migrate.add_argument("--family", required=True)
    migrate.add_argument("--namespace", required=True)
    migrate.add_argument("--project-root", required=True)
    migrate.add_argument("--output", required=True)
    migrate.add_argument("--prospective-directory")
    migrate.add_argument("--apply", action="store_true")
    migrate.add_argument("--equivalence-report")
    migrate.set_defaults(handler=_migrate)
    compare = commands.add_parser(
        "compare", help="compare a prospective generated catalog with its legacy oracle"
    )
    compare.add_argument("--baseline", required=True)
    compare.add_argument("--generated-bytes", required=True)
    compare.add_argument("--generated-bindings", required=True)
    compare.add_argument("--migration-report", required=True)
    compare.add_argument("--legacy-catalog", required=True)
    compare.add_argument("--prospective-catalog", required=True)
    compare.add_argument("--output", required=True)
    compare.set_defaults(handler=_compare)
    inventory = commands.add_parser(
        "inventory", help="summarize evaluated projects without modifying them"
    )
    inventory.add_argument("--manifest-directory", required=True)
    inventory.add_argument("--project-root", required=True)
    inventory.add_argument("--output", required=True)
    inventory.add_argument("--markdown-output")
    inventory.set_defaults(handler=_inventory)
    sync = commands.add_parser(
        "sync", help="preview or explicitly write missing translation placeholders"
    )
    sync.add_argument("--catalog", required=True)
    sync.add_argument("--family", required=True)
    sync.add_argument("--bindings", required=True)
    sync.add_argument("--output", required=True)
    sync.add_argument("--write", action="store_true")
    sync.add_argument("--prune", action="store_true")
    sync.set_defaults(handler=_sync)
    review = commands.add_parser(
        "review", help="open the single localhost browser review interface"
    )
    review.add_argument("plugin", nargs="?")
    review.add_argument("--locale")
    review.add_argument("--port", type=int)
    review.add_argument("--no-browser", action="store_true")
    review.set_defaults(handler=_review)
    classification = commands.add_parser(
        "sync-classification",
        help="preview or apply source-derived repository classification views",
    )
    classification.add_argument("--repository")
    classification.add_argument("--output")
    classification.add_argument("--apply", action="store_true")
    classification.set_defaults(handler=_sync_classification)
    check_classification = commands.add_parser(
        "check-classification", help="validate one project's generated classification views"
    )
    check_classification.add_argument("--repository")
    check_classification.add_argument("--project", required=True)
    check_classification.set_defaults(handler=_check_classification)
    retirement = commands.add_parser(
        "check-legacy-retirement",
        help="report whether the transitional legacy generator path can be removed",
    )
    retirement.add_argument("--repository")
    retirement.add_argument("--output")
    retirement.set_defaults(handler=_check_legacy_retirement)
    project_view = commands.add_parser(
        "sync-project-view",
        help="preview or apply one effect's explicit three-item Localization view",
    )
    project_view.add_argument("--repository")
    project_view.add_argument("--project", required=True)
    project_view.add_argument("--output")
    project_view.add_argument("--apply", action="store_true")
    project_view.set_defaults(handler=_sync_project_view)
    return parser


def main() -> int:
    arguments = _parser().parse_args()
    return int(arguments.handler(arguments))


if __name__ == "__main__":
    raise SystemExit(main())
