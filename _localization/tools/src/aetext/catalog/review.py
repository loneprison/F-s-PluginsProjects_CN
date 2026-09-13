"""Cache-backed multi-project review workspace orchestration."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from ..core.projects import ProjectDiscoveryService
from ..scanner import scan_sources
from .files import commit_files, content_hash
from .models import (
    BindingRecord,
    EffectCatalog,
    FamilyDefinition,
    TextRole,
    UseSource,
    WorkflowDefinition,
)
from .publication import (
    PublicationReviewReport,
    validate_publication_review,
    validate_settings_publication_review,
)
from .repository import CatalogConflictError, CatalogRepository, CatalogSnapshot
from .review_state import (
    ReviewBaseline,
    ReviewStateConflictError,
    ReviewStateDocument,
    ReviewStateEntry,
    ReviewStateRepository,
    ReviewStateSnapshot,
    effective_review_state,
    source_fingerprint,
    translation_fingerprint,
)
from .saving import review_entries, submitted_values, workflow_semantics
from .settings import (
    SETTINGS_TRANSLATION_LOCALES,
    SettingsCatalog,
    SettingsCatalogRepository,
    SettingsCatalogSnapshot,
    validate_settings_catalog,
)
from .source_index import (
    ReviewLayout,
    ReviewUse,
    SourceSnapshot,
    SourceSnapshotRepository,
)
from .validation import has_errors, validate_catalog_domain
from .workflow import WorkflowService

ProjectRole = Literal["Production", "Templates", "Tests", "Abandoned", "Support"]
CatalogKind = Literal["source-derived", "settings", "invalid"]
ScanState = Literal["ready", "unscanned", "error", "settings", "invalid"]
ContentStatus = Literal["missing", "use-source", "valid", "error", "unscanned"]
ReviewPanel = Literal["Param", "Label", "Popup", "Topic", "About", "Error", "Settings"]

_ROLE_ORDER = {
    name: index
    for index, name in enumerate(("Production", "Templates", "Tests", "Abandoned", "Support"))
}


class ReviewValidationError(ValueError):
    def __init__(self, diagnostics: list[dict[str, object]]) -> None:
        super().__init__("catalog review validation failed")
        self.diagnostics = diagnostics


class ReviewContextChangedError(ValueError):
    """The source or review rules no longer match what the user saw."""


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
    persisted_workflow_stage: str | None = None
    review_change_reasons: list[str] = Field(default_factory=list)
    workflow_stage_explicit: bool = False
    original: str
    translation: str | None
    use_source: bool
    primary_role: ReviewPanel
    roles: list[TextRole]
    panel_order: int
    stable_id: str
    definition_path: str | None
    definition_line: int | None
    use_count: int
    validation_diagnostics: list[dict[str, object]] = Field(default_factory=list)


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
    category: str
    category_label: str
    catalog_path: Path
    locales: list[str]
    catalog_kind: CatalogKind
    scan_state: ScanState
    progress: dict[str, ReviewProgress]

    @property
    def reviewable(self) -> bool:
        return self.catalog_kind in {"source-derived", "settings"} and self.scan_state == "ready"


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
    snapshot: CatalogSnapshot | SettingsCatalogSnapshot
    review_snapshot: ReviewStateSnapshot
    source_snapshot: SourceSnapshot | None
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


class ReviewInitializationReport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    applied: bool
    project_count: int
    locale_counts: dict[str, int]


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
        self.settings_catalogs = SettingsCatalogRepository(self.repository_root)
        self.review_states = ReviewStateRepository(self.repository_root)
        self.source_snapshots = SourceSnapshotRepository(self.repository_root)
        self.workflows = WorkflowService(self.repository_root)
        self.family_path = (
            self.repository_root / "_localization" / "families" / "fs" / "generation.json"
        ).resolve()
        self._catalog_snapshots: dict[str, CatalogSnapshot] = {}
        self._settings_catalog_snapshots: dict[str, SettingsCatalogSnapshot] = {}
        self._review_state_snapshots: dict[str, ReviewStateSnapshot] = {}
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
    def _rows(
        catalog: EffectCatalog,
        review_state: ReviewStateDocument,
        locale: str,
        bindings: list[BindingRecord],
        review_layout: ReviewLayout,
        diagnostics: list[dict[str, object]],
        workflow: WorkflowDefinition,
    ) -> list[ReviewRow]:
        locale_map = catalog.flatten_locale(locale)
        locale_state = review_state.locales.get(locale)
        review_map = {} if locale_state is None else locale_state.root
        error_ids = {
            str(item.get("stableId"))
            for item in diagnostics
            if item.get("severity") == "error" and item.get("locale") == locale
        }
        diagnostics_by_id: dict[str, list[dict[str, object]]] = {}
        for item in diagnostics:
            if item.get("severity") != "error" or item.get("locale") != locale:
                continue
            stable_id = str(item.get("stableId") or "")
            if stable_id:
                diagnostics_by_id.setdefault(stable_id, []).append(dict(item))
        bindings_by_id: dict[str, list[BindingRecord]] = {}
        for binding in bindings:
            bindings_by_id.setdefault(binding.stable_id, []).append(binding)
        rows: list[ReviewRow] = []
        for section in review_layout.sections:
            for entry in section.entries:
                stable_bindings = bindings_by_id[entry.stable_id]
                binding = next(
                    item
                    for item in stable_bindings
                    if item.role == entry.primary_role and item.disposition == "translated"
                )
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
                review_entry = review_map.get(binding.stable_id)
                source_hash = source_fingerprint(binding.stable_id, binding.original)
                translation_hash = (
                    None
                    if value is None
                    else translation_fingerprint(locale, binding.stable_id, value)
                )
                review = effective_review_state(
                    review_entry,
                    workflow,
                    source_hash,
                    translation_hash,
                )
                definition = binding.definition
                rows.append(
                    ReviewRow(
                        content_status=content_status,
                        workflow_stage=review.effective_stage,
                        persisted_workflow_stage=review.persisted_stage,
                        review_change_reasons=list(review.reasons),
                        original=binding.original,
                        translation=translation,
                        use_source=use_source,
                        primary_role=entry.primary_role,
                        roles=entry.roles,
                        panel_order=entry.panel_order,
                        stable_id=binding.stable_id,
                        definition_path=None if definition is None else definition.path,
                        definition_line=None if definition is None else definition.line,
                        use_count=sum(len(item.uses) for item in stable_bindings),
                        validation_diagnostics=diagnostics_by_id.get(binding.stable_id, []),
                    )
                )
        return rows

    @staticmethod
    def _settings_rows(
        catalog: SettingsCatalog,
        review_state: ReviewStateDocument,
        locale: str,
        workflow: WorkflowDefinition,
    ) -> list[ReviewRow]:
        if locale not in SETTINGS_TRANSLATION_LOCALES:
            raise ValueError(f"unsupported Settings translation locale: {locale}")
        diagnostics = validate_settings_catalog(catalog, locale)
        diagnostics_by_id: dict[str, list[dict[str, object]]] = {}
        for item in diagnostics:
            stable_id = str(item.get("stableId") or "")
            if stable_id:
                diagnostics_by_id.setdefault(stable_id, []).append(dict(item))
        locale_state = review_state.locales.get(locale)
        review_map = {} if locale_state is None else locale_state.root
        rows: list[ReviewRow] = []
        for index, entry in enumerate(catalog.entries):
            value = getattr(entry, locale)
            translation = value if isinstance(value, str) else None
            review = effective_review_state(
                review_map.get(entry.id),
                workflow,
                source_fingerprint(entry.id, entry.zh),
                None if value is None else translation_fingerprint(locale, entry.id, value),
            )
            rows.append(
                ReviewRow(
                    content_status="missing"
                    if value is None
                    else "error"
                    if entry.id in diagnostics_by_id
                    else "use-source"
                    if isinstance(value, UseSource)
                    else "valid",
                    workflow_stage=review.effective_stage,
                    persisted_workflow_stage=review.persisted_stage,
                    review_change_reasons=list(review.reasons),
                    original=entry.zh,
                    translation=translation,
                    use_source=isinstance(value, UseSource),
                    primary_role="Settings",
                    roles=[],
                    panel_order=index,
                    stable_id=entry.id,
                    definition_path=None,
                    definition_line=None,
                    use_count=1,
                    validation_diagnostics=diagnostics_by_id.get(entry.id, []),
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
        review_state: ReviewStateSnapshot,
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
                        review_state.document,
                        locale,
                        source.bindings,
                        source.review_layout,
                        diagnostics,
                        self.workflow,
                    )
                    progress[locale] = self._progress(rows, self.workflow)
            scan_state = "ready"
        return ReviewProject(
            name=name,
            role=role,
            category=category,
            category_label=category_label,
            catalog_path=path,
            locales=self.family.translation_locales(),
            catalog_kind="source-derived",
            scan_state=scan_state,
            progress=progress,
        )

    def _settings_project(
        self,
        *,
        name: str,
        role: ProjectRole,
        category: str,
        category_label: str,
        path: Path,
        catalog: SettingsCatalogSnapshot,
        review_state: ReviewStateSnapshot,
    ) -> ReviewProject:
        progress = {
            locale: self._progress(
                self._settings_rows(
                    catalog.catalog,
                    review_state.document,
                    locale,
                    self.workflow,
                ),
                self.workflow,
            )
            for locale in SETTINGS_TRANSLATION_LOCALES
        }
        return ReviewProject(
            name=name,
            role=role,
            category=category,
            category_label=category_label,
            catalog_path=path,
            locales=list(SETTINGS_TRANSLATION_LOCALES),
            catalog_kind="settings",
            scan_state="ready",
            progress=progress,
        )

    def load_workspace(self) -> ReviewWorkspace:
        self.family = self._load_family(self.family_path)
        self.workflow = self.workflows.load()
        self._catalog_snapshots = {}
        self._settings_catalog_snapshots = {}
        self._review_state_snapshots = {}
        self._source_snapshot_cache = {}
        projects: list[ReviewProject] = []
        for path in sorted(self.catalogs.catalog_root.rglob("*.json")):
            relative = path.relative_to(self.catalogs.catalog_root)
            is_settings = relative == Path("Settings.json")
            name = "FsLanguageSettings" if is_settings else path.stem
            role, category, category_label = (
                ("Support", "", "") if is_settings else self._classification(relative)
            )
            try:
                document = json.loads(path.read_text(encoding="utf-8-sig"))
            except (OSError, UnicodeError, json.JSONDecodeError):
                projects.append(
                    ReviewProject(
                        name=name,
                        role=role,
                        category=category,
                        category_label=category_label,
                        catalog_path=path.resolve(),
                        locales=[],
                        catalog_kind="invalid",
                        scan_state="invalid",
                        progress={},
                    )
                )
                continue
            common = {
                "name": name,
                "role": role,
                "category": category,
                "category_label": category_label,
                "catalog_path": path.resolve(),
                "locales": self._raw_locales(document),
                "progress": {},
            }
            if is_settings:
                try:
                    settings = self.settings_catalogs.load(path)
                    review_state = self.review_states.load_for_catalog(path)
                except (OSError, UnicodeError, json.JSONDecodeError, ValidationError):
                    projects.append(
                        ReviewProject(**common, catalog_kind="invalid", scan_state="invalid")
                    )
                    continue
                key = name.casefold()
                self._settings_catalog_snapshots[key] = settings
                self._review_state_snapshots[key] = review_state
                projects.append(
                    self._settings_project(
                        name=name,
                        role=role,
                        category=category,
                        category_label=category_label,
                        path=path.resolve(),
                        catalog=settings,
                        review_state=review_state,
                    )
                )
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
            try:
                review_state = self.review_states.load_for_catalog(path)
            except (OSError, UnicodeError, json.JSONDecodeError, ValidationError):
                projects.append(
                    ReviewProject(**common, catalog_kind="invalid", scan_state="invalid")
                )
                self._catalog_snapshots.pop(key, None)
                continue
            self._review_state_snapshots[key] = review_state
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
                    review_state=review_state,
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
        locales = self.family.translation_locales()
        locales.extend(locale for locale in SETTINGS_TRANSLATION_LOCALES if locale not in locales)
        workspace = ReviewWorkspace(
            projects=projects,
            locales=locales,
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
        review_state = self._review_state_snapshots.get(key)
        if project.catalog_kind == "settings":
            settings = self._settings_catalog_snapshots.get(key)
            if settings is None or review_state is None or not project.reviewable:
                raise ReviewUnavailableError(project.name, project.scan_state)
            if locale not in project.locales:
                raise ValueError(f"locale is not defined by the Settings catalog: {locale}")
            diagnostics = validate_settings_catalog(settings.catalog, locale)
            return ReviewSession(
                project=project,
                family=self.family,
                workflow=self.workflow,
                snapshot=settings,
                review_snapshot=review_state,
                source_snapshot=None,
                locale=locale,
                rows=self._settings_rows(
                    settings.catalog,
                    review_state.document,
                    locale,
                    self.workflow,
                ),
                diagnostics=diagnostics,
            )
        catalog = self._catalog_snapshots.get(key)
        source = self._source_snapshot_cache.get(key)
        if catalog is None or review_state is None or source is None or not project.reviewable:
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
            review_snapshot=review_state,
            source_snapshot=source,
            locale=locale,
            rows=self._rows(
                catalog.catalog,
                review_state.document,
                locale,
                source.bindings,
                source.review_layout,
                diagnostics,
                self.workflow,
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
        input_hashes = self.source_snapshots.hash_inputs(manifest.inputs)
        report = self.scanner(manifest.inputs, project_root=self.repository_root)
        if input_hashes != self.source_snapshots.hash_inputs(manifest.inputs):
            raise ReviewContextChangedError("source inputs changed during the scan; scan again")
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
        return self.source_snapshots.save(
            manifest,
            bindings,
            review_uses,
            review_layout,
            diagnostics,
            input_hashes,
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
            review_state=self._review_state_snapshots[key],
            source=self._source_snapshot_cache.get(key),
            source_error=False,
        )
        self._replace_project(refreshed)
        return refreshed

    def _refresh_settings_project(self, project_name: str) -> ReviewProject:
        current = self._project(project_name)
        key = current.name.casefold()
        refreshed = self._settings_project(
            name=current.name,
            role=current.role,
            category=current.category,
            category_label=current.category_label,
            path=current.catalog_path,
            catalog=self._settings_catalog_snapshots[key],
            review_state=self._review_state_snapshots[key],
        )
        self._replace_project(refreshed)
        return refreshed

    def scan_project(self, project_name: str, locale: str | None = None) -> ReviewSession:
        project = self._project(project_name)
        source = self._scan(project)
        self._source_snapshot_cache[project.name.casefold()] = source
        refreshed = self._refresh_effect_project(project.name)
        return self._session(refreshed, locale or self.workspace.locales[0])

    def validate_project_publication(self, project_name: str) -> PublicationReviewReport:
        project = self._project(project_name)
        if project.catalog_kind == "settings":
            return validate_settings_publication_review(
                self.settings_catalogs.load(project.catalog_path).catalog,
                self.workflows.load(),
                self.review_states.load_for_catalog(project.catalog_path).document,
            )
        source = self._scan(project)
        key = project.name.casefold()
        self._source_snapshot_cache[key] = source
        self._refresh_effect_project(project.name)
        return validate_publication_review(
            self._catalog_snapshots[key].catalog,
            self.family,
            source.bindings,
            source.review_layout,
            self.workflow,
            self._review_state_snapshots[key].document,
        )

    def initialize_review_states(
        self,
        *,
        completed_locale: str,
        pretranslated_locale: str,
        apply: bool,
        expected_project_count: int | None = None,
        expected_entry_count: int | None = None,
    ) -> ReviewInitializationReport:
        if completed_locale == pretranslated_locale:
            raise ValueError("initial review locales must be distinct")
        family_locales = set(self.family.translation_locales())
        if {completed_locale, pretranslated_locale} - family_locales:
            raise ValueError("initial review locales must belong to the current family")
        pretranslated_stage = self.workflow.defaults.pretranslation
        if pretranslated_stage is None:
            raise ValueError("workflow does not define defaults.pretranslation")
        plans: list[
            tuple[
                str,
                ReviewStateSnapshot,
                SourceSnapshot,
                dict[str, ReviewStateEntry],
                dict[str, ReviewStateEntry],
            ]
        ] = []
        counts = {completed_locale: 0, pretranslated_locale: 0}
        candidates = [
            project
            for project in self.workspace.projects
            if project.catalog_kind == "source-derived"
        ]
        for project in candidates:
            key = project.name.casefold()
            state_snapshot = self._review_state_snapshots[key]
            if state_snapshot.document.locales:
                raise ValueError(
                    f"review-state initialization refuses existing records: {project.name}"
                )
            source = self._scan(project)
            catalog = self._catalog_snapshots[key].catalog
            diagnostics = validate_catalog_domain(
                catalog,
                self.family,
                source.bindings,
                source.review_layout,
                publication=True,
            )
            if has_errors(diagnostics):
                raise ReviewValidationError(diagnostics)
            originals = {
                binding.stable_id: binding.original
                for binding in source.bindings
                if binding.disposition == "translated"
            }
            completed_values = catalog.flatten_locale(completed_locale)
            completed_entries: dict[str, ReviewStateEntry] = {}
            pretranslated_entries: dict[str, ReviewStateEntry] = {}
            for stable_id in source.review_layout.stable_ids():
                completed_value = completed_values.get(stable_id)
                if completed_value is None:
                    raise ValueError(
                        f"completed initialization requires translation: "
                        f"{project.name}:{completed_locale}:{stable_id}"
                    )
                completed_entries[stable_id] = ReviewStateEntry(
                    stage=self.workflow.completed_stage_id,
                    reviewedAgainst=ReviewBaseline(
                        source=source_fingerprint(stable_id, originals[stable_id]),
                        translation=translation_fingerprint(
                            completed_locale,
                            stable_id,
                            completed_value,
                        ),
                    ),
                )
                pretranslated_entries[stable_id] = ReviewStateEntry(stage=pretranslated_stage)
            counts[completed_locale] += len(completed_entries)
            counts[pretranslated_locale] += len(pretranslated_entries)
            plans.append(
                (
                    key,
                    state_snapshot,
                    source,
                    completed_entries,
                    pretranslated_entries,
                )
            )

        if expected_project_count is not None and len(plans) != expected_project_count:
            raise ValueError(
                f"review-state project count mismatch: expected={expected_project_count} "
                f"actual={len(plans)}"
            )
        if expected_entry_count is not None:
            mismatches = {
                locale: count for locale, count in counts.items() if count != expected_entry_count
            }
            if mismatches:
                raise ValueError(
                    f"review-state entry count mismatch: expected={expected_entry_count} "
                    f"actual={mismatches}"
                )
        if apply:
            for key, snapshot, source, completed_entries, pretranslated_entries in plans:
                saved = self.review_states.save_locale(
                    snapshot,
                    completed_locale,
                    completed_entries,
                )
                saved = self.review_states.save_locale(
                    saved,
                    pretranslated_locale,
                    pretranslated_entries,
                )
                self._review_state_snapshots[key] = saved
                self._source_snapshot_cache[key] = source
            for project in candidates:
                self._refresh_effect_project(project.name)
        return ReviewInitializationReport(
            applied=apply,
            project_count=len(plans),
            locale_counts=counts,
        )

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

    def _assert_save_context(self, session: ReviewSession) -> ReviewSession:
        current = self.open_cached_project(session.project.name, session.locale)
        if current.snapshot.sha256 != session.snapshot.sha256:
            raise CatalogConflictError("workspace catalog changed while the page was open")
        if current.review_snapshot.sha256 != session.review_snapshot.sha256:
            raise ReviewStateConflictError("workspace review-state changed while the page was open")
        if (
            workflow_semantics(session.workflow) != workflow_semantics(self.workflow)
            or workflow_semantics(session.workflow) != workflow_semantics(self.workflows.load())
            or session.family != self.family
            or session.family != self._load_family(self.family_path)
        ):
            raise ReviewContextChangedError("review rules changed; reload before saving")
        if {row.stable_id: row.original for row in current.rows} != {
            row.stable_id: row.original for row in session.rows
        }:
            raise ReviewContextChangedError("reviewed source changed; scan and review it again")
        source = current.source_snapshot
        if source is not None:
            manifest = self.discovery.discover(session.project.name)
            if (
                manifest.catalog_path.resolve() != session.snapshot.path.resolve()
                or not source.input_hashes
                or source.input_hashes != self.source_snapshots.hash_inputs(manifest.inputs)
            ):
                raise ReviewContextChangedError("source inputs changed; scan before saving")
        return current

    def _commit_locale(
        self,
        session: ReviewSession,
        candidate: EffectCatalog | SettingsCatalog,
        entries: dict[str, ReviewStateEntry] | None,
    ) -> ReviewSession:
        settings = isinstance(candidate, SettingsCatalog)
        repository = self.settings_catalogs if settings else self.catalogs
        catalog_write = repository.prepare(session.snapshot, candidate)
        writes = []
        saved_review = session.review_snapshot
        if entries is not None:
            saved_review, state_write = self.review_states.prepare_locale(
                session.review_snapshot,
                session.locale,
                entries,
            )
            writes.append(state_write)
        writes.append(catalog_write)
        commit_files(session.snapshot.path, writes)

        key = session.project.name.casefold()
        snapshot_type = SettingsCatalogSnapshot if settings else CatalogSnapshot
        saved = snapshot_type(
            path=catalog_write.path,
            sha256=content_hash(catalog_write.content),
            catalog=candidate,
        )
        snapshots = self._settings_catalog_snapshots if settings else self._catalog_snapshots
        snapshots[key] = saved
        self._review_state_snapshots[key] = saved_review
        refresh = self._refresh_settings_project if settings else self._refresh_effect_project
        return self._session(refresh(session.project.name), session.locale)

    def save_locale(
        self,
        session: ReviewSession,
        rows: list[dict[str, object]],
    ) -> ReviewSession:
        current = self._assert_save_context(session)
        catalog = current.snapshot.catalog
        settings = isinstance(catalog, SettingsCatalog)
        if settings:
            old_values = {
                entry.id: getattr(entry, session.locale)
                for entry in catalog.entries
            }
        else:
            old_values = catalog.flatten_locale(session.locale)
        values, stages = submitted_values(
            rows,
            old_values,
            {row.stable_id: row.workflow_stage for row in session.rows},
            current.workflow,
        )
        if settings:
            candidate = catalog.with_locale(session.locale, values)
            diagnostics = validate_settings_catalog(candidate, session.locale)
        else:
            source = current.source_snapshot
            ordered = current.source_snapshot.review_layout.canonicalize(values)
            document = catalog.model_dump(by_alias=True, exclude_none=True)
            document["translations"][session.locale] = ordered
            candidate = EffectCatalog.model_validate(document, strict=True)
            diagnostics = validate_catalog_domain(
                candidate,
                current.family,
                source.bindings,
                source.review_layout,
            )
            diagnostics = [
                item for item in diagnostics if item.get("locale") in {None, session.locale}
            ]
        if has_errors(diagnostics):
            raise ReviewValidationError(diagnostics)
        entries = None
        if current.workflow.enabled:
            entries = review_entries(
                values,
                stages,
                {row.stable_id: row.original for row in current.rows},
                session.locale,
                current.workflow,
            )
        return self._commit_locale(current, candidate, entries)

    def set_workflow_stage(
        self,
        session: ReviewSession,
        stable_ids: set[str],
        stage: str | None,
    ) -> ReviewSession:
        if not self.workflow.enabled:
            raise ValueError("workflow stage editing is disabled")
        known = {item.id for item in self.workflow.stages}
        if stage is not None and stage not in known:
            raise ValueError(f"unknown workflow stage: {stage}")
        rows = [
            row.model_copy(update={"workflow_stage": stage, "workflow_stage_explicit": True})
            if row.stable_id in stable_ids
            else row
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
            entry.stage
            for snapshot in self._review_state_snapshots.values()
            for locale_state in snapshot.document.locales.values()
            for entry in locale_state.root.values()
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
