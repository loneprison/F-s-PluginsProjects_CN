"""Fixed-order Popup item editor shared by all workspace sections."""

from collections.abc import Callable

from nicegui import ui

from ..catalog.popup import POPUP_SEPARATOR, popup_structure_issues, split_popup
from .i18n import UiText


def create_popup_editor(grids: dict[str, object], get_text: Callable[[], UiText]):
    popup_state: dict[str, object] = {
        "role": "",
        "row_id": "",
        "stable_id": "",
        "original_items": [],
        "items": [],
        "initial_issues": [],
    }
    popup_dialog = ui.dialog()

    async def apply_popup_translation() -> None:
        text = get_text()
        original_items = list(popup_state["original_items"])
        items = list(popup_state["items"])
        original = "|".join(str(item) for item in original_items)
        translated = "|".join(str(item) for item in items)
        if popup_structure_issues(original, translated):
            ui.notify(text.text("popup.structure_error"), type="negative")
            return
        role = str(popup_state["role"])
        await grids[role].run_row_method(
            str(popup_state["row_id"]),
            "setDataValue",
            "translation",
            translated,
        )
        popup_dialog.close()

    with popup_dialog:

        @ui.refreshable
        def popup_editor_content() -> None:
            text = get_text()
            original_items = list(popup_state["original_items"])
            items = list(popup_state["items"])
            with ui.card().classes("w-[720px] max-w-[95vw] gap-3"):
                ui.label(text.text("popup.title")).classes("text-xl font-semibold")
                ui.label(
                    text.text(
                        "popup.item_count",
                        stable_id=popup_state["stable_id"],
                        count=len(original_items),
                    )
                ).classes("text-sm text-gray-600")
                initial_issues = list(popup_state["initial_issues"])
                if initial_issues:
                    ui.label(
                        text.text(
                            "popup.existing_invalid",
                            errors="; ".join(text.popup_issue(item) for item in initial_issues),
                        )
                    ).classes("text-sm text-orange-800 bg-orange-50 p-2 rounded")

                feedback_error = None
                feedback_ok = None
                preview = None
                apply_button = None

                def refresh_feedback() -> None:
                    translated = "|".join(str(item) for item in popup_state["items"])
                    original = "|".join(str(item) for item in popup_state["original_items"])
                    issues = popup_structure_issues(original, translated)
                    preview.text = text.text("popup.preview", value=translated)
                    feedback_error.text = "; ".join(text.popup_issue(item) for item in issues)
                    feedback_error.set_visibility(bool(issues))
                    feedback_ok.set_visibility(not issues)
                    (apply_button.disable if issues else apply_button.enable)()

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
                                ui.label(text.text("popup.separator_readonly")).classes(
                                    "grow text-gray-600 italic"
                                )
                            elif original_item == "":
                                ui.label(text.text("popup.empty_readonly")).classes(
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
                feedback_ok = ui.label(text.text("popup.valid")).classes("text-sm text-green-700")
                with ui.row().classes("w-full justify-end gap-2"):
                    ui.button(
                        text.text("common.cancel"),
                        on_click=popup_dialog.close,
                    ).props("flat")
                    apply_button = ui.button(
                        text.text("popup.apply"),
                        icon="check",
                        on_click=apply_popup_translation,
                    ).props("color=primary")
                refresh_feedback()

        popup_editor_content()

    def open_popup_editor(role: str, event) -> None:
        text = get_text()
        data = event.args.get("data") or {}
        if data.get("use_source"):
            ui.notify(text.text("popup.disable_use_source"), type="warning")
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
                items.append(translated_items[index] if index < len(translated_items) else "")
        popup_state.update(
            role=role,
            row_id=str(event.args.get("rowId") or data.get("stable_id") or ""),
            stable_id=str(data.get("stable_id") or ""),
            original_items=original_items,
            items=items,
            initial_issues=popup_structure_issues(original, translation),
        )
        popup_editor_content.refresh()
        popup_dialog.open()

    return open_popup_editor
