"""Command-line entry points for the bounded AeText tooling."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

from .catalog.files import FileWrite, commit_files, content_hash
from .catalog.formatting import format_catalog_json
from .catalog.repository import CatalogConflictError
from .classification import (
    ClassificationError,
    apply_classification_plan,
    build_classification_plan,
    check_project_classification,
)
from .project_view import (
    ProjectViewError,
    apply_project_view_plan,
    build_project_view_plan,
)
from .scanner import scan_sources
from .schema import synchronize_effect_catalog


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


def _sync(arguments: argparse.Namespace) -> int:
    catalog_path = Path(arguments.catalog).resolve()
    catalog_bytes = catalog_path.read_bytes()
    catalog = json.loads(catalog_bytes.decode("utf-8-sig"))
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
        commit_files(
            catalog_path,
            [
                FileWrite(
                    catalog_path,
                    content_hash(catalog_bytes),
                    format_catalog_json(result["catalog"]).encode("utf-8"),
                    CatalogConflictError,
                )
            ],
        )
    return 1 if errors else 0


def _review(arguments: argparse.Namespace) -> int:
    from .catalog.review import ReviewWorkspaceService
    from .core.projects import repository_root
    from .web import run_review

    root = repository_root()
    service = ReviewWorkspaceService(root)
    try:
        run_review(
            service,
            arguments.plugin,
            locale=arguments.locale,
            port=arguments.port,
            show_browser=not arguments.no_browser,
        )
    except KeyboardInterrupt:
        print("AeText review stopped.", flush=True)
    return 0


def _validate_publication_review(arguments: argparse.Namespace) -> int:
    from .catalog import (
        BindingRecord,
        CatalogRepository,
        FamilyDefinition,
        ReviewLayout,
        ReviewStateRepository,
        WorkflowService,
        validate_publication_review,
    )
    from .catalog.publication import validate_settings_publication_review
    from .catalog.settings import SettingsCatalogRepository

    repository_root = Path(arguments.project_root).resolve()
    catalog_path = Path(arguments.catalog).resolve()
    workflow = WorkflowService(repository_root).load()
    review_state = ReviewStateRepository(repository_root).load_for_catalog(catalog_path).document
    if arguments.kind == "Settings":
        catalog = SettingsCatalogRepository(repository_root).load(catalog_path).catalog
        report = validate_settings_publication_review(catalog, workflow, review_state)
    else:
        if not arguments.family or not arguments.source_list:
            raise ValueError("Effect review requires --family and --source-list")
        catalog = CatalogRepository(repository_root).load(catalog_path).catalog
        family = FamilyDefinition.model_validate(
            json.loads(Path(arguments.family).read_text(encoding="utf-8-sig")),
            strict=True,
        )
        scan = scan_sources(
            _source_paths(arguments.source_list),
            project_root=repository_root,
        )
        scan_errors = [item for item in scan["diagnostics"] if item["severity"] == "error"]
        if scan_errors:
            for diagnostic in scan_errors:
                print(
                    f"{diagnostic['path']}({diagnostic['line']},{diagnostic['column']}): "
                    f"error {diagnostic['code']}: {diagnostic['message']}",
                    file=sys.stderr,
                )
            return 1
        bindings = [
            BindingRecord.model_validate(binding, strict=True) for binding in scan["bindings"]
        ]
        layout = ReviewLayout.model_validate(scan["reviewLayout"], strict=True)
        report = validate_publication_review(
            catalog,
            family,
            bindings,
            layout,
            workflow,
            review_state,
        )
    value = report.model_dump(by_alias=True)
    if arguments.output:
        _write_json(Path(arguments.output), value)
    print(json.dumps(value, ensure_ascii=False, separators=(",", ":")))
    for issue in report.issues:
        location = ":".join(value for value in (issue.locale, issue.stable_id) if value is not None)
        prefix = f"{location}: " if location else ""
        print(f"error {issue.code}: {prefix}{issue.message}", file=sys.stderr)
    return 0 if report.valid else 1


def _initialize_review_state(arguments: argparse.Namespace) -> int:
    from .catalog.review import ReviewWorkspaceService

    root = _classification_root(arguments.repository)
    service = ReviewWorkspaceService(root)
    report = service.initialize_review_states(
        completed_locale=arguments.completed_locale,
        pretranslated_locale=arguments.pretranslated_locale,
        apply=arguments.apply,
        expected_project_count=arguments.expected_project_count,
        expected_entry_count=arguments.expected_entry_count,
    )
    print(
        json.dumps(
            report.model_dump(by_alias=True),
            ensure_ascii=False,
            separators=(",", ":"),
        )
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
            "reviewStateMoves": [
                {
                    "from": source.relative_to(root).as_posix(),
                    "to": destination.relative_to(root).as_posix(),
                }
                for source, destination in plan.review_state_moves
            ],
            "projectUpdates": [
                path.relative_to(root).as_posix() for path, _ in plan.project_updates
            ],
            "applied": bool(arguments.apply and plan.changed),
        }
        if arguments.apply and plan.changed:
            apply_classification_plan(plan)
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
    publication_review = commands.add_parser(
        "validate-publication-review",
        help="validate tracked review evidence for one effect or Settings catalog",
    )
    publication_review.add_argument("--catalog", required=True)
    publication_review.add_argument("--kind", choices=("Effect", "Settings"), default="Effect")
    publication_review.add_argument("--family")
    publication_review.add_argument("--source-list")
    publication_review.add_argument("--project-root", required=True)
    publication_review.add_argument("--output")
    publication_review.set_defaults(handler=_validate_publication_review)
    initialize_review = commands.add_parser(
        "initialize-review-state",
        help="fresh-scan and initialize the explicitly certified one-time review baseline",
    )
    initialize_review.add_argument("--repository")
    initialize_review.add_argument("--completed-locale", required=True)
    initialize_review.add_argument("--pretranslated-locale", required=True)
    initialize_review.add_argument("--expected-project-count", type=int)
    initialize_review.add_argument("--expected-entry-count", type=int)
    initialize_review.add_argument("--apply", action="store_true")
    initialize_review.set_defaults(handler=_initialize_review_state)
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
