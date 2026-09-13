"""Data-driven family workflow settings dialog."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from nicegui import ui

from ..catalog.review import ReviewWorkspaceService
from .i18n import SUPPORTED_UI_LOCALES, UiText


def create_workflow_dialog(
    service: ReviewWorkspaceService,
    on_saved: Callable[[], Awaitable[None]],
    get_text: Callable[[], UiText],
) -> Callable[[], None]:
    dialog = ui.dialog()
    state: dict[str, object] = {}

    def reset() -> None:
        document = service.workflow.model_dump(by_alias=True)
        state.clear()
        state.update(document)

    def move(index: int, delta: int) -> None:
        stages = state["stages"]
        target = index + delta
        if 0 <= target < len(stages):
            stages[index], stages[target] = stages[target], stages[index]
            render()

    def display_label(stage: dict[str, object]) -> str:
        text = get_text()
        labels = stage["labels"]
        return str(labels.get(text.locale) or labels["en"])

    def update_label(labels: dict[str, object], locale: str, value: object) -> None:
        label = str(value or "")
        if locale == "en" or label:
            labels[locale] = label
        else:
            labels.pop(locale, None)

    def render() -> None:
        text = get_text()
        dialog.clear()
        stages = state["stages"]
        defaults = state["defaults"]
        source_change = state["sourceChange"]
        with dialog, ui.card().classes("w-[1100px] max-w-[96vw] gap-4"):
            ui.label(text.text("workflow.title")).classes("text-xl font-semibold")
            ui.switch(
                text.text("workflow.enabled"),
                value=bool(state["enabled"]),
                on_change=lambda event: state.update(enabled=bool(event.value)),
            )
            ui.label(text.text("workflow.order_color")).classes("font-medium")
            for index, stage in enumerate(stages):
                labels = stage["labels"]
                with ui.row().classes("w-full items-center gap-2"):
                    ui.input(text.text("workflow.id"), value=str(stage["id"])).props(
                        "readonly"
                    ).classes("w-36")
                    for locale in SUPPORTED_UI_LOCALES:
                        ui.input(
                            text.text(f"workflow.name.{locale}"),
                            value=str(labels.get(locale) or ""),
                            on_change=lambda event, item=labels, key=locale: update_label(
                                item, key, event.value
                            ),
                        ).classes("flex-1")
                    ui.input(
                        text.text("workflow.color"),
                        value=str(stage["color"]),
                        on_change=lambda event, item=stage: item.update(color=str(event.value)),
                    ).classes("w-28")
                    ui.switch(
                        text.text("workflow.stage_enabled"),
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
                ui.expansion(text.text("workflow.add_section"), icon="add").classes("w-full"),
                ui.row().classes("w-full items-end"),
            ):
                new_id = ui.input(text.text("workflow.id")).classes("w-40")
                new_labels = {
                    locale: ui.input(text.text(f"workflow.name.{locale}")).classes("flex-1")
                    for locale in SUPPORTED_UI_LOCALES
                }
                new_color = ui.input(text.text("workflow.color"), value="gray").classes("w-28")

                def add_stage() -> None:
                    labels = {
                        locale: str(element.value or "")
                        for locale, element in new_labels.items()
                        if locale == "en" or element.value
                    }
                    stages.append(
                        {
                            "id": str(new_id.value or ""),
                            "labels": labels,
                            "color": str(new_color.value or "gray"),
                            "enabled": True,
                        }
                    )
                    render()

                ui.button(text.text("workflow.add"), icon="add", on_click=add_stage)

            options = {
                "": text.text("common.none"),
                **{str(stage["id"]): display_label(stage) for stage in stages},
            }
            ui.select(
                {key: value for key, value in options.items() if key},
                label=text.text("workflow.completed"),
                value=str(state["completedStageId"]),
                on_change=lambda event: state.update(completedStageId=str(event.value)),
            ).classes("w-full")
            with ui.row().classes("w-full gap-4"):
                ui.select(
                    options,
                    label=text.text("workflow.manual_default"),
                    value=str(defaults.get("manualEdit") or ""),
                    on_change=lambda event: defaults.update(manualEdit=event.value or None),
                ).classes("flex-1")
                ui.select(
                    options,
                    label=text.text("workflow.pretranslation_default"),
                    value=str(defaults.get("pretranslation") or ""),
                    on_change=lambda event: defaults.update(pretranslation=event.value or None),
                ).classes("flex-1")

            ui.label(text.text("workflow.source_change")).classes("font-medium")
            for stage in stages:
                stage_id = str(stage["id"])
                with ui.row().classes("w-full items-center"):
                    ui.label(display_label(stage)).classes("w-40")

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
                text = get_text()
                try:
                    service.save_workflow_definition(state)
                except Exception as error:
                    ui.notify(text.text("workflow.invalid", error=error), type="negative")
                    return
                dialog.close()
                await on_saved()
                ui.notify(text.text("workflow.saved"), type="positive")

            with ui.row().classes("w-full justify-end"):
                ui.button(text.text("common.cancel"), on_click=dialog.close).props("flat")
                ui.button(text.text("workflow.save"), icon="save", on_click=save).props(
                    "color=primary"
                )

    def open_dialog() -> None:
        reset()
        render()
        dialog.open()

    return open_dialog
