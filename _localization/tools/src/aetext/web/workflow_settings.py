"""Data-driven family workflow settings dialog."""

from __future__ import annotations

from collections.abc import Callable

from nicegui import ui

from ..catalog.review import ReviewWorkspaceService


def create_workflow_dialog(
    service: ReviewWorkspaceService,
    on_saved: Callable[[], None],
) -> Callable[[], None]:
    dialog = ui.dialog()
    state: dict[str, object] = {}

    def reset() -> None:
        document = service.workflow.model_dump(by_alias=True)
        state.clear()
        state.update(document)

    def move(index: int, delta: int) -> None:
        stages = state["stages"]
        assert isinstance(stages, list)
        target = index + delta
        if 0 <= target < len(stages):
            stages[index], stages[target] = stages[target], stages[index]
            render()

    def render() -> None:
        dialog.clear()
        stages = state["stages"]
        defaults = state["defaults"]
        source_change = state["sourceChange"]
        assert isinstance(stages, list)
        assert isinstance(defaults, dict)
        assert isinstance(source_change, dict)
        with dialog, ui.card().classes("w-[760px] max-w-[92vw] gap-4"):
            ui.label("F's 审校工作流设置").classes("text-xl font-semibold")
            ui.switch(
                "启用审校流程",
                value=bool(state["enabled"]),
                on_change=lambda event: state.update(enabled=bool(event.value)),
            )
            ui.label("阶段顺序与颜色").classes("font-medium")
            for index, stage in enumerate(stages):
                assert isinstance(stage, dict)
                with ui.row().classes("w-full items-center gap-2"):
                    ui.input("ID", value=str(stage["id"])).props("readonly").classes("w-36")
                    ui.input(
                        "显示名称",
                        value=str(stage["label"]),
                        on_change=lambda event, item=stage: item.update(label=str(event.value)),
                    ).classes("flex-1")
                    ui.input(
                        "颜色",
                        value=str(stage["color"]),
                        on_change=lambda event, item=stage: item.update(color=str(event.value)),
                    ).classes("w-28")
                    ui.switch(
                        "启用",
                        value=bool(stage["enabled"]),
                        on_change=lambda event, item=stage: item.update(enabled=bool(event.value)),
                    )
                    ui.button(
                        icon="arrow_upward", on_click=lambda _, value=index: move(value, -1)
                    ).props("flat dense")
                    ui.button(
                        icon="arrow_downward",
                        on_click=lambda _, value=index: move(value, 1),
                    ).props("flat dense")

            with (
                ui.expansion("新增阶段", icon="add").classes("w-full"),
                ui.row().classes("w-full items-end"),
            ):
                new_id = ui.input("ID").classes("w-40")
                new_label = ui.input("显示名称").classes("flex-1")
                new_color = ui.input("颜色", value="gray").classes("w-28")

                def add_stage() -> None:
                    stages.append(
                        {
                            "id": str(new_id.value or ""),
                            "label": str(new_label.value or ""),
                            "color": str(new_color.value or "gray"),
                            "enabled": True,
                        }
                    )
                    render()

                ui.button("添加", icon="add", on_click=add_stage)

            options = {"": "无", **{str(stage["id"]): str(stage["label"]) for stage in stages}}
            ui.select(
                {key: value for key, value in options.items() if key},
                label="计为完成的阶段",
                value=str(state["completedStageId"]),
                on_change=lambda event: state.update(completedStageId=str(event.value)),
            ).classes("w-full")
            with ui.row().classes("w-full gap-4"):
                ui.select(
                    options,
                    label="手工编辑后的默认阶段",
                    value=str(defaults.get("manualEdit") or ""),
                    on_change=lambda event: defaults.update(manualEdit=event.value or None),
                ).classes("flex-1")
                ui.select(
                    options,
                    label="预翻译默认阶段",
                    value=str(defaults.get("pretranslation") or ""),
                    on_change=lambda event: defaults.update(pretranslation=event.value or None),
                ).classes("flex-1")

            ui.label("原文变化时的阶段回退").classes("font-medium")
            for stage in stages:
                assert isinstance(stage, dict)
                stage_id = str(stage["id"])
                with ui.row().classes("w-full items-center"):
                    ui.label(str(stage["label"])).classes("w-40")

                    def update_source_change(event, source=stage_id) -> None:
                        if event.value:
                            source_change[source] = event.value
                        else:
                            source_change.pop(source, None)

                    ui.select(
                        options,
                        value=str(source_change.get(stage_id) or ""),
                        on_change=update_source_change,
                    ).classes("flex-1")

            async def save() -> None:
                try:
                    service.save_workflow_definition(state)
                except Exception as error:
                    ui.notify(f"工作流设置无效：{error}", type="negative")  # noqa: RUF001
                    return
                dialog.close()
                on_saved()
                ui.notify("工作流设置已保存", type="positive")

            with ui.row().classes("w-full justify-end"):
                ui.button("取消", on_click=dialog.close).props("flat")
                ui.button("保存设置", icon="save", on_click=save).props("color=primary")

    def open_dialog() -> None:
        reset()
        render()
        dialog.open()

    return open_dialog
