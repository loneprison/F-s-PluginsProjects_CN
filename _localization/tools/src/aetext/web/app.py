"""Single NiceGUI workspace backed only by cache-aware review services."""

from __future__ import annotations

import asyncio
import json
import secrets
import socket
import threading
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from functools import wraps

from nicegui import ui

from ..catalog.repository import CatalogConflictError
from ..catalog.review import (
    ReviewContextChangedError,
    ReviewSession,
    ReviewUnavailableError,
    ReviewValidationError,
    ReviewWorkspaceService,
)
from ..catalog.review_state import ReviewStateConflictError
from .browser import BROWSER_RESPONSE_TIMEOUT, acknowledge_grid_save, read_grid_rows
from .drafts import DraftConflictError, LocaleDraft, apply_draft, draft_changes, rebase_draft
from .i18n import (
    SUPPORTED_UI_LOCALES,
    UI_LOCALE_NAMES,
    UiText,
    ag_grid_locale_text,
    normalize_ui_locale,
)
from .popup_editor import create_popup_editor
from .preferences import UiPreferencesRepository
from .project_tree import project_name_from_node, project_tree_nodes
from .styles import workspace_head
from .translation_grid import (
    CONTENT_STATUSES,
    ROLE_ORDER,
    community_stage_filter,
    community_text_filter,
    content_filter_values,
    content_status_counts,
    grid_options_for_section,
    row_data,
    rows_for_section,
    section_summary,
    summary,
    workflow_stage_counts,
)
from .workflow_settings import create_workflow_dialog


@dataclass(frozen=True)
class ReviewRun:
    host: str
    port: int
    token: str

    @property
    def path(self) -> str:
        return f"/{self.token}"

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}{self.path}"


def _available_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(("127.0.0.1", 0))
        return int(listener.getsockname()[1])


def _initial_project(service: ReviewWorkspaceService, requested: str | None) -> str | None:
    names = {project.name.casefold(): project.name for project in service.workspace.projects}
    if requested and requested.casefold() in names:
        return names[requested.casefold()]
    candidates = [
        project.name
        for project in service.workspace.projects
        if project.catalog_kind == "source-derived"
    ]
    return candidates[0] if candidates else None


def configure_review_app(
    service: ReviewWorkspaceService,
    review_run: ReviewRun,
    *,
    initial_plugin: str | None = None,
    default_locale: str | None = None,
) -> None:
    preferences = UiPreferencesRepository(service.repository_root)

    @ui.page(review_run.path, title="AeText Translation Workspace", language="en")
    async def workspace_page(content_locale: str | None = None) -> None:
        text = UiText(preferences.load())
        locales = service.workspace.locales
        selected_locale = (
            content_locale
            if content_locale in locales
            else default_locale
            if default_locale in locales
            else "zh"
            if "zh" in locales
            else locales[0]
        )
        selected_project = _initial_project(service, initial_plugin)
        initial_project_record = next(
            (project for project in service.workspace.projects if project.name == selected_project),
            None,
        )
        if (
            initial_project_record is not None
            and selected_locale not in initial_project_record.locales
        ):
            selected_locale = initial_project_record.locales[0]
        search_value = ""
        current_session: ReviewSession | None = None
        drafts: dict[tuple[str, str], LocaleDraft] = {}
        operation_lock = asyncio.Lock()

        def page_action(action):
            @wraps(action)
            async def serialized(*args, **kwargs):
                async with operation_lock:
                    freeze = action.__name__ not in {"save_plugin", "save_all"}
                    if freeze:
                        await ui.run_javascript(
                            "document.querySelector('.aetext-editor')?.setAttribute('inert', '');",
                            timeout=BROWSER_RESPONSE_TIMEOUT,
                        )
                    try:
                        return await action(*args, **kwargs)
                    finally:
                        if freeze:
                            await ui.run_javascript(
                                "document.querySelector('.aetext-editor')?.removeAttribute('inert');",
                                timeout=BROWSER_RESPONSE_TIMEOUT,
                            )

            return serialized

        dirty_contexts: set[tuple[str, str]] = set()
        capture_current: Callable[[], Awaitable[None]] | None = None
        acknowledge_current_save: Callable | None = None
        show_current_diagnostics: Callable[[list[dict[str, object]]], Awaitable[None]] | None = None
        refresh_current_draft_state: Callable[[], Awaitable[None]] | None = None
        refresh_current_interface: Callable[[], Awaitable[None]] | None = None
        refresh_current_content: Callable[[str, str], Awaitable[bool]] | None = None
        tree_container = None
        project_tree = None
        editor_container = None

        ui.page_title(text.text("page.title"))
        ui.add_head_html(workspace_head(text))

        with ui.dialog() as save_failure_dialog, ui.card().classes("w-[720px] max-w-[95vw] gap-3"):
            save_failure_title = ui.label(text.text("save.failures_title")).classes(
                "text-lg font-semibold"
            )
            save_failure_details = ui.markdown().classes("max-h-[60vh] overflow-auto")
            save_failure_close = ui.button(
                text.text("common.close"), on_click=save_failure_dialog.close
            ).props("color=primary")

        def project_by_name(name: str | None):
            return next(
                (project for project in service.workspace.projects if project.name == name),
                None,
            )

        def dirty_projects() -> set[str]:
            return {project for project, _locale in dirty_contexts}

        async def sync_dirty_flag() -> None:
            value = "true" if dirty_contexts else "false"
            await ui.run_javascript(
                f"window.aetextDirty = {value} || "
                "window.aetextEditVersion > window.aetextCapturedVersion;",
                timeout=BROWSER_RESPONSE_TIMEOUT,
            )

        async def capture_current_context() -> None:
            if capture_current is not None:
                await capture_current()

        async def refresh_editor() -> None:
            if (
                refresh_current_content is not None
                and selected_project is not None
                and await refresh_current_content(selected_project, selected_locale)
            ):
                return
            render_editor()

        def render_tree() -> None:
            nonlocal project_tree
            tree_container.clear()
            with tree_container:
                nodes = project_tree_nodes(
                    service.workspace,
                    selected_locale,
                    text,
                    search_value,
                    dirty_projects(),
                )

                @page_action
                async def select_node(event) -> None:
                    nonlocal selected_locale, selected_project
                    project_name = project_name_from_node(event.value)
                    if project_name is None or project_name == selected_project:
                        return

                    await capture_current_context()
                    selected_project = project_name
                    project = project_by_name(project_name)
                    if project is not None and selected_locale not in project.locales:
                        selected_locale = project.locales[0]
                        ui.navigate.history.replace(
                            f"{review_run.path}?content_locale={selected_locale}"
                        )
                    update_header()
                    await refresh_editor()

                project_tree = (
                    ui.tree(nodes, on_select=select_node)
                    .props("dense no-connectors")
                    .classes("aetext-project-tree")
                )
                project_tree.expand()
                if selected_project is not None:
                    project_tree.value = f"project:{selected_project}"

        def refresh_tree_nodes() -> None:
            if project_tree is None:
                render_tree()
                return
            project_tree._props["nodes"] = project_tree_nodes(
                service.workspace,
                selected_locale,
                text,
                search_value,
                dirty_projects(),
            )
            project_tree.update()

        async def perform_scan_current() -> None:
            nonlocal current_session
            if selected_project is None:
                ui.notify(text.text("scan.select_project"), type="warning")
                return
            project = project_by_name(selected_project)
            if project is None or project.catalog_kind not in {"source-derived", "settings"}:
                ui.notify(text.text("scan.unsupported"), type="warning")
                return
            notice = ui.notification(
                message=text.text("scan.current.progress", project=selected_project),
                spinner=True,
                timeout=None,
            )
            try:
                current_session = await asyncio.to_thread(
                    service.scan_project,
                    selected_project,
                    selected_locale,
                )
            except Exception as error:
                notice.dismiss()
                ui.notify(text.text("scan.current.failed", error=error), type="negative")
                refresh_tree_nodes()
                await refresh_editor()
                return
            notice.dismiss()
            ui.notify(text.text("scan.current.updated"), type="positive")
            refresh_tree_nodes()
            await refresh_editor()

        @page_action
        async def scan_current() -> None:
            await capture_current_context()
            await perform_scan_current()

        async def perform_scan_all() -> None:
            progress_state: dict[str, object] = {
                "current": 0,
                "total": 1,
                "name": text.text("scan.preparing"),
            }
            cancel_event = threading.Event()
            with ui.dialog() as progress_dialog, ui.card().classes("w-96 gap-3"):
                ui.label(text.text("scan.all.title")).classes("font-medium")
                progress_label = ui.label(text.text("scan.preparing"))
                progress_bar = ui.linear_progress(value=0)
                ui.button(text.text("common.cancel"), on_click=cancel_event.set).props("flat")

            def update_progress(current, total, result) -> None:
                progress_state.update(current=current, total=max(total, 1), name=result.project)

            def refresh_progress() -> None:
                current = int(progress_state["current"])
                total = int(progress_state["total"])
                progress_label.text = f"{current} / {total} · {progress_state['name']}"
                progress_bar.value = current / total

            timer = ui.timer(0.2, refresh_progress)
            progress_dialog.open()
            result = await asyncio.to_thread(
                service.scan_all,
                progress=update_progress,
                cancelled=cancel_event.is_set,
            )
            timer.cancel()
            progress_dialog.close()
            failures = [item for item in result.results if item.status == "failed"]
            if failures:
                ui.notify(
                    text.text(
                        "scan.all.failed",
                        projects=", ".join(item.project for item in failures),
                    ),
                    type="warning",
                )
            elif result.cancelled:
                ui.notify(text.text("scan.all.cancelled"), type="warning")
            else:
                ui.notify(text.text("scan.all.updated"), type="positive")
            refresh_tree_nodes()
            await refresh_editor()

        @page_action
        async def scan_all() -> None:
            await capture_current_context()
            await perform_scan_all()

        async def perform_publication_preview() -> None:
            if selected_project is None:
                ui.notify(text.text("scan.select_project"), type="warning")
                return
            project = project_by_name(selected_project)
            if project is None or project.catalog_kind != "source-derived":
                ui.notify(text.text("publication.unsupported"), type="warning")
                return
            notice = ui.notification(
                message=text.text("publication.progress", project=selected_project),
                spinner=True,
                timeout=None,
            )
            try:
                report = await asyncio.to_thread(
                    service.validate_project_publication,
                    selected_project,
                )
            except Exception as error:
                notice.dismiss()
                ui.notify(text.text("publication.failed", error=error), type="negative")
                refresh_tree_nodes()
                await refresh_editor()
                return
            notice.dismiss()
            refresh_tree_nodes()
            await refresh_editor()
            if report.valid:
                ui.notify(
                    text.text(
                        "publication.passed",
                        completed=report.completed,
                        total=report.total,
                    ),
                    type="positive",
                )
                return
            with ui.dialog() as dialog, ui.card().classes("w-[760px] max-w-[95vw] gap-3"):
                ui.label(text.text("publication.rejected")).classes("text-xl font-semibold")
                ui.label(
                    text.text(
                        "publication.completed",
                        completed=report.completed,
                        total=report.total,
                    )
                )
                ui.markdown(
                    "\n".join(
                        f"- `{issue.code}` {issue.locale or '-'} / "
                        f"{issue.stable_id or '-'}: "
                        f"{text.diagnostic(issue.model_dump(by_alias=True))}"
                        for issue in report.issues
                    )
                ).classes("max-h-[60vh] overflow-auto")
                ui.button(text.text("common.close"), on_click=dialog.close).props("color=primary")
            dialog.open()

        @page_action
        async def publication_preview() -> None:
            await capture_current_context()
            if dirty_contexts:
                ui.notify(text.text("publication.unsaved_ignored"), type="warning")
            await perform_publication_preview()

        async def perform_reload_catalogs() -> None:
            nonlocal selected_locale, selected_project
            await asyncio.to_thread(service.reload_catalogs)
            if project_by_name(selected_project) is None:
                selected_project = _initial_project(service, None)
            project = project_by_name(selected_project)
            if project is not None and selected_locale not in project.locales:
                selected_locale = project.locales[0]
            ui.notify(text.text("reload.completed"), type="positive")
            refresh_tree_nodes()
            await refresh_editor()

        @page_action
        async def reload_catalogs() -> None:
            await capture_current_context()
            await perform_reload_catalogs()

        def show_save_failures(
            failures: list[tuple[tuple[str, str], str]],
        ) -> None:
            save_failure_details.content = "\n".join(
                f"- `{project}` · `{locale}`: {message}" for (project, locale), message in failures
            )
            save_failure_dialog.open()

        async def save_draft(
            key: tuple[str, str],
        ) -> tuple[bool, str | None]:
            nonlocal current_session
            draft = drafts.get(key)
            if draft is None:
                return True, None
            project, locale = key
            try:
                fresh = service.open_cached_project(project, locale)
                candidate = apply_draft(fresh, draft)
                saved = service.save_locale(
                    fresh,
                    [row.model_dump() for row in candidate.rows],
                )
            except ReviewValidationError as error:
                if (
                    key == (selected_project, selected_locale)
                    and show_current_diagnostics is not None
                ):
                    await show_current_diagnostics(error.diagnostics)
                return False, text.text("save.validation_failed")
            except ReviewContextChangedError:
                return False, text.text("save.source_changed")
            except (CatalogConflictError, DraftConflictError, ReviewStateConflictError):
                return False, text.text("save.conflict")
            except Exception as error:
                return False, str(error)
            if key == (selected_project, selected_locale) and acknowledge_current_save is not None:
                await acknowledge_current_save(saved, draft)
            else:
                drafts.pop(key, None)
                dirty_contexts.discard(key)
            return True, None

        async def save_keys(
            keys: list[tuple[str, str]],
            *,
            scope: str,
        ) -> None:
            keys = [key for key in keys if key in dirty_contexts]
            if not keys:
                await sync_dirty_flag()
                refresh_tree_nodes()
                update_header()
                if refresh_current_draft_state is not None:
                    await refresh_current_draft_state()
                ui.notify(text.text("save.nothing"), type="info")
                return
            failures: list[tuple[tuple[str, str], str]] = []
            saved_count = 0
            for key in keys:
                saved, message = await save_draft(key)
                if saved:
                    saved_count += 1
                else:
                    failures.append((key, message or text.text("save.unknown_failure")))
            await sync_dirty_flag()
            refresh_tree_nodes()
            update_header()
            if refresh_current_draft_state is not None:
                await refresh_current_draft_state()
            if failures:
                ui.notify(
                    text.text(
                        "save.partial",
                        saved=saved_count,
                        failed=len(failures),
                    ),
                    type="warning",
                )
                show_save_failures(failures)
            else:
                message = "save.all_completed" if scope == "all" else "save.plugin_completed"
                ui.notify(text.text(message, count=saved_count), type="positive")

        @page_action
        async def save_plugin(project: str | None = None) -> None:
            target = project or selected_project
            if target is None:
                ui.notify(text.text("scan.select_project"), type="warning")
                return
            await capture_current_context()
            project = project_by_name(target)
            project_locales = [] if project is None else project.locales
            keys = [
                (target, locale) for locale in project_locales if (target, locale) in dirty_contexts
            ]
            await save_keys(keys, scope="plugin")

        @page_action
        async def save_all() -> None:
            await capture_current_context()
            order = {locale: index for index, locale in enumerate(locales)}
            keys = sorted(
                dirty_contexts,
                key=lambda key: (key[0].casefold(), order.get(key[1], len(order))),
            )
            await save_keys(keys, scope="all")

        def render_ready_editor(
            session: ReviewSession,
            base_session: ReviewSession,
        ) -> None:
            nonlocal capture_current, current_session, refresh_current_draft_state
            nonlocal acknowledge_current_save
            nonlocal refresh_current_content, refresh_current_interface
            nonlocal show_current_diagnostics
            current_session = session
            active_session = session
            acknowledged_revision = 0
            draft_base_session = base_session
            active_context_key = (session.project.name, session.locale)
            ui.run_javascript("window.aetextDrafts = {};")
            ui.label(session.project.name).classes("text-2xl font-semibold")
            item_count_label = ui.label(
                text.text(
                    "editor.item_count",
                    locale=selected_locale,
                    count=len(session.rows),
                )
            ).classes("text-sm text-gray-600")
            summary_label = ui.label(summary(session, text)).classes("text-sm text-gray-600")

            active_content: set[str] = set()
            active_stages: set[str] = set()
            active_roles = tuple(role for role in ROLE_ORDER if rows_for_section(session, role))
            grid_holder: dict[str, object] = {}
            expansion_holder: dict[str, object] = {}
            content_chip_holder: dict[str, object] = {}
            stage_chip_holder: dict[str, object] = {}
            existing_draft = drafts.get(active_context_key)
            changed_ids = set(draft_changes(existing_draft)) if existing_draft else set()
            dirty_roles = {row.primary_role for row in session.rows if row.stable_id in changed_ids}
            content_counts = content_status_counts(session)
            stage_counts = workflow_stage_counts(session)
            save_plugin_button = None

            def stage_display_label(stage) -> str:
                return (
                    text.stage_label(stage)
                    if stage.enabled
                    else text.text("common.disabled", label=text.stage_label(stage))
                )

            def section_title(role: str, current: ReviewSession | None = None) -> str:
                displayed_session = current or current_session or active_session
                dirty = f"  ● {text.text('editor.unsaved')}" if role in dirty_roles else ""
                return (
                    f"{text.text(f'role.{role}')}  "
                    f"{section_summary(displayed_session, role)}{dirty}"
                )

            def mark_dirty(role: str) -> None:
                was_dirty = active_context_key in dirty_contexts
                dirty_contexts.add(active_context_key)
                dirty_roles.add(role)
                expansion = expansion_holder.get(role)
                if expansion is not None:
                    expansion.set_text(section_title(role))
                ui.run_javascript("window.aetextDirty = true")
                if save_plugin_button is not None:
                    save_plugin_button.enable()
                if not was_dirty:
                    refresh_tree_nodes()
                    update_header()

            async def filter_all(column: str, model: dict[str, object] | None) -> None:
                for grid in grid_holder.values():
                    await grid.run_grid_method("setColumnFilterModel", column, model)
                    await grid.run_grid_method("onFilterChanged")

            with ui.row().classes("aetext-filter-row items-center flex-wrap"):
                filter_label = ui.label(text.text("editor.filter")).classes(
                    "aetext-filter-label text-sm"
                )

                async def filter_content(status: str, selected: bool) -> None:
                    (active_content.add if selected else active_content.discard)(status)
                    values = content_filter_values(active_content, text)
                    await filter_all(
                        "content_status_label",
                        community_text_filter(values),
                    )

                for status in CONTENT_STATUSES:
                    if status == "unscanned":
                        continue
                    content_chip_holder[status] = (
                        ui.chip(
                            f"{text.text(f'status.{status}')} {content_counts[status]}",
                            selectable=True,
                            on_selection_change=lambda event, value=status: filter_content(
                                value, bool(event.value)
                            ),
                        )
                        .props("outline")
                        .classes("aetext-filter-chip")
                    )
                if session.workflow.enabled:

                    async def filter_stage(stage_id: str, selected: bool) -> None:
                        (active_stages.add if selected else active_stages.discard)(stage_id)
                        await filter_all(
                            "workflow_stage",
                            community_stage_filter(active_stages),
                        )

                    stage_chip_holder[""] = (
                        ui.chip(
                            f"{text.text('common.none')} {stage_counts['']}",
                            selectable=True,
                            color="grey",
                            on_selection_change=lambda event: filter_stage("", bool(event.value)),
                        )
                        .props("outline")
                        .classes("aetext-filter-chip")
                    )
                    for stage in session.workflow.stages:
                        stage_chip_holder[stage.id] = (
                            ui.chip(
                                f"{stage_display_label(stage)} {stage_counts.get(stage.id, 0)}",
                                selectable=True,
                                color=stage.color,
                                on_selection_change=lambda event, value=stage.id: filter_stage(
                                    value, bool(event.value)
                                ),
                            )
                            .props("outline")
                            .classes("aetext-filter-chip")
                        )

            open_popup_editor = create_popup_editor(grid_holder, lambda: text)

            for role in active_roles:
                role_rows = rows_for_section(session, role)
                title = section_title(role)
                expansion = ui.expansion(title, value=True, icon="table_rows").classes(
                    "w-full border rounded"
                )
                expansion_holder[role] = expansion
                with expansion:
                    grid = ui.aggrid(
                        grid_options_for_section(session, role, text),
                        modules="community",
                        auto_size_columns=False,
                    ).classes("w-full aetext-review-grid")
                    grid.style(f"height: {min(max(180, 76 + len(role_rows) * 44), 520)}px")

                    async def grid_changed(event, grid_role=role, current_grid=grid) -> None:
                        revision = (event.args.get("data") or {}).get("edit_revision", 0)
                        if revision <= acknowledged_revision:
                            return
                        mark_dirty(grid_role)
                        if event.args.get("colId") == "use_source":
                            await current_grid.run_grid_method("refreshCells", {"force": True})

                    grid.on("cellValueChanged", grid_changed)
                    grid.on("draftChanged", grid_changed)
                    grid.on(
                        "popupEditRequested",
                        lambda event, grid_role=role: open_popup_editor(grid_role, event),
                    )
                    grid_holder[role] = grid

            async def collect_rows() -> list[dict[str, object]]:
                return await read_grid_rows([grid.id for grid in grid_holder.values()])

            async def capture() -> None:
                rows = await read_grid_rows(
                    [grid.id for grid in grid_holder.values()], capture=True
                )
                candidate = LocaleDraft(base_session=draft_base_session, rows=rows)
                if draft_changes(candidate):
                    drafts[active_context_key] = candidate
                    dirty_contexts.add(active_context_key)
                else:
                    drafts.pop(active_context_key, None)
                    dirty_contexts.discard(active_context_key)
                await sync_dirty_flag()

            async def acknowledge_saved(saved: ReviewSession, submitted: LocaleDraft) -> None:
                nonlocal active_session, draft_base_session, current_session, acknowledged_revision
                draft_base_session = saved
                current_session = saved
                result = await acknowledge_grid_save(
                    [grid.id for grid in grid_holder.values()],
                    submitted.rows,
                    [row_data(row, text) for row in saved.rows],
                    other_dirty=bool(dirty_contexts - {active_context_key}),
                )
                acknowledged_revision = int(result["revision"])
                candidate = LocaleDraft(saved, result["rows"])
                if draft_changes(candidate):
                    drafts[active_context_key] = candidate
                    dirty_contexts.add(active_context_key)
                    active_session = apply_draft(saved, candidate)
                else:
                    drafts.pop(active_context_key, None)
                    dirty_contexts.discard(active_context_key)
                    active_session = saved
                current_session = active_session

            acknowledge_current_save = acknowledge_saved

            capture_current = capture

            async def collect_selected_rows() -> list[dict[str, object]]:
                rows: list[dict[str, object]] = []
                for role in active_roles:
                    rows.extend(await grid_holder[role].get_selected_rows())
                return rows

            async def update_grid_rows(
                rows: list[dict[str, object]], *, stage_edit: bool = False
            ) -> None:
                if stage_edit:
                    await ui.run_javascript(
                        "const rows = "
                        + json.dumps({str(row["stable_id"]): row for row in rows})
                        + "; for (const id of "
                        + json.dumps([grid.id for grid in grid_holder.values()])
                        + ") { const api = getElement(id).api; api.forEachNode(node => {"
                        + "const row = rows[node.data.stable_id]; if (!row) return; "
                        + "Object.assign(node.data, row); window.aetextMarkEdit(node.data, true); "
                        + "api.refreshCells({rowNodes: [node], columns: ['workflow_stage'], "
                        + "force: true}); }); }",
                        timeout=BROWSER_RESPONSE_TIMEOUT,
                    )
                    return
                for role in active_roles:
                    changed_rows = [row for row in rows if str(row["primary_role"]) == role]
                    if not changed_rows:
                        continue
                    grid = grid_holder[role]
                    await grid.run_grid_method(
                        "applyTransactionAsync",
                        {"update": changed_rows},
                        timeout=BROWSER_RESPONSE_TIMEOUT,
                    )
                    await grid.run_grid_method(
                        "flushAsyncTransactions", timeout=BROWSER_RESPONSE_TIMEOUT
                    )

            async def show_inline_diagnostics(items: list[dict[str, object]]) -> None:
                messages: dict[str, list[str]] = {}
                for item in items:
                    if item.get("severity") != "error" or item.get("locale") != selected_locale:
                        continue
                    stable_id = str(item.get("stableId") or "")
                    if stable_id:
                        messages.setdefault(stable_id, []).append(text.diagnostic(item))
                for role in active_roles:
                    for row in rows_for_section(active_session, role):
                        await grid_holder[role].run_row_method(
                            row.stable_id,
                            "setDataValue",
                            "validation_message",
                            "\n".join(messages.get(row.stable_id, [])),
                        )
                    await grid_holder[role].run_grid_method("refreshCells", {"force": True})

            show_current_diagnostics = show_inline_diagnostics

            @page_action
            async def apply_stage(stage: str | None, scope: str) -> None:
                rows = await collect_rows()
                if scope == "selected":
                    selected = await collect_selected_rows()
                    if not selected:
                        ui.notify(text.text("batch.select_row"), type="warning")
                        return
                    target_ids = {str(row["stable_id"]) for row in selected}
                else:
                    target_ids = {str(row["stable_id"]) for row in rows}
                changed_rows: list[dict[str, object]] = []
                for row in rows:
                    if str(row["stable_id"]) not in target_ids:
                        continue
                    current_stage = row.get("workflow_stage") or None
                    if current_stage == stage:
                        continue
                    row["workflow_stage"] = stage
                    row["workflow_stage_explicit"] = True
                    changed_rows.append(row)
                await update_grid_rows(changed_rows, stage_edit=True)
                for role in {str(row["primary_role"]) for row in changed_rows}:
                    mark_dirty(role)

            if session.workflow.enabled:

                def enabled_stage_options() -> dict[str, str]:
                    return {
                        stage.id: text.stage_label(stage)
                        for stage in session.workflow.stages
                        if stage.enabled
                    }

                apply_all_dialog = ui.dialog()
                with ui.row().classes("items-end gap-2"):
                    batch_stage = ui.select(
                        {"": text.text("common.none"), **enabled_stage_options()},
                        value="",
                        label=text.text("batch.stage"),
                    ).classes("w-48")
                    apply_selected_button = ui.button(
                        text.text("batch.apply_selected"),
                        on_click=lambda: apply_stage(batch_stage.value or None, "selected"),
                    ).props("outline")
                    apply_all_button = ui.button(
                        text.text("batch.apply_all", count=len(session.rows)),
                        on_click=apply_all_dialog.open,
                    ).props("outline")

                with apply_all_dialog, ui.card().classes("w-96 gap-3"):
                    apply_all_title = ui.label(text.text("batch.confirm_title")).classes(
                        "text-lg font-semibold"
                    )
                    apply_all_body = ui.label(
                        text.text("batch.confirm_body", count=len(session.rows))
                    )

                    async def apply_all_confirmed() -> None:
                        apply_all_dialog.close()
                        await apply_stage(batch_stage.value or None, "all")

                    with ui.row().classes("w-full justify-end gap-2"):
                        apply_all_cancel = ui.button(
                            text.text("common.cancel"),
                            on_click=apply_all_dialog.close,
                        ).props("flat")
                        apply_all_confirm = ui.button(
                            text.text("batch.confirm_all"),
                            on_click=apply_all_confirmed,
                        ).props("color=primary")

            save_plugin_button = ui.button(
                text.text("save.plugin_button"),
                icon="save",
                on_click=lambda: save_plugin(session.project.name),
            ).props("color=primary")
            if session.project.name not in dirty_projects():
                save_plugin_button.disable()

            diagnostics_markdown = ui.markdown().classes("w-full text-sm")

            def refresh_session_diagnostics() -> None:
                errors = [
                    item for item in active_session.diagnostics if item.get("severity") == "error"
                ]
                diagnostics_markdown.content = "\n".join(
                    f"- `{item.get('code')}` {text.diagnostic(item)}" for item in errors
                )
                diagnostics_markdown.set_visibility(bool(errors))

            def refresh_session_chrome() -> None:
                item_count_label.text = text.text(
                    "editor.item_count",
                    locale=active_session.locale,
                    count=len(active_session.rows),
                )
                summary_label.text = summary(active_session, text)
                for status, chip in content_chip_holder.items():
                    chip.text = f"{text.text(f'status.{status}')} {content_counts[status]}"
                if active_session.workflow.enabled:
                    stage_chip_holder[""].text = f"{text.text('common.none')} {stage_counts['']}"
                    stages = {stage.id: stage for stage in active_session.workflow.stages}
                    for stage_id, chip in stage_chip_holder.items():
                        if stage_id:
                            chip.text = (
                                f"{stage_display_label(stages[stage_id])} "
                                f"{stage_counts.get(stage_id, 0)}"
                            )
                    apply_all_button.text = text.text(
                        "batch.apply_all", count=len(active_session.rows)
                    )
                    apply_all_body.text = text.text(
                        "batch.confirm_body", count=len(active_session.rows)
                    )
                for role, expansion in expansion_holder.items():
                    expansion.set_text(section_title(role, active_session))
                if active_session.project.name in dirty_projects():
                    save_plugin_button.enable()
                else:
                    save_plugin_button.disable()
                refresh_session_diagnostics()

            async def refresh_draft_state() -> None:
                active_draft = drafts.get(active_context_key)
                changed = set(draft_changes(active_draft)) if active_draft else set()
                dirty_roles.clear()
                dirty_roles.update(
                    row.primary_role for row in active_session.rows if row.stable_id in changed
                )
                content_counts.clear()
                content_counts.update(content_status_counts(active_session))
                stage_counts.clear()
                stage_counts.update(workflow_stage_counts(active_session))
                refresh_session_chrome()

            refresh_current_draft_state = refresh_draft_state

            displayed_text = text

            async def refresh_interface() -> None:
                nonlocal displayed_text
                active_session = current_session or session
                item_count_label.text = text.text(
                    "editor.item_count",
                    locale=selected_locale,
                    count=len(active_session.rows),
                )
                summary_label.text = summary(active_session, text)
                filter_label.text = text.text("editor.filter")
                save_plugin_button.text = text.text("save.plugin_button")
                for status, chip in content_chip_holder.items():
                    chip.text = f"{text.text(f'status.{status}')} {content_counts[status]}"
                if active_session.workflow.enabled:
                    stage_chip_holder[""].text = f"{text.text('common.none')} {stage_counts['']}"
                    stages = {stage.id: stage for stage in active_session.workflow.stages}
                    for stage_id, chip in stage_chip_holder.items():
                        if not stage_id:
                            continue
                        chip.text = (
                            f"{stage_display_label(stages[stage_id])} "
                            f"{stage_counts.get(stage_id, 0)}"
                        )
                for role, expansion in expansion_holder.items():
                    expansion.set_text(section_title(role, active_session))

                client_rows = await collect_rows()
                model_rows = {row.stable_id: row for row in active_session.rows}
                localized_rows: list[dict[str, object]] = []
                localized_fields = (
                    "content_status_label",
                    "validation_message",
                    "review_change_message",
                )
                for row in client_rows:
                    source = model_rows[str(row["stable_id"])]
                    localized = row_data(source, text)
                    for field in localized_fields:
                        row[field] = localized[field]
                    localized_rows.append(row)
                await update_grid_rows(localized_rows)

                old_status_labels = {
                    displayed_text.text(f"status.{status}"): text.text(f"status.{status}")
                    for status in CONTENT_STATUSES
                }

                def relabel_status_filter(value: object) -> object:
                    if isinstance(value, dict):
                        return {key: relabel_status_filter(item) for key, item in value.items()}
                    if isinstance(value, list):
                        return [relabel_status_filter(item) for item in value]
                    if isinstance(value, str):
                        return old_status_labels.get(value, value)
                    return value

                for role, grid in grid_holder.items():
                    column_state = await grid.run_grid_method(
                        "getColumnState", timeout=BROWSER_RESPONSE_TIMEOUT
                    )
                    filter_model = await grid.run_grid_method(
                        "getFilterModel", timeout=BROWSER_RESPONSE_TIMEOUT
                    )
                    options = grid_options_for_section(active_session, role, text)
                    await grid.run_grid_method(
                        "setGridOption",
                        "columnDefs",
                        options["columnDefs"],
                        timeout=BROWSER_RESPONSE_TIMEOUT,
                    )
                    if isinstance(column_state, list):
                        await grid.run_grid_method(
                            "applyColumnState",
                            {"state": column_state, "applyOrder": True},
                            timeout=BROWSER_RESPONSE_TIMEOUT,
                        )
                    if isinstance(filter_model, dict):
                        if "content_status_label" in filter_model:
                            filter_model["content_status_label"] = relabel_status_filter(
                                filter_model["content_status_label"]
                            )
                        await grid.run_grid_method(
                            "setFilterModel", filter_model, timeout=BROWSER_RESPONSE_TIMEOUT
                        )
                    await grid.run_grid_method("refreshHeader", timeout=BROWSER_RESPONSE_TIMEOUT)
                    await grid.run_grid_method(
                        "refreshCells", {"force": True}, timeout=BROWSER_RESPONSE_TIMEOUT
                    )
                    await grid.run_grid_method("onFilterChanged", timeout=BROWSER_RESPONSE_TIMEOUT)

                if active_session.workflow.enabled:
                    batch_stage.set_label(text.text("batch.stage"))
                    batch_stage.set_options(
                        {"": text.text("common.none"), **enabled_stage_options()}
                    )
                    apply_selected_button.text = text.text("batch.apply_selected")
                    apply_all_button.text = text.text(
                        "batch.apply_all", count=len(active_session.rows)
                    )
                    apply_all_title.text = text.text("batch.confirm_title")
                    apply_all_body.text = text.text(
                        "batch.confirm_body", count=len(active_session.rows)
                    )
                    apply_all_cancel.text = text.text("common.cancel")
                    apply_all_confirm.text = text.text("batch.confirm_all")
                refresh_session_diagnostics()
                displayed_text = text

            async def refresh_content(project_name: str, locale: str) -> bool:
                nonlocal active_context_key, active_session, current_session
                nonlocal draft_base_session
                if project_name != active_session.project.name:
                    return False
                try:
                    new_base_session = service.open_cached_project(project_name, locale)
                except ReviewUnavailableError:
                    return False
                draft = drafts.get((project_name, locale))
                try:
                    if draft:
                        draft = rebase_draft(new_base_session, draft)
                        if draft_changes(draft):
                            drafts[(project_name, locale)] = draft
                        else:
                            drafts.pop((project_name, locale), None)
                            dirty_contexts.discard((project_name, locale))
                            draft = None
                    new_session = (
                        apply_draft(new_base_session, draft) if draft else new_base_session
                    )
                except ValueError:
                    return False
                old_shape = tuple((row.primary_role, row.stable_id) for row in active_session.rows)
                new_shape = tuple((row.primary_role, row.stable_id) for row in new_session.rows)
                if old_shape != new_shape or active_session.workflow != new_session.workflow:
                    return False

                active_session = new_session
                current_session = new_session
                active_context_key = (project_name, locale)
                draft_base_session = draft.base_session if draft else new_base_session
                content_counts.clear()
                content_counts.update(content_status_counts(new_session))
                stage_counts.clear()
                stage_counts.update(workflow_stage_counts(new_session))
                changed_ids = set(draft_changes(draft)) if draft else set()
                dirty_roles.clear()
                dirty_roles.update(
                    row.primary_role for row in new_session.rows if row.stable_id in changed_ids
                )
                await ui.run_javascript("window.aetextDrafts = {};")
                await update_grid_rows([row_data(row, text) for row in new_session.rows])
                for grid in grid_holder.values():
                    await grid.run_grid_method("refreshCells", {"force": True})
                    await grid.run_grid_method("onFilterChanged")
                refresh_session_chrome()
                return True

            refresh_session_diagnostics()
            refresh_current_content = refresh_content
            refresh_current_interface = refresh_interface

        def render_editor() -> None:
            nonlocal capture_current, current_session, refresh_current_draft_state
            nonlocal acknowledge_current_save
            nonlocal refresh_current_content, refresh_current_interface
            nonlocal show_current_diagnostics
            current_session = None
            capture_current = None
            acknowledge_current_save = None
            refresh_current_draft_state = None
            refresh_current_interface = None
            refresh_current_content = None
            show_current_diagnostics = None
            editor_container.clear()
            project = project_by_name(selected_project)
            with editor_container:
                if project is None:
                    message = ui.label(text.text("editor.select_project")).classes(
                        "text-xl text-gray-500"
                    )

                    async def refresh_select_project() -> None:
                        message.text = text.text("editor.select_project")

                    refresh_current_interface = refresh_select_project
                    return
                if project.scan_state in {"invalid", "error"}:
                    ui.label(project.name).classes("text-2xl font-semibold")
                    message = ui.label(text.text("editor.invalid"))
                    scan_button = None
                    if project.catalog_kind == "source-derived":
                        scan_button = ui.button(
                            text.text("header.scan_current"),
                            icon="refresh",
                            on_click=scan_current,
                        )

                    async def refresh_invalid() -> None:
                        message.text = text.text("editor.invalid")
                        if scan_button is not None:
                            scan_button.text = text.text("header.scan_current")

                    refresh_current_interface = refresh_invalid
                    return
                if project.scan_state == "unscanned":
                    ui.label(project.name).classes("text-2xl font-semibold")
                    unscanned_label = ui.label(text.text("editor.unscanned")).classes("text-lg")
                    scan_hint = ui.label(text.text("editor.scan_hint"))
                    scan_button = ui.button(
                        text.text("header.scan_current"),
                        icon="document_scanner",
                        on_click=scan_current,
                    ).props("color=primary")

                    async def refresh_unscanned() -> None:
                        unscanned_label.text = text.text("editor.unscanned")
                        scan_hint.text = text.text("editor.scan_hint")
                        scan_button.text = text.text("header.scan_current")

                    refresh_current_interface = refresh_unscanned
                    return
                try:
                    base_session = service.open_cached_project(project.name, selected_locale)
                except ReviewUnavailableError as error:
                    ui.label(str(error)).classes("text-negative")

                    async def refresh_unavailable() -> None:
                        return

                    refresh_current_interface = refresh_unavailable
                    return
                draft = drafts.get((project.name, selected_locale))
                try:
                    if draft:
                        draft = rebase_draft(base_session, draft)
                        if draft_changes(draft):
                            drafts[(project.name, selected_locale)] = draft
                        else:
                            drafts.pop((project.name, selected_locale), None)
                            dirty_contexts.discard((project.name, selected_locale))
                            draft = None
                    session = apply_draft(base_session, draft) if draft else base_session
                except ValueError as error:
                    error_message = str(error)
                    message = ui.label(
                        text.text("editor.draft_stale", error=error_message)
                    ).classes("text-negative")

                    async def refresh_stale() -> None:
                        message.text = text.text("editor.draft_stale", error=error_message)

                    refresh_current_interface = refresh_stale
                    return
                render_ready_editor(
                    session,
                    draft.base_session if draft else base_session,
                )

        @page_action
        async def workflow_saved() -> None:
            refresh_tree_nodes()
            await refresh_editor()

        open_workflow_settings = create_workflow_dialog(
            service,
            workflow_saved,
            lambda: text,
        )

        @page_action
        async def open_workflow_settings_with_draft() -> None:
            await capture_current_context()
            open_workflow_settings()

        @page_action
        async def change_interface_language(event) -> None:
            nonlocal text
            requested_ui_locale = normalize_ui_locale(event.value)
            if requested_ui_locale == text.locale:
                return

            await capture_current_context()
            preferences.save(requested_ui_locale)
            text = UiText(requested_ui_locale)
            save_failure_title.text = text.text("save.failures_title")
            save_failure_close.text = text.text("common.close")
            await ui.run_javascript(
                "document.documentElement.lang = "
                f"{json.dumps(text.locale)}; document.title = "
                f"{json.dumps(text.text('page.title'), ensure_ascii=False)}; "
                "window.aetextAgGridLocale = "
                f"{json.dumps(ag_grid_locale_text(text), ensure_ascii=False)};",
                timeout=BROWSER_RESPONSE_TIMEOUT,
            )
            update_header()
            refresh_tree_nodes()
            if refresh_current_interface is not None:
                await refresh_current_interface()

        @page_action
        async def change_locale(event) -> None:
            nonlocal selected_locale
            requested_locale = str(event.value)
            if requested_locale == selected_locale:
                return
            project = project_by_name(selected_project)
            if project is None or requested_locale not in project.locales:
                return

            await capture_current_context()
            selected_locale = requested_locale
            ui.navigate.history.replace(f"{review_run.path}?content_locale={selected_locale}")
            update_header()
            refresh_tree_nodes()
            await refresh_editor()

        def change_search(event) -> None:
            nonlocal search_value
            search_value = str(event.value or "")
            refresh_tree_nodes()

        with ui.header().classes("aetext-header items-center gap-4 px-4 no-wrap"):
            ui.label("AeText").classes("text-xl font-semibold")
            interface_language_select = ui.select(
                {locale: UI_LOCALE_NAMES[locale] for locale in SUPPORTED_UI_LOCALES},
                value=text.locale,
                label=text.text("header.interface_language"),
                on_change=change_interface_language,
            ).classes("w-44")
            translation_language_select = ui.select(
                {locale: locale for locale in locales},
                value=selected_locale,
                label=text.text("header.translation_language"),
                on_change=change_locale,
            ).classes("w-44")
            search_input = (
                ui.input(
                    text.text("header.search"),
                    value=search_value,
                    on_change=change_search,
                )
                .props("clearable dense")
                .classes("w-64")
            )
            with ui.dropdown_button(
                text.text("header.scan"),
                icon="document_scanner",
                auto_close=True,
            ) as scan_dropdown:
                with ui.item(on_click=scan_current):
                    scan_current_text = ui.item_section(text.text("header.scan_current"))
                with ui.item(on_click=scan_all):
                    scan_all_text = ui.item_section(text.text("header.scan_all"))
                with ui.item(on_click=publication_preview):
                    publication_text = ui.item_section(text.text("header.publication"))
                with ui.item(on_click=reload_catalogs):
                    reload_text = ui.item_section(text.text("header.reload"))
            workflow_button = ui.button(
                text.text("header.workflow"),
                icon="tune",
                on_click=open_workflow_settings_with_draft,
            ).props("flat")
            save_all_button = (
                ui.button(
                    text.text("save.all_button"),
                    on_click=save_all,
                )
                .props("color=primary")
                .classes("aetext-save-all")
            )

        def update_header() -> None:
            interface_language_select.set_label(text.text("header.interface_language"))
            translation_language_select.set_label(text.text("header.translation_language"))
            project = project_by_name(selected_project)
            available_locales = [] if project is None else project.locales
            translation_language_select.set_options(
                {
                    locale: (
                        f"* {locale}" if (selected_project, locale) in dirty_contexts else locale
                    )
                    for locale in available_locales
                },
                value=selected_locale,
            )
            search_input.set_label(text.text("header.search"))
            scan_dropdown.text = text.text("header.scan")
            scan_current_text.text = text.text("header.scan_current")
            scan_all_text.text = text.text("header.scan_all")
            publication_text.text = text.text("header.publication")
            reload_text.text = text.text("header.reload")
            workflow_button.text = text.text("header.workflow")
            save_all_button.text = text.text("save.all_button")
            if dirty_contexts:
                save_all_button.enable()
            else:
                save_all_button.disable()

        update_header()

        with ui.left_drawer(value=True, bordered=True).props("width=360"):
            tree_container = ui.column().classes("aetext-tree-host w-full p-2")
        editor_container = (
            ui.column().classes("aetext-editor").classes("aetext-editor-host w-full p-5 gap-3")
        )
        render_tree()
        render_editor()


def run_review(
    service: ReviewWorkspaceService,
    plugin_name: str | None = None,
    *,
    locale: str | None = None,
    port: int | None = None,
    show_browser: bool = True,
) -> None:
    review_run = ReviewRun(
        host="127.0.0.1",
        port=port or _available_port(),
        token=secrets.token_urlsafe(24),
    )
    configure_review_app(
        service,
        review_run,
        initial_plugin=plugin_name,
        default_locale=locale,
    )
    print(f"AeText review: {review_run.url}", flush=True)
    ui.run(
        host=review_run.host,
        port=review_run.port,
        show=review_run.path if show_browser else False,
        native=False,
        reload=False,
        on_air=None,
        fastapi_docs=False,
        storage_secret=review_run.token,
        show_welcome_message=False,
    )
