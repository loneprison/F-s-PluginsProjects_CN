"""Cache-backed multi-project review workspace orchestration."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from ..core.projects import ProjectDiscoveryService
from ..scanner import scan_sources
from .models import (
    BindingRecord,
    EffectCatalog,
    FamilyDefinition,
    TextRole,
    UseSource,
    WorkflowDefinition,
)
from .repository import CatalogRepository, CatalogSnapshot
from .source_index import (
    ReviewLayout,
    ReviewUse,
    SourceSnapshot,
    SourceSnapshotRepository,
)
from .validation import has_errors, validate_catalog_domain
from .workflow import WorkflowService

ProjectRole = Literal["Production", "Templates", "Tests", "Abandoned", "Support"]
CatalogKind = Literal["source-derived", "legacy", "settings", "invalid"]
ScanState = Literal["ready", "unscanned", "error", "legacy", "settings", "invalid"]
ContentStatus = Literal["missing", "use-source", "valid", "error", "unscanned"]

_ROLE_LABELS = {
    "Production": "正式插件",
    "Templates": "模板",
    "Tests": "测试",
    "Abandoned": "已弃用",
    "Support": "支持工具",
}
_ROLE_ORDER = {name: index for index, name in enumerate(_ROLE_LABELS)}


class ReviewValidationError(ValueError):
    def __init__(self, diagnostics: list[dict[str, object]]) -> None:
        super().__init__("catalog review validation failed")
        self.diagnostics = diagnostics


class ReviewUnavailableError(ValueError):
    def __init__(self, project_name: str, scan_state: str) -> None:
        super().__init__(
            f"project is not available for cached review: {project_name}: {scan_state}"
        )
        self.project_name = project_name
        self.scan_state = scan_state


class ReviewRow(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    content_status: ContentStatus
    workflow_stage: str | None
    original: str
    translation: str | None
    use_source: bool
    primary_role: TextRole
    roles: list[TextRole]
    panel_order: int
    stable_id: str
    definition_path: str | None
    definition_line: int | None
    use_count: int
    validation_messages: list[str] = Field(default_factory=list)


class ReviewProgress(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    total: int
    valid: int
    missing: int
    use_source: int
    errors: int
    reviewed: int
    pending_review: int


class ReviewProject(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid", frozen=True)

    name: str
    role: ProjectRole
    role_label: str
    category: str
    category_label: str
    catalog_path: Path
    locales: list[str]
    catalog_kind: CatalogKind
    scan_state: ScanState
    deferred: bool = False
    progress: dict[str, ReviewProgress]

    @property
    def reviewable(self) -> bool:
        return self.catalog_kind == "source-derived" and self.scan_state == "ready"


class ReviewWorkspace(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    projects: list[ReviewProject]
    locales: list[str]
    workflow: WorkflowDefinition


class ReviewSession(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid", frozen=True)

    project: ReviewProject
    family: FamilyDefinition
    workflow: WorkflowDefinition
    snapshot: CatalogSnapshot
    source_snapshot: SourceSnapshot
    locale: str
    rows: list[ReviewRow]
    diagnostics: list[dict[str, object]]


class ScanResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    project: str
    status: Literal["ready", "failed", "cancelled"]
    error: str | None = None


class ScanAllResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    results: list[ScanResult]
    cancelled: bool


class ReviewWorkspaceService:
    def __init__(
        self,
        repository_root: str | Path,
        *,
        discovery: ProjectDiscoveryService | Any | None = None,
        scanner: Callable[..., dict[str, object]] = scan_sources,
    ) -> None:
        self.repository_root = Path(repository_root).resolve()
        self.discovery = discovery or ProjectDiscoveryService(self.repository_root)
        self.scanner = scanner
        self.catalogs = CatalogRepository(self.repository_root)
        self.source_snapshots = SourceSnapshotRepository(self.repository_root)
        self.workflows = WorkflowService(self.repository_root)
        self.family_path = (
            self.repository_root / "_localization" / "families" / "fs" / "generation.json"
        ).resolve()
        self._catalog_snapshots: dict[str, CatalogSnapshot] = {}
        self._source_snapshot_cache: dict[str, SourceSnapshot] = {}
        self.workspace = self.load_workspace()

    @staticmethod
    def _load_family(path: Path) -> FamilyDefinition:
        document = json.loads(path.read_text(encoding="utf-8-sig"))
        return FamilyDefinition.model_validate(document, strict=True)

    @staticmethod
    def _classification(relative: Path) -> tuple[ProjectRole, str, str]:
        parts = relative.parent.parts
        if not parts:
            return "Production", "", ""
        first = parts[0]
        special = {
            "(Templates)": "Templates",
            "(Tests)": "Tests",
            "(Abandoned)": "Abandoned",
            "_Support": "Support",
        }
        if first in special:
            role = special[first]
            return role, "", ""
        prefix = "NF's Plugins-"
        category_parts = [first.removeprefix(prefix), *parts[1:]]
        normalized = [part.strip("(){}") for part in category_parts]
        return "Production", "/".join(category_parts), " / ".join(normalized)

    @staticmethod
    def _raw_locales(document: object) -> list[str]:
        if not isinstance(document, dict):
            return []
        translations = document.get("translations")
        return (
            sorted(str(locale) for locale in translations) if isinstance(translations, dict) else []
        )

    @staticmethod
    def _workflow_map(catalog: EffectCatalog, locale: str) -> dict[str, str]:
        return catalog.flatten_workflow(locale)

    @staticmethod
    def _rows(
        catalog: EffectCatalog,
        locale: str,
        bindings: list[BindingRecord],
        review_layout: ReviewLayout,
        diagnostics: list[dict[str, object]],
        workflow: WorkflowDefinition,
        source_change_pending: set[str],
    ) -> list[ReviewRow]:
        locale_map = catalog.flatten_locale(locale)
        workflow_map = ReviewWorkspaceService._workflow_map(catalog, locale)
        error_ids = {
            str(item.get("stableId"))
            for item in diagnostics
            if item.get("severity") == "error" and item.get("locale") == locale
        }
        messages_by_id: dict[str, list[str]] = {}
        for item in diagnostics:
            if item.get("severity") != "error" or item.get("locale") != locale:
                continue
            stable_id = str(item.get("stableId") or "")
            if stable_id:
                messages_by_id.setdefault(stable_id, []).append(str(item.get("message") or ""))
        bindings_by_id: dict[str, list[BindingRecord]] = {}
        for binding in bindings:
            bindings_by_id.setdefault(binding.stable_id, []).append(binding)
        rows: list[ReviewRow] = []
        for section in review_layout.sections:
            for entry in section.entries:
                stable_bindings = bindings_by_id.get(entry.stable_id, [])
                binding = next(
                    (
                        item
                        for item in stable_bindings
                        if item.role == entry.primary_role and item.disposition == "translated"
                    ),
                    None,
                )
                if binding is None:
                    continue
                value = locale_map.get(binding.stable_id)
                use_source = isinstance(value, UseSource)
                translation = value if isinstance(value, str) else None
                content_status: ContentStatus = (
                    "error"
                    if binding.stable_id in error_ids
                    else "use-source"
                    if use_source
                    else "missing"
                    if value is None
                    else "valid"
                )
                workflow_stage = workflow_map.get(binding.stable_id)
                if binding.stable_id in source_change_pending and workflow_stage is not None:
                    workflow_stage = workflow.source_change.get(workflow_stage, workflow_stage)
                definition = binding.definition
                rows.append(
                    ReviewRow(
                        content_status=content_status,
                        workflow_stage=workflow_stage,
                        original=binding.original or "",
                        translation=translation,
                        use_source=use_source,
                        primary_role=entry.primary_role,
                        roles=entry.roles,
                        panel_order=entry.panel_order,
                        stable_id=binding.stable_id,
                        definition_path=None if definition is None else definition.path,
                        definition_line=None if definition is None else definition.line,
                        use_count=sum(len(item.uses) for item in stable_bindings),
                        validation_messages=messages_by_id.get(binding.stable_id, []),
                    )
                )
        return rows

    @staticmethod
    def _progress(rows: list[ReviewRow], workflow: WorkflowDefinition) -> ReviewProgress:
        completed_stage = workflow.completed_stage_id
        return ReviewProgress(
            total=len(rows),
            valid=sum(row.content_status in {"valid", "use-source"} for row in rows),
            missing=sum(row.content_status == "missing" for row in rows),
            use_source=sum(row.content_status == "use-source" for row in rows),
            errors=sum(row.content_status == "error" for row in rows),
            reviewed=sum(row.workflow_stage == completed_stage for row in rows),
            pending_review=sum(
                row.workflow_stage is not None and row.workflow_stage != completed_stage
                for row in rows
            ),
        )

    def _effect_project(
        self,
        *,
        name: str,
        role: ProjectRole,
        category: str,
        category_label: str,
        path: Path,
        catalog: CatalogSnapshot,
        source: SourceSnapshot | None,
        source_error: bool,
    ) -> ReviewProject:
        progress: dict[str, ReviewProgress] = {}
        scan_state: ScanState = "error" if source_error else "unscanned"
        if source is not None:
            diagnostics = validate_catalog_domain(
                catalog.catalog,
                self.family,
                source.bindings,
                source.review_layout,
            )
            for locale in self.family.translation_locales():
                if locale in catalog.catalog.translations:
                    rows = self._rows(
                        catalog.catalog,
                        locale,
                        source.bindings,
                        source.review_layout,
                        diagnostics,
                        self.workflow,
                        set(source.source_change_pending.get(locale, [])),
                    )
                    progress[locale] = self._progress(rows, self.workflow)
            scan_state = "ready"
        return ReviewProject(
            name=name,
            role=role,
            role_label=_ROLE_LABELS[role],
            category=category,
            category_label=category_label,
            catalog_path=path,
            locales=self.family.translation_locales(),
            catalog_kind="source-derived",
            scan_state=scan_state,
            deferred=False,
            progress=progress,
        )

    def load_workspace(self) -> ReviewWorkspace:
        self.family = self._load_family(self.family_path)
        self.workflow = self.workflows.load()
        self._catalog_snapshots = {}
        self._source_snapshot_cache = {}
        projects: list[ReviewProject] = []
        for path in sorted(self.catalogs.catalog_root.rglob("*.json")):
            relative = path.relative_to(self.catalogs.catalog_root)
            name = "FsLanguageSettings" if path.stem == "Settings" else path.stem
            role, category, category_label = self._classification(relative)
            try:
                document = json.loads(path.read_text(encoding="utf-8-sig"))
            except (OSError, UnicodeError, json.JSONDecodeError):
                projects.append(
                    ReviewProject(
                        name=name,
                        role=role,
                        role_label=_ROLE_LABELS[role],
                        category=category,
                        category_label=category_label,
                        catalog_path=path.resolve(),
                        locales=[],
                        catalog_kind="invalid",
                        scan_state="invalid",
                        deferred=False,
                        progress={},
                    )
                )
                continue
            common = {
                "name": name,
                "role": role,
                "role_label": _ROLE_LABELS[role],
                "category": category,
                "category_label": category_label,
                "catalog_path": path.resolve(),
                "locales": self._raw_locales(document),
                "deferred": False,
                "progress": {},
            }
            if role == "Support":
                projects.append(
                    ReviewProject(**common, catalog_kind="settings", scan_state="settings")
                )
                continue
            if isinstance(document, dict) and "bindings" in document:
                projects.append(ReviewProject(**common, catalog_kind="legacy", scan_state="legacy"))
                continue
            try:
                snapshot = self.catalogs.load(path)
            except (OSError, UnicodeError, json.JSONDecodeError, ValidationError):
                projects.append(
                    ReviewProject(**common, catalog_kind="invalid", scan_state="invalid")
                )
                continue
            key = name.casefold()
            self._catalog_snapshots[key] = snapshot
            source: SourceSnapshot | None = None
            source_error = False
            try:
                source = self.source_snapshots.load(name)
            except (OSError, UnicodeError, json.JSONDecodeError, ValidationError):
                source_error = True
            if source is not None:
                expected_catalog = snapshot.path.relative_to(self.repository_root).as_posix()
                if source.project != name or source.catalog_path != expected_catalog:
                    source = None
                    source_error = True
                else:
                    self._source_snapshot_cache[key] = source
            projects.append(
                self._effect_project(
                    name=name,
                    role=role,
                    category=category,
                    category_label=category_label,
                    path=path.resolve(),
                    catalog=snapshot,
                    source=source,
                    source_error=source_error,
                )
            )
        projects.sort(
            key=lambda project: (
                _ROLE_ORDER[project.role],
                project.category_label.casefold(),
                project.name.casefold(),
            )
        )
        workspace = ReviewWorkspace(
            projects=projects,
            locales=self.family.translation_locales(),
            workflow=self.workflow,
        )
        self.workspace = workspace
        return workspace

    def reload_catalogs(self) -> ReviewWorkspace:
        return self.load_workspace()

    def _project(self, project_name: str) -> ReviewProject:
        matches = [
            project
            for project in self.workspace.projects
            if project.name.casefold() == project_name.casefold()
        ]
        if len(matches) != 1:
            raise ValueError(f"project name is missing or ambiguous: {project_name}")
        return matches[0]

    def _session(self, project: ReviewProject, locale: str) -> ReviewSession:
        key = project.name.casefold()
        catalog = self._catalog_snapshots.get(key)
        source = self._source_snapshot_cache.get(key)
        if catalog is None or source is None or not project.reviewable:
            raise ReviewUnavailableError(project.name, project.scan_state)
        if locale not in self.family.translation_locales():
            raise ValueError(f"locale is not defined by the project family: {locale}")
        if locale not in catalog.catalog.translations:
            raise ValueError(f"catalog is missing selected locale: {locale}")
        diagnostics = validate_catalog_domain(
            catalog.catalog,
            self.family,
            source.bindings,
            source.review_layout,
        )
        return ReviewSession(
            project=project,
            family=self.family,
            workflow=self.workflow,
            snapshot=catalog,
            source_snapshot=source,
            locale=locale,
            rows=self._rows(
                catalog.catalog,
                locale,
                source.bindings,
                source.review_layout,
                diagnostics,
                self.workflow,
                set(source.source_change_pending.get(locale, [])),
            ),
            diagnostics=diagnostics,
        )

    def open_cached_project(self, project_name: str, locale: str | None = None) -> ReviewSession:
        project = self._project(project_name)
        selected_locale = locale or self.workspace.locales[0]
        return self._session(project, selected_locale)

    def switch_locale(self, session: ReviewSession, locale: str) -> ReviewSession:
        return self._session(self._project(session.project.name), locale)

    def _scan(self, project: ReviewProject) -> SourceSnapshot:
        if project.catalog_kind != "source-derived":
            raise ReviewUnavailableError(project.name, project.scan_state)
        manifest = self.discovery.discover(project.name)
        if manifest.catalog_path.resolve() != project.catalog_path.resolve():
            raise ValueError("scanned project catalog does not match workspace catalog")
        report = self.scanner(manifest.inputs, project_root=self.repository_root)
        diagnostics = list(report["diagnostics"])
        if has_errors(diagnostics):
            raise ReviewValidationError(diagnostics)
        bindings = [
            BindingRecord.model_validate(binding, strict=True) for binding in report["bindings"]
        ]
        review_uses = [ReviewUse.model_validate(call, strict=True) for call in report["calls"]]
        review_layout = ReviewLayout.model_validate(report["reviewLayout"], strict=True)
        if not bindings:
            raise ValueError(f"source scan produced no bindings: {project.name}")
        previous = self._source_snapshot_cache.get(project.name.casefold())
        previous_originals = (
            {binding.stable_id: binding.original for binding in previous.bindings}
            if previous is not None
            else {}
        )
        changed_ids = {
            binding.stable_id
            for binding in bindings
            if binding.stable_id in previous_originals
            and previous_originals[binding.stable_id] != binding.original
        }
        previous_pending = {} if previous is None else previous.source_change_pending
        pending = {
            locale: sorted(set(previous_pending.get(locale, [])) | changed_ids)
            for locale in self.family.translation_locales()
            if previous_pending.get(locale) or changed_ids
        }
        return self.source_snapshots.save(
            manifest,
            bindings,
            review_uses,
            review_layout,
            diagnostics,
            source_change_pending=pending,
        )

    def _replace_project(self, project: ReviewProject) -> None:
        self.workspace = self.workspace.model_copy(
            update={
                "projects": [
                    project if item.name.casefold() == project.name.casefold() else item
                    for item in self.workspace.projects
                ]
            }
        )

    def _refresh_effect_project(self, project_name: str) -> ReviewProject:
        current = self._project(project_name)
        key = current.name.casefold()
        refreshed = self._effect_project(
            name=current.name,
            role=current.role,
            category=current.category,
            category_label=current.category_label,
            path=current.catalog_path,
            catalog=self._catalog_snapshots[key],
            source=self._source_snapshot_cache.get(key),
            source_error=False,
        )
        self._replace_project(refreshed)
        return refreshed

    def scan_project(self, project_name: str, locale: str | None = None) -> ReviewSession:
        project = self._project(project_name)
        source = self._scan(project)
        self._source_snapshot_cache[project.name.casefold()] = source
        refreshed = self._refresh_effect_project(project.name)
        return self._session(refreshed, locale or self.workspace.locales[0])

    def scan_all(
        self,
        *,
        progress: Callable[[int, int, ScanResult], None] | None = None,
        cancelled: Callable[[], bool] | None = None,
    ) -> ScanAllResult:
        candidates = [
            project
            for project in self.workspace.projects
            if project.catalog_kind == "source-derived"
        ]
        results: list[ScanResult] = []
        was_cancelled = False
        for index, project in enumerate(candidates, start=1):
            if cancelled is not None and cancelled():
                was_cancelled = True
                results.append(ScanResult(project=project.name, status="cancelled"))
                break
            try:
                source = self._scan(project)
                self._source_snapshot_cache[project.name.casefold()] = source
                self._refresh_effect_project(project.name)
                result = ScanResult(project=project.name, status="ready")
            except Exception as error:
                result = ScanResult(project=project.name, status="failed", error=str(error))
            results.append(result)
            if progress is not None:
                progress(index, len(candidates), result)
        return ScanAllResult(results=results, cancelled=was_cancelled)

    @staticmethod
    def _translation_value(value: object, use_source: bool) -> object:
        if use_source:
            return {"useSource": True}
        if value is None:
            return None
        if not isinstance(value, str) or not value:
            raise ValueError("translation must be nonempty or null")
        return value

    @staticmethod
    def _dump_translation(value: object) -> object:
        return value.model_dump(by_alias=True) if isinstance(value, UseSource) else value

    def save_locale(
        self,
        session: ReviewSession,
        rows: list[dict[str, object]],
    ) -> ReviewSession:
        key = session.project.name.casefold()
        current_project = self._project(session.project.name)
        current_catalog = self._catalog_snapshots.get(key)
        current_source = self._source_snapshot_cache.get(key)
        if current_catalog is None or current_source is None or not current_project.reviewable:
            raise ReviewUnavailableError(session.project.name, current_project.scan_state)
        if current_catalog.sha256 != session.snapshot.sha256:
            raise ValueError("workspace catalog snapshot changed while the page was open")
        expected_ids = set(current_source.review_layout.stable_ids())
        submitted_ids = [str(row.get("stable_id")) for row in rows]
        if len(submitted_ids) != len(set(submitted_ids)) or set(submitted_ids) != expected_ids:
            raise ValueError("submitted rows do not exactly match cached translated stable IDs")

        old_locale = current_catalog.catalog.flatten_locale(session.locale)
        old_workflow = self._workflow_map(current_catalog.catalog, session.locale)
        known_stages = {stage.id for stage in self.workflow.stages}
        translations: dict[str, object] = {}
        stages: dict[str, str | None] = {}
        for row in rows:
            stable_id = str(row["stable_id"])
            value = self._translation_value(
                row.get("translation"),
                row.get("use_source") is True,
            )
            translations[stable_id] = value
            stage_value = row.get("workflow_stage")
            stage = None if stage_value in {None, ""} else str(stage_value)
            if stage is not None and stage not in known_stages:
                raise ValueError(f"unknown workflow stage: {stage}")
            changed = self._dump_translation(old_locale.get(stable_id)) != value
            if self.workflow.enabled and changed and stage == old_workflow.get(stable_id):
                stage = self.workflow.defaults.manual_edit
            stages[stable_id] = stage

        ordered_translations = current_source.review_layout.canonicalize(translations)
        ordered_stages = current_source.review_layout.canonicalize(
            {stable_id: stage for stable_id, stage in stages.items() if stage is not None}
        )
        document = current_catalog.catalog.model_dump(by_alias=True, exclude_none=True)
        document["translations"][session.locale] = ordered_translations
        if self.workflow.enabled:
            workflow = document.setdefault("workflow", {})
            if ordered_stages:
                workflow[session.locale] = ordered_stages
            else:
                workflow.pop(session.locale, None)
            if not workflow:
                document.pop("workflow", None)
        candidate = EffectCatalog.model_validate(document, strict=True)
        diagnostics = validate_catalog_domain(
            candidate,
            self.family,
            current_source.bindings,
            current_source.review_layout,
        )
        if has_errors(diagnostics):
            raise ReviewValidationError(diagnostics)
        saved = self.catalogs.save_locale(
            session.snapshot,
            session.locale,
            ordered_translations,
            ordered_stages if self.workflow.enabled else None,
        )
        self._catalog_snapshots[key] = saved
        if self.workflow.enabled:
            current_source = self.source_snapshots.acknowledge_source_changes(
                current_source,
                session.locale,
            )
        self._source_snapshot_cache[key] = current_source
        refreshed = self._refresh_effect_project(session.project.name)
        return self._session(refreshed, session.locale)

    def set_workflow_stage(
        self,
        session: ReviewSession,
        stable_ids: set[str],
        stage: str | None,
    ) -> ReviewSession:
        known = {item.id for item in self.workflow.stages}
        if stage is not None and stage not in known:
            raise ValueError(f"unknown workflow stage: {stage}")
        rows = [
            row.model_copy(update={"workflow_stage": stage}) if row.stable_id in stable_ids else row
            for row in session.rows
        ]
        return session.model_copy(update={"rows": rows})

    def save_workflow_definition(
        self,
        definition: WorkflowDefinition | dict[str, object],
    ) -> WorkflowDefinition:
        validated = (
            definition
            if isinstance(definition, WorkflowDefinition)
            else WorkflowDefinition.model_validate(definition, strict=True)
        )
        used = {
            stage
            for snapshot in self._catalog_snapshots.values()
            if snapshot.catalog.workflow is not None
            for locale_sections in snapshot.catalog.workflow.root.values()
            for role_map in locale_sections.values()
            for stage in role_map.values()
        }
        removed = sorted(used - {stage.id for stage in validated.stages})
        if removed:
            raise ValueError(
                "workflow stages are still referenced; disable them instead of deleting: "
                + ", ".join(removed)
            )
        self.workflow = self.workflows.save(validated)
        self.workspace = self.workspace.model_copy(update={"workflow": self.workflow})
        for project in list(self.workspace.projects):
            if project.catalog_kind == "source-derived":
                self._refresh_effect_project(project.name)
        return self.workflow
