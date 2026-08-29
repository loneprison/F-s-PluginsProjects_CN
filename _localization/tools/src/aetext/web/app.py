# ruff: noqa: RUF001
"""Single NiceGUI workspace backed only by cache-aware review services."""

from __future__ import annotations

import asyncio
import secrets
import socket
import threading
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from nicegui import ui

from ..catalog.popup import POPUP_SEPARATOR, popup_structure_errors, split_popup
from ..catalog.review import (
    ReviewSession,
    ReviewUnavailableError,
    ReviewValidationError,
    ReviewWorkspaceService,
)
from .project_tree import project_name_from_node, project_tree_nodes
from .translation_grid import (
    CONTENT_STATUS_LABELS,
    ROLE_LABELS,
    ROLE_ORDER,
    all_row_data,
    community_stage_filter,
    community_text_filter,
    content_filter_values,
    content_status_counts,
    grid_options_for_section,
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
    @ui.page(review_run.path, title="AeText 翻译工作区", language="zh-CN")
    async def workspace_page() -> None:
        locales = service.workspace.locales
        selected_locale = (
            default_locale if default_locale in locales else "zh" if "zh" in locales else locales[0]
        )
        selected_project = _initial_project(service, initial_plugin)
        search_value = ""
        current_session: ReviewSession | None = None
        save_current: Callable[[], Awaitable[bool]] | None = None
        tree_container = None
        editor_container = None

        ui.add_head_html(
            """
<script>
window.aetextDirty = false;
window.aetextDrafts = {};
window.addEventListener('beforeunload', event => {
  if (window.aetextDirty) {
    event.preventDefault();
    event.returnValue = '';
  }
});
</script>
<style>
.aetext-translation-wrap { width: 100%; padding: 5px 0; }
.aetext-translation-input { width: 100%; min-height: 34px; border: 1px solid #b8c0cc;
  border-radius: 6px; padding: 6px 8px; background: var(--q-page-container-background, white);
  color: inherit; resize: vertical; line-height: 1.4; }
.aetext-translation-input:focus { outline: 2px solid var(--q-primary); border-color: transparent; }
.aetext-translation-input:disabled { background: rgba(127,127,127,.12); color: #777;
  cursor: not-allowed; }
.aetext-popup-button { border: 1px solid var(--q-primary); color: var(--q-primary);
  background: transparent;
  border-radius: 6px; padding: 6px 10px; cursor: pointer; }
.aetext-popup-button:disabled { border-color: #aaa; color: #888; cursor: not-allowed;
  opacity: .65; }
.aetext-stage-select { max-width: 100%; border: 0; border-radius: 999px; padding: 4px 24px 4px 10px;
  cursor: pointer; font-weight: 600; }
.aetext-original-wrap { display: flex; align-items: flex-start; gap: 6px; width: 100%;
  padding: 5px 0; }
.aetext-original-text { flex: 1; white-space: pre-wrap; overflow-wrap: anywhere; }
.aetext-copy-button { opacity: 0; border: 0; border-radius: 4px; padding: 2px 6px; cursor: pointer;
  color: var(--q-primary); background: rgba(127,127,127,.10); transition: opacity .12s; }
.aetext-original-wrap:hover .aetext-copy-button, .aetext-copy-button:focus { opacity: 1; }
.aetext-row-validation { color: #c62828; font-size: 12px; white-space: pre-wrap; margin-top: 3px; }
</style>
"""
        )

        unsaved_dialog = ui.dialog().props("persistent")
        with unsaved_dialog, ui.card().classes("w-[460px] max-w-[92vw] gap-3"):
            ui.label("有未保存的更改").classes("text-lg font-semibold")
            ui.label("继续当前操作前，请保存或放弃当前插件、当前语言的草稿。")
            with ui.row().classes("w-full justify-end gap-2"):
                ui.button("取消", on_click=lambda: unsaved_dialog.submit("cancel")).props("flat")
                ui.button(
                    "放弃并继续",
                    on_click=lambda: unsaved_dialog.submit("discard"),
                ).props("flat color=negative")
                ui.button(
                    "保存并继续",
                    on_click=lambda: unsaved_dialog.submit("save"),
                ).props("color=primary")

        def project_by_name(name: str | None):
            return next(
                (project for project in service.workspace.projects if project.name == name),
                None,
            )

        async def guard_unsaved(action: Callable[[], Awaitable[None]]) -> bool:
            dirty = bool(await ui.run_javascript("return Boolean(window.aetextDirty)"))
            if dirty:
                choice = await unsaved_dialog
                if choice == "save":
                    if save_current is None or not await save_current():
                        return False
                elif choice == "discard":
                    await ui.run_javascript("window.aetextDrafts = {}; window.aetextDirty = false;")
                else:
                    return False
            await action()
            return True

        def render_tree() -> None:
            tree_container.clear()
            with tree_container:
                nodes = project_tree_nodes(service.workspace, selected_locale, search_value)

                async def select_node(event) -> None:
                    project_name = project_name_from_node(event.value)
                    if project_name is None or project_name == selected_project:
                        return

                    async def apply_selection() -> None:
                        nonlocal selected_project
                        selected_project = project_name
                        render_editor()

                    if not await guard_unsaved(apply_selection):
                        tree.value = (
                            f"project:{selected_project}" if selected_project is not None else None
                        )

                tree = ui.tree(nodes, on_select=select_node).props("dense no-connectors")
                tree.expand()
                if selected_project is not None:
                    tree.value = f"project:{selected_project}"

        def show_diagnostics(items: list[dict[str, object]]) -> None:
            errors = [item for item in items if item.get("severity") == "error"]
            if not errors:
                return
            ui.markdown(
                "\n".join(f"- `{item.get('code')}` {item.get('message')}" for item in errors)
            ).classes("w-full text-sm")

        async def perform_scan_current() -> None:
            nonlocal current_session
            if selected_project is None:
                ui.notify("请先选择插件", type="warning")
                return
            project = project_by_name(selected_project)
            if project is None or project.catalog_kind != "source-derived":
                ui.notify("该项目尚不能建立 source-derived 索引", type="warning")
                return
            notice = ui.notification(
                message=f"正在扫描 {selected_project}…",
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
                ui.notify(f"扫描失败：{error}", type="negative")
                render_tree()
                render_editor()
                return
            notice.dismiss()
            ui.notify("源码索引已更新", type="positive")
            render_tree()
            render_editor()

        async def scan_current() -> None:
            await guard_unsaved(perform_scan_current)

        async def perform_scan_all() -> None:
            progress_state: dict[str, object] = {"current": 0, "total": 1, "name": "准备中"}
            cancel_event = threading.Event()
            with ui.dialog() as progress_dialog, ui.card().classes("w-96 gap-3"):
                ui.label("扫描所有可迁移插件源码").classes("font-medium")
                progress_label = ui.label("准备中")
                progress_bar = ui.linear_progress(value=0)
                ui.button("取消", on_click=cancel_event.set).props("flat")

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
                    "扫描完成，失败：" + "、".join(item.project for item in failures),
                    type="warning",
                )
            elif result.cancelled:
                ui.notify("扫描已取消", type="warning")
            else:
                ui.notify("全部源码索引已更新", type="positive")
            render_tree()
            render_editor()

        async def scan_all() -> None:
            await guard_unsaved(perform_scan_all)

        async def perform_reload_catalogs() -> None:
            nonlocal selected_project
            await asyncio.to_thread(service.reload_catalogs)
            if project_by_name(selected_project) is None:
                selected_project = _initial_project(service, None)
            ui.notify("翻译文件已重新读取", type="positive")
            render_tree()
            render_editor()

        async def reload_catalogs() -> None:
            await guard_unsaved(perform_reload_catalogs)

        def render_ready_editor(session: ReviewSession) -> None:
            nonlocal current_session, save_current
            current_session = session
            ui.run_javascript("window.aetextDrafts = {}; window.aetextDirty = false;")
            ui.label(session.project.name).classes("text-2xl font-semibold")
            ui.label(f"{selected_locale} · {len(session.rows)} 项").classes("text-sm text-gray-600")
            summary_label = ui.label(summary(session)).classes("text-sm text-gray-600")

            active_content: set[str] = set()
            active_stages: set[str] = set()
            active_roles = tuple(role for role in ROLE_ORDER if rows_for_section(session, role))
            grid_holder: dict[str, object] = {}
            expansion_holder: dict[str, object] = {}
            content_chip_holder: dict[str, object] = {}
            stage_chip_holder: dict[str, object] = {}
            dirty_roles: set[str] = set()
            content_counts = content_status_counts(session)
            stage_counts = workflow_stage_counts(session)

            def section_title(role: str, current: ReviewSession | None = None) -> str:
                active_session = current or current_session or session
                dirty = "  ● 未保存" if role in dirty_roles else ""
                return f"{ROLE_LABELS[role]}  {section_summary(active_session, role)}{dirty}"

            def mark_dirty(role: str) -> None:
                dirty_roles.add(role)
                expansion = expansion_holder.get(role)
                if expansion is not None:
                    expansion.set_text(section_title(role))
                ui.run_javascript("window.aetextDirty = true")

            async def filter_all(column: str, model: dict[str, object] | None) -> None:
                for grid in grid_holder.values():
                    await grid.run_grid_method("setColumnFilterModel", column, model)
                    await grid.run_grid_method("onFilterChanged")

            with ui.row().classes("items-center gap-2"):
                ui.label("筛选：").classes("text-sm")

                async def filter_content(status: str, selected: bool) -> None:
                    (active_content.add if selected else active_content.discard)(status)
                    values = content_filter_values(active_content)
                    await filter_all(
                        "content_status_label",
                        community_text_filter(values),
                    )

                for status, label in CONTENT_STATUS_LABELS.items():
                    if status == "unscanned":
                        continue
                    content_chip_holder[status] = ui.chip(
                        f"{label} {content_counts[status]}",
                        selectable=True,
                        on_selection_change=lambda event, value=status: filter_content(
                            value, bool(event.value)
                        ),
                    ).props("outline dense")
                if session.workflow.enabled:

                    async def filter_stage(stage_id: str, selected: bool) -> None:
                        (active_stages.add if selected else active_stages.discard)(stage_id)
                        await filter_all(
                            "workflow_stage",
                            community_stage_filter(active_stages),
                        )

                    stage_chip_holder[""] = ui.chip(
                        f"无 {stage_counts['']}",
                        selectable=True,
                        color="grey",
                        on_selection_change=lambda event: filter_stage("", bool(event.value)),
                    ).props("outline dense")
                    for stage in session.workflow.stages:
                        label = stage.label if stage.enabled else f"{stage.label}（已停用）"

                        stage_chip_holder[stage.id] = ui.chip(
                            f"{label} {stage_counts.get(stage.id, 0)}",
                            selectable=True,
                            color=stage.color,
                            on_selection_change=lambda event, value=stage.id: filter_stage(
                                value, bool(event.value)
                            ),
                        ).props("outline dense")

            popup_state: dict[str, object] = {
                "role": "",
                "row_id": "",
                "stable_id": "",
                "original_items": [],
                "items": [],
                "initial_errors": [],
            }
            popup_dialog = ui.dialog()

            async def apply_popup_translation() -> None:
                original_items = list(popup_state["original_items"])
                items = list(popup_state["items"])
                original = "|".join(str(item) for item in original_items)
                translated = "|".join(str(item) for item in items)
                if popup_structure_errors(original, translated):
                    ui.notify("下拉菜单结构仍有错误", type="negative")
                    return
                role = str(popup_state["role"])
                await grid_holder[role].run_row_method(
                    str(popup_state["row_id"]),
                    "setDataValue",
                    "translation",
                    translated,
                )
                popup_dialog.close()

            with popup_dialog:

                @ui.refreshable
                def popup_editor_content() -> None:
                    original_items = list(popup_state["original_items"])
                    items = list(popup_state["items"])
                    with ui.card().classes("w-[720px] max-w-[95vw] gap-3"):
                        ui.label("编辑下拉菜单项").classes("text-xl font-semibold")
                        ui.label(
                            f"{popup_state['stable_id']} · 共 {len(original_items)} 项"
                        ).classes("text-sm text-gray-600")
                        initial_errors = list(popup_state["initial_errors"])
                        if initial_errors:
                            ui.label(
                                "现有译文结构不一致；请确认各项后再应用："
                                + "；".join(str(item) for item in initial_errors)
                            ).classes("text-sm text-orange-800 bg-orange-50 p-2 rounded")

                        feedback_error = None
                        feedback_ok = None
                        preview = None
                        apply_button = None

                        def refresh_feedback() -> None:
                            translated = "|".join(str(item) for item in popup_state["items"])
                            original = "|".join(str(item) for item in popup_state["original_items"])
                            errors = popup_structure_errors(original, translated)
                            preview.text = f"序列化预览：{translated}"
                            feedback_error.text = "；".join(errors)
                            feedback_error.set_visibility(bool(errors))
                            feedback_ok.set_visibility(not errors)
                            (apply_button.disable if errors else apply_button.enable)()

                        def update_item(index: int, value: str) -> None:
                            current = list(popup_state["items"])
                            current[index] = value
                            popup_state["items"] = current
                            refresh_feedback()

                        with ui.column().classes("w-full gap-2"):
                            for index, original_item in enumerate(original_items):
                                with ui.row().classes("w-full items-center gap-3 no-wrap"):
                                    ui.label(str(index + 1)).classes(
                                        "w-7 h-7 rounded-full bg-grey-3 text-center pt-1"
                                    )
                                    if original_item == POPUP_SEPARATOR:
                                        ui.label("—— 分隔符（结构只读）——").classes(
                                            "grow text-gray-600 italic"
                                        )
                                    elif original_item == "":
                                        ui.label("空项（结构只读）").classes(
                                            "grow text-gray-500 italic"
                                        )
                                    else:
                                        ui.label(original_item).classes(
                                            "w-52 text-sm text-gray-600 break-words"
                                        )
                                        ui.input(
                                            value=str(items[index]),
                                            on_change=lambda event, item_index=index: update_item(
                                                item_index, str(event.value)
                                            ),
                                        ).props("outlined dense").classes("grow")

                        ui.separator()
                        preview = ui.label().classes("text-xs text-gray-600 break-all")
                        feedback_error = ui.label().classes("text-sm text-red-700")
                        feedback_ok = ui.label("结构有效").classes("text-sm text-green-700")
                        with ui.row().classes("w-full justify-end gap-2"):
                            ui.button("取消", on_click=popup_dialog.close).props("flat")
                            apply_button = ui.button(
                                "应用到译文",
                                icon="check",
                                on_click=apply_popup_translation,
                            ).props("color=primary")
                        refresh_feedback()

                popup_editor_content()

            def open_popup_editor(role: str, event) -> None:
                data = event.args.get("data") or {}
                if data.get("use_source"):
                    ui.notify("请先取消“使用原文”", type="warning")
                    return
                original = str(data.get("original") or "")
                translation_value = data.get("translation")
                translation = translation_value if isinstance(translation_value, str) else ""
                original_items = split_popup(original)
                translated_items = split_popup(translation)
                items: list[str] = []
                for index, original_item in enumerate(original_items):
                    if original_item in {"", POPUP_SEPARATOR}:
                        items.append(original_item)
                    else:
                        items.append(
                            translated_items[index] if index < len(translated_items) else ""
                        )
                popup_state.update(
                    role=role,
                    row_id=str(event.args.get("rowId") or data.get("stable_id") or ""),
                    stable_id=str(data.get("stable_id") or ""),
                    original_items=original_items,
                    items=items,
                    initial_errors=popup_structure_errors(original, translation),
                )
                popup_editor_content.refresh()
                popup_dialog.open()

            for role in active_roles:
                role_rows = rows_for_section(session, role)
                title = section_title(role)
                expansion = ui.expansion(title, value=True, icon="table_rows").classes(
                    "w-full border rounded"
                )
                expansion_holder[role] = expansion
                with expansion:
                    grid = ui.aggrid(
                        grid_options_for_section(session, role),
                        modules="community",
                        auto_size_columns=False,
                    ).classes("w-full")
                    grid.style(f"height: {min(max(180, 76 + len(role_rows) * 44), 520)}px")

                    async def grid_changed(event, grid_role=role, current_grid=grid) -> None:
                        mark_dirty(grid_role)
                        if event.args.get("colId") == "use_source":
                            await current_grid.run_grid_method("refreshCells", {"force": True})

                    grid.on("cellValueChanged", grid_changed)
                    grid.on(
                        "popupEditRequested",
                        lambda event, grid_role=role: open_popup_editor(grid_role, event),
                    )
                    grid_holder[role] = grid

            async def collect_rows() -> list[dict[str, object]]:
                rows: list[dict[str, object]] = []
                for role in active_roles:
                    rows.extend(await grid_holder[role].get_client_data(method="all_unsorted"))
                drafts = await ui.run_javascript("return {...(window.aetextDrafts || {})}")
                for row in rows:
                    stable_id = str(row["stable_id"])
                    if stable_id in drafts:
                        row["translation"] = str(drafts[stable_id])
                return rows

            async def collect_selected_rows() -> list[dict[str, object]]:
                rows: list[dict[str, object]] = []
                for role in active_roles:
                    rows.extend(await grid_holder[role].get_selected_rows())
                return rows

            async def update_grid_rows(rows: list[dict[str, object]]) -> None:
                for role in active_roles:
                    changed_rows = [row for row in rows if str(row["primary_role"]) == role]
                    if not changed_rows:
                        continue
                    grid = grid_holder[role]
                    await grid.run_grid_method(
                        "applyTransactionAsync",
                        {"update": changed_rows},
                    )
                    await grid.run_grid_method("flushAsyncTransactions")

            async def patch_saved_derived_fields(
                before_rows: list[dict[str, object]],
                saved_session: ReviewSession,
            ) -> None:
                before_by_id = {str(row["stable_id"]): row for row in before_rows}
                for saved_row in all_row_data(saved_session):
                    stable_id = str(saved_row["stable_id"])
                    before = before_by_id[stable_id]
                    grid = grid_holder[str(saved_row["primary_role"])]
                    if before.get("validation_message") != saved_row.get("validation_message"):
                        await grid.run_row_method(stable_id, "updateData", saved_row)
                        continue
                    fields = ["content_status", "content_status_label"]
                    if saved_session.workflow.enabled:
                        fields.append("workflow_stage")
                    for field in fields:
                        if before.get(field) != saved_row.get(field):
                            await grid.run_row_method(
                                stable_id,
                                "setDataValue",
                                field,
                                saved_row.get(field),
                            )

            async def show_inline_diagnostics(items: list[dict[str, object]]) -> None:
                messages: dict[str, list[str]] = {}
                for item in items:
                    if item.get("severity") != "error" or item.get("locale") != selected_locale:
                        continue
                    stable_id = str(item.get("stableId") or "")
                    if stable_id:
                        messages.setdefault(stable_id, []).append(str(item.get("message") or ""))
                client_rows = {str(row["stable_id"]): row for row in await collect_rows()}
                for role in active_roles:
                    for row in rows_for_section(session, role):
                        client_row = client_rows[row.stable_id]
                        client_row["validation_message"] = "\n".join(
                            messages.get(row.stable_id, [])
                        )
                        await grid_holder[role].run_row_method(
                            row.stable_id,
                            "updateData",
                            client_row,
                        )
                    await grid_holder[role].run_grid_method("refreshCells", {"force": True})

            async def apply_stage(stage: str | None, scope: str) -> None:
                rows = await collect_rows()
                if scope == "selected":
                    selected = await collect_selected_rows()
                    if not selected:
                        ui.notify("请先选择至少一行", type="warning")
                        return
                    target_ids = {str(row["stable_id"]) for row in selected}
                elif scope == "all":
                    target_ids = {str(row["stable_id"]) for row in rows}
                else:
                    raise ValueError(f"unknown stage scope: {scope}")
                changed_rows: list[dict[str, object]] = []
                for row in rows:
                    if str(row["stable_id"]) not in target_ids:
                        continue
                    current_stage = row.get("workflow_stage") or None
                    if current_stage == stage:
                        continue
                    row["workflow_stage"] = stage
                    changed_rows.append(row)
                await update_grid_rows(changed_rows)
                for role in {str(row["primary_role"]) for row in changed_rows}:
                    mark_dirty(role)

            if session.workflow.enabled:
                enabled = {
                    stage.id: stage.label for stage in session.workflow.stages if stage.enabled
                }
                apply_all_dialog = ui.dialog()
                with ui.row().classes("items-end gap-2"):
                    batch_stage = ui.select(
                        {"": "无", **enabled},
                        value="",
                        label="批量设置阶段",
                    ).classes("w-48")
                    ui.button(
                        "应用到所选",
                        on_click=lambda: apply_stage(batch_stage.value or None, "selected"),
                    ).props("outline")
                    ui.button(
                        f"应用到全部 {len(session.rows)} 项",
                        on_click=apply_all_dialog.open,
                    ).props("outline")

                with apply_all_dialog, ui.card().classes("w-96 gap-3"):
                    ui.label("确认批量设置阶段").classes("text-lg font-semibold")
                    ui.label(
                        f"将应用到当前插件、当前语言的全部 {len(session.rows)} 项，"
                        "包括折叠或筛选隐藏的条目。"
                    )

                    async def apply_all_confirmed() -> None:
                        apply_all_dialog.close()
                        await apply_stage(batch_stage.value or None, "all")

                    with ui.row().classes("w-full justify-end gap-2"):
                        ui.button("取消", on_click=apply_all_dialog.close).props("flat")
                        ui.button(
                            "确认应用到全部",
                            on_click=apply_all_confirmed,
                        ).props("color=primary")

            async def save() -> bool:
                nonlocal current_session
                for grid in grid_holder.values():
                    await grid.run_grid_method("stopEditing")
                rows = await collect_rows()
                try:
                    current_session = service.save_locale(current_session, rows)
                except ReviewValidationError as error:
                    ui.notify("存在结构或编码错误，未保存", type="negative")
                    await show_inline_diagnostics(error.diagnostics)
                    show_diagnostics(error.diagnostics)
                    return False
                except Exception as error:
                    ui.notify(
                        f"保存失败，磁盘内容未覆盖：{error}",
                        type="negative",
                    )
                    return False
                await patch_saved_derived_fields(rows, current_session)
                await ui.run_javascript("window.aetextDrafts = {};")
                summary_label.text = summary(current_session)
                saved_content_counts = content_status_counts(current_session)
                for status, chip in content_chip_holder.items():
                    chip.set_text(f"{CONTENT_STATUS_LABELS[status]} {saved_content_counts[status]}")
                saved_stage_counts = workflow_stage_counts(current_session)
                if "" in stage_chip_holder:
                    stage_chip_holder[""].set_text(f"无 {saved_stage_counts['']}")
                for stage in current_session.workflow.stages:
                    label = stage.label if stage.enabled else f"{stage.label}（已停用）"
                    stage_chip_holder[stage.id].set_text(
                        f"{label} {saved_stage_counts.get(stage.id, 0)}"
                    )
                dirty_roles.clear()
                for role in active_roles:
                    expansion_holder[role].set_text(section_title(role, current_session))
                await ui.run_javascript("window.aetextDirty = false;")
                ui.notify("已保存当前插件的当前语言", type="positive")
                return True

            save_current = save
            ui.button("保存当前语言", icon="save", on_click=save).props("color=primary")
            show_diagnostics(session.diagnostics)

        def render_editor() -> None:
            nonlocal current_session, save_current
            current_session = None
            save_current = None
            editor_container.clear()
            project = project_by_name(selected_project)
            with editor_container:
                if project is None:
                    ui.label("请选择左侧插件").classes("text-xl text-gray-500")
                    return
                if project.scan_state == "legacy":
                    ui.label(project.name).classes("text-2xl font-semibold")
                    ui.label("该插件仍使用迁移期 bindings，完成等价迁移后才开放检阅。")
                    ui.label(str(project.catalog_path)).classes("text-xs text-gray-500")
                    return
                if project.scan_state == "settings":
                    ui.label(project.name).classes("text-2xl font-semibold")
                    ui.label("支持工具使用独立 Settings catalog，不在效果翻译工作区编辑。")
                    return
                if project.scan_state in {"invalid", "error"}:
                    ui.label(project.name).classes("text-2xl font-semibold")
                    ui.label("Catalog 或源码缓存无效，请修正或重新扫描。")
                    if project.catalog_kind == "source-derived":
                        ui.button("扫描当前插件", icon="refresh", on_click=scan_current)
                    return
                if project.scan_state == "unscanned":
                    ui.label(project.name).classes("text-2xl font-semibold")
                    ui.label("尚未建立源码索引。").classes("text-lg")
                    ui.label("选择扫描当前插件后，才会调用 MSBuild 和 Tree-sitter。")
                    ui.button("扫描当前插件", icon="document_scanner", on_click=scan_current).props(
                        "color=primary"
                    )
                    return
                try:
                    session = service.open_cached_project(project.name, selected_locale)
                except ReviewUnavailableError as error:
                    ui.label(str(error)).classes("text-negative")
                    return
                render_ready_editor(session)

        def workflow_saved() -> None:
            render_tree()
            render_editor()

        open_workflow_settings = create_workflow_dialog(service, workflow_saved)

        async def guarded_open_workflow_settings() -> None:
            async def open_dialog() -> None:
                open_workflow_settings()

            await guard_unsaved(open_dialog)

        with ui.header().classes("items-center gap-4 px-4"):
            ui.label("AeText").classes("text-xl font-semibold")

            async def change_locale(event) -> None:
                requested_locale = str(event.value)
                if requested_locale == selected_locale:
                    return

                async def apply_locale() -> None:
                    nonlocal selected_locale
                    selected_locale = requested_locale
                    render_tree()
                    render_editor()

                if not await guard_unsaved(apply_locale):
                    locale_select.set_value(selected_locale)

            locale_select = ui.select(
                locales,
                value=selected_locale,
                label="语言",
                on_change=change_locale,
            ).classes("w-44")

            def change_search(event) -> None:
                nonlocal search_value
                search_value = str(event.value or "")
                render_tree()

            ui.input("搜索插件名", on_change=change_search).props("clearable dense").classes("w-64")
            with ui.dropdown_button("扫描", icon="document_scanner", auto_close=True):
                ui.menu_item("扫描当前插件源码", on_click=scan_current)
                ui.menu_item("扫描所有插件源码", on_click=scan_all)
                ui.menu_item("重新读取翻译文件", on_click=reload_catalogs)
            ui.button(
                "工作流设置",
                icon="tune",
                on_click=guarded_open_workflow_settings,
            ).props("flat")

        with ui.left_drawer(value=True, bordered=True).props("width=360"):
            tree_container = ui.column().classes("w-full p-2")
        editor_container = ui.column().classes("w-full p-5 gap-3")
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
