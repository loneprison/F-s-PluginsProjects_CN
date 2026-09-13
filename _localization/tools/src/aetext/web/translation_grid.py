"""Per-Role AG Grid configuration for one cached review session."""

from __future__ import annotations

import json

from ..catalog.review import ReviewRow, ReviewSession
from ..core.scanner_contract import ROLE_ORDER as ROLE_INDEX
from .i18n import UiText

CONTENT_STATUSES = ("missing", "use-source", "valid", "error", "unscanned")
ROLE_ORDER = (*tuple(sorted(ROLE_INDEX, key=ROLE_INDEX.__getitem__)), "Settings")
STAGE_OPTION_MARKERS = {
    "black": "⚫",
    "blue": "🔵",
    "brown": "🟤",
    "gray": "⚪",
    "green": "🟢",
    "grey": "⚪",
    "orange": "🟠",
    "purple": "🟣",
    "red": "🔴",
    "yellow": "🟡",
}


def row_data(row: ReviewRow, text: UiText) -> dict[str, object]:
    result = row.model_dump()
    result["content_status_label"] = text.text(f"status.{row.content_status}")
    result["panel_order_display"] = row.panel_order + 1
    result["popup_item_count"] = len(row.original.split("|")) if row.primary_role == "Popup" else 0
    result["validation_message"] = "\n".join(
        text.diagnostic(item) for item in row.validation_diagnostics
    )
    result["review_change_message"] = " · ".join(
        text.text(f"review_change.{reason}") for reason in row.review_change_reasons
    )
    return result


def all_row_data(session: ReviewSession, text: UiText) -> list[dict[str, object]]:
    return [row_data(row, text) for row in session.rows]


def rows_for_section(session: ReviewSession, role: str) -> list[ReviewRow]:
    return [row for row in session.rows if row.primary_role == role]


def content_status_counts(session: ReviewSession) -> dict[str, int]:
    counts = {name: 0 for name in CONTENT_STATUSES}
    for row in session.rows:
        counts[row.content_status] += 1
    return counts


def workflow_stage_counts(session: ReviewSession) -> dict[str, int]:
    counts = {"": 0, **{stage.id: 0 for stage in session.workflow.stages}}
    for row in session.rows:
        counts[row.workflow_stage or ""] = counts.get(row.workflow_stage or "", 0) + 1
    return counts


def _translation_renderer(session: ReviewSession, text: UiText) -> str:
    messages = json.dumps(
        {
            "popupEdit": text.text("grid.popup_edit", count="{count}"),
            "popupDisabled": text.text("grid.popup_disabled"),
            "popupOpen": text.text("grid.popup_open"),
            "useSource": text.text("grid.use_source"),
            "enterTranslation": text.text("grid.enter_translation"),
            "translationAria": text.text("grid.translation_aria", stable_id="{stable_id}"),
            "validText": text.text("grid.valid_text"),
            "invalidText": text.text("grid.invalid_text"),
            "unsaved": text.text("editor.unsaved"),
            "workflowEnabled": session.workflow.enabled,
            "manualEditStage": session.workflow.defaults.manual_edit,
        },
        ensure_ascii=False,
    )
    template = r"""params => {
        const messages = __MESSAGES__;
        const wrapper = document.createElement('div');
        wrapper.className = 'aetext-translation-wrap';
        const main = document.createElement('div');
        main.className = 'aetext-translation-main';
        const validation = document.createElement('div');
        validation.className = 'aetext-row-validation';
        validation.textContent = params.data.validation_message || '';
        const clearValidation = () => {
          if (!params.data.validation_message) return;
          params.data.validation_message = '';
          validation.textContent = '';
        };
        if (params.data.primary_role === 'Popup') {
          const button = document.createElement('button');
          button.type = 'button';
          button.className = 'aetext-popup-button';
          button.textContent = messages.popupEdit.replace('{count}', params.data.popup_item_count);
          button.disabled = Boolean(params.data.use_source);
          button.title = button.disabled ? messages.popupDisabled : messages.popupOpen;
          button.addEventListener('click', event => {
            event.stopPropagation();
            params.api.dispatchEvent({
              type: 'popupEditRequested',
              data: params.data,
              node: params.node,
              column: params.column,
            });
          });
          main.append(button);
        } else {
          const multiline = ['About', 'Error'].includes(params.data.primary_role);
          const editor = document.createElement(multiline ? 'textarea' : 'input');
          if (!multiline) editor.type = 'text';
          if (multiline) editor.rows = 2;
          editor.className = 'aetext-translation-input';
          const drafts = window.aetextDrafts || (window.aetextDrafts = {});
          editor.value = Object.hasOwn(drafts, params.data.stable_id)
            ? drafts[params.data.stable_id]
            : (params.value ?? '');
          editor.disabled = Boolean(params.data.use_source);
          editor.placeholder = editor.disabled ? messages.useSource : messages.enterTranslation;
          editor.setAttribute(
            'aria-label', messages.translationAria.replace('{stable_id}', params.data.stable_id));
          const resize = () => {
            if (!multiline) return;
            editor.style.height = 'auto';
            editor.style.height = `${Math.max(52, editor.scrollHeight)}px`;
          };
          editor.addEventListener('input', () => {
            clearValidation();
            params.data.translation = editor.value;
            window.aetextDrafts[params.data.stable_id] = editor.value;
            window.aetextMarkEdit(params.data, false,
              messages.workflowEnabled ? messages.manualEditStage : undefined);
            params.api.refreshCells({
              rowNodes: [params.node], columns: ['workflow_stage'], force: true});
            params.api.dispatchEvent({
              type: 'draftChanged',
              data: params.data,
              node: params.node,
              column: params.column,
            });
            const expansion = editor.closest('.q-expansion-item');
            const title = expansion?.querySelector('.q-item__label');
            if (title && !title.textContent.includes(`● ${messages.unsaved}`)) {
              title.textContent += `  ● ${messages.unsaved}`;
            }
            resize();
          });
          editor.addEventListener('click', event => event.stopPropagation());
          main.append(editor);
          queueMicrotask(resize);
        }
        const isValid = ['valid', 'use-source'].includes(params.data.content_status);
        const validity = document.createElement('span');
        validity.className = `aetext-content-validity ${isValid ? 'is-valid' : 'is-invalid'}`;
        validity.textContent = isValid ? '✓' : '!';
        validity.title = isValid ? messages.validText : messages.invalidText;
        validity.setAttribute('aria-label', validity.title);
        validity.setAttribute('role', 'img');
        main.append(validity);
        wrapper.append(main);
        if (validation.textContent) wrapper.append(validation);
        return wrapper;
    }"""
    return template.replace("__MESSAGES__", messages)


def _original_renderer(text: UiText) -> str:
    messages = json.dumps(
        {
            "copy": text.text("grid.copy"),
            "copySource": text.text("grid.copy_source"),
            "copied": text.text("grid.copied"),
        },
        ensure_ascii=False,
    )
    template = r"""params => {
        const messages = __MESSAGES__;
        const wrapper = document.createElement('div');
        wrapper.className = 'aetext-original-wrap';
        wrapper.title = params.value ?? '';
        const text = document.createElement('span');
        text.className = 'aetext-original-text';
        text.textContent = params.value ?? '';
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'aetext-copy-button';
        button.textContent = messages.copy;
        button.title = messages.copySource;
        const copy = async event => {
          event.stopPropagation();
          try {
            await navigator.clipboard.writeText(params.value ?? '');
          } catch (_) {
            const helper = document.createElement('textarea');
            helper.value = params.value ?? '';
            helper.style.position = 'fixed';
            helper.style.opacity = '0';
            document.body.append(helper);
            helper.select();
            document.execCommand('copy');
            helper.remove();
          }
          Quasar.Notify.create({message: messages.copied, timeout: 900, position: 'top'});
        };
        wrapper.addEventListener('dblclick', copy);
        button.addEventListener('click', copy);
        wrapper.append(text, button);
        return wrapper;
    }"""
    return template.replace("__MESSAGES__", messages)


def _workflow_renderer(session: ReviewSession, text: UiText) -> str:
    stage_options = [
        {
            "id": "",
            "label": text.text("common.none"),
            "color": "grey",
            "menuMarker": STAGE_OPTION_MARKERS["grey"],
            "enabled": True,
        },
        *[
            {
                "id": stage.id,
                "label": (
                    text.stage_label(stage)
                    if stage.enabled
                    else text.text("common.disabled", label=text.stage_label(stage))
                ),
                "color": stage.color,
                "menuMarker": STAGE_OPTION_MARKERS.get(stage.color.lower(), "●"),
                "enabled": stage.enabled,
            }
            for stage in session.workflow.stages
        ],
    ]
    return f"""params => {{
        const stages = {json.dumps(stage_options, ensure_ascii=False)};
        const wrapper = document.createElement('div');
        wrapper.className = 'aetext-stage-wrap';
        const control = document.createElement('div');
        control.className = 'aetext-stage-control';
        const select = document.createElement('select');
        select.className = 'aetext-stage-select';
        select.tabIndex = -1;
        select.setAttribute('aria-hidden', 'true');
        const trigger = document.createElement('button');
        trigger.type = 'button';
        trigger.className = 'aetext-stage-trigger';
        trigger.setAttribute('aria-haspopup', 'listbox');
        trigger.setAttribute('aria-expanded', 'false');
        const indicator = document.createElement('span');
        indicator.className = 'aetext-stage-indicator';
        indicator.setAttribute('aria-hidden', 'true');
        const label = document.createElement('span');
        label.className = 'aetext-stage-label';
        label.setAttribute('aria-hidden', 'true');
        const chevron = document.createElement('span');
        chevron.className = 'aetext-stage-chevron';
        chevron.setAttribute('aria-hidden', 'true');
        const menu = document.createElement('div');
        menu.className = 'aetext-stage-menu';
        menu.setAttribute('role', 'listbox');
        menu.hidden = true;
        const current = params.value ?? '';
        const resolveStageColor = stage => {{
          const configuredColor = getComputedStyle(document.documentElement)
            .getPropertyValue(`--q-${{stage.color}}`).trim() || stage.color;
          return CSS.supports('color', configuredColor) ? configuredColor : '#6b7280';
        }};
        for (const stage of stages) {{
          const option = document.createElement('option');
          option.value = stage.id;
          option.textContent = `${{stage.menuMarker}} ${{stage.label}}`;
          option.disabled = !stage.enabled && stage.id !== current;
          select.append(option);
          const menuOption = document.createElement('button');
          menuOption.type = 'button';
          menuOption.className = 'aetext-stage-menu-option';
          menuOption.dataset.value = stage.id;
          menuOption.setAttribute('role', 'option');
          menuOption.disabled = option.disabled;
          const menuIndicator = document.createElement('span');
          menuIndicator.className = 'aetext-stage-menu-indicator';
          menuIndicator.setAttribute('aria-hidden', 'true');
          menuIndicator.style.backgroundColor = resolveStageColor(stage);
          const menuLabel = document.createElement('span');
          menuLabel.className = 'aetext-stage-menu-label';
          menuLabel.textContent = stage.label;
          menuOption.append(menuIndicator, menuLabel);
          menu.append(menuOption);
        }}
        select.value = current;
        const applyState = () => {{
          const stage = stages.find(item => item.id === select.value) ?? stages[0];
          indicator.style.backgroundColor = resolveStageColor(stage);
          label.textContent = stage.label;
          select.setAttribute('aria-label', stage.label);
          trigger.setAttribute('aria-label', stage.label);
          control.title = stage.label;
          control.style.opacity = stage.enabled ? '1' : '0.65';
          for (const menuOption of menu.querySelectorAll('.aetext-stage-menu-option')) {{
            const selected = menuOption.dataset.value === select.value;
            menuOption.classList.toggle('is-selected', selected);
            menuOption.setAttribute('aria-selected', String(selected));
          }}
        }};
        let menuOpen = false;
        const closeMenu = (restoreFocus = false) => {{
          if (!menuOpen) return;
          menuOpen = false;
          menu.hidden = true;
          menu.remove();
          trigger.setAttribute('aria-expanded', 'false');
          document.removeEventListener('pointerdown', closeOnOutside, true);
          document.removeEventListener('keydown', closeOnKeydown);
          window.removeEventListener('resize', closeOnViewport);
          window.removeEventListener('scroll', closeOnViewport, true);
          if (window.__aetextStageMenuClose === closeMenu) {{
            window.__aetextStageMenuClose = null;
          }}
          if (restoreFocus) trigger.focus();
        }};
        const closeOnOutside = event => {{
          if (!control.contains(event.target) && !menu.contains(event.target)) closeMenu();
        }};
        const closeOnViewport = () => closeMenu();
        const closeOnKeydown = event => {{
          if (event.key === 'Escape') closeMenu(true);
        }};
        const positionMenu = () => {{
          const rect = control.getBoundingClientRect();
          const width = rect.width;
          menu.style.width = `${{width}}px`;
          const menuHeight = menu.getBoundingClientRect().height;
          const below = rect.bottom + 2;
          const top = below + menuHeight <= window.innerHeight - 8
            ? below : Math.max(8, rect.top - menuHeight - 2);
          const left = Math.min(
            Math.max(8, rect.left), Math.max(8, window.innerWidth - width - 8));
          menu.style.top = `${{top}}px`;
          menu.style.left = `${{left}}px`;
        }};
        const openMenu = () => {{
          if (window.__aetextStageMenuClose) window.__aetextStageMenuClose();
          menuOpen = true;
          menu.hidden = false;
          document.body.append(menu);
          applyState();
          positionMenu();
          trigger.setAttribute('aria-expanded', 'true');
          window.__aetextStageMenuClose = closeMenu;
          document.addEventListener('pointerdown', closeOnOutside, true);
          document.addEventListener('keydown', closeOnKeydown);
          window.addEventListener('resize', closeOnViewport);
          window.addEventListener('scroll', closeOnViewport, true);
        }};
        select.addEventListener('change', () => {{
          const value = select.value || null;
          params.data.workflow_stage = value;
          params.data.workflow_stage_explicit = true;
          window.aetextMarkEdit(params.data, true);
          params.api.dispatchEvent({{
            type: 'draftChanged',
            data: params.data,
            node: params.node,
            column: params.column,
          }});
          applyState();
        }});
        trigger.addEventListener('click', event => {{
          event.stopPropagation();
          if (menuOpen) closeMenu(); else openMenu();
        }});
        trigger.addEventListener('keydown', event => {{
          if (!['Enter', ' ', 'ArrowDown', 'ArrowUp'].includes(event.key)) return;
          event.preventDefault();
          if (!menuOpen) openMenu();
          const enabled = [...menu.querySelectorAll('.aetext-stage-menu-option:not(:disabled)')];
          const selected = enabled.find(item => item.dataset.value === select.value);
          (selected ?? enabled[0])?.focus();
        }});
        menu.addEventListener('click', event => {{
          const menuOption = event.target.closest('.aetext-stage-menu-option');
          if (!menuOption || menuOption.disabled) return;
          select.value = menuOption.dataset.value;
          select.dispatchEvent(new Event('change', {{ bubbles: true }}));
          closeMenu(true);
        }});
        menu.addEventListener('keydown', event => {{
          const enabled = [...menu.querySelectorAll('.aetext-stage-menu-option:not(:disabled)')];
          if (event.key === 'Escape') {{
            event.preventDefault();
            closeMenu(true);
            return;
          }}
          if (!['ArrowDown', 'ArrowUp', 'Home', 'End'].includes(event.key)) return;
          event.preventDefault();
          const currentIndex = enabled.indexOf(document.activeElement);
          let nextIndex = currentIndex;
          if (event.key === 'Home') nextIndex = 0;
          if (event.key === 'End') nextIndex = enabled.length - 1;
          if (event.key === 'ArrowDown') nextIndex = (currentIndex + 1) % enabled.length;
          if (event.key === 'ArrowUp') {{
            nextIndex = (currentIndex - 1 + enabled.length) % enabled.length;
          }}
          enabled[nextIndex]?.focus();
        }});
        applyState();
        trigger.append(indicator, label, chevron);
        control.append(select, trigger);
        wrapper.append(control);
        if (params.data.review_change_message) {{
          const reason = document.createElement('div');
          reason.className = 'aetext-row-validation';
          reason.textContent = params.data.review_change_message;
          wrapper.append(reason);
        }}
        return wrapper;
    }}"""


def grid_options_for_section(
    session: ReviewSession,
    role: str,
    text: UiText,
) -> dict[str, object]:
    columns: list[dict[str, object]] = [
        {
            "field": "panel_order_display",
            "headerName": text.text("grid.header.order"),
            "editable": False,
            "width": 100,
            "pinned": "left",
            "lockPinned": True,
            "headerClass": "aetext-center-header",
            "cellClass": "aetext-center-cell",
        },
        {
            "field": "original",
            "headerName": text.text("grid.header.original"),
            "editable": False,
            "filter": True,
            "width": 280,
            "cellClass": "aetext-text-cell",
            ":cellRenderer": _original_renderer(text),
        },
    ]
    if session.workflow.enabled:
        columns.append(
            {
                "field": "workflow_stage",
                "headerName": text.text("grid.header.workflow"),
                "editable": False,
                "filter": True,
                "filterParams": {"filterOptions": ["equals"], "maxNumConditions": 10},
                ":cellRenderer": _workflow_renderer(session, text),
                "width": 168,
                "headerClass": "aetext-center-header aetext-filtered-center-header",
                "cellClass": "aetext-center-cell",
            }
        )
    columns.extend(
        [
            {
                "field": "translation",
                "headerName": text.text("grid.header.translation"),
                "editable": False,
                "filter": True,
                "flex": 2,
                "minWidth": 320,
                "wrapText": True,
                "autoHeight": True,
                "cellClass": "aetext-text-cell",
                ":cellRenderer": _translation_renderer(session, text),
            },
            {
                "field": "use_source",
                "headerName": text.text("grid.header.use_source"),
                "editable": True,
                "cellEditor": "agCheckboxCellEditor",
                "cellRenderer": "agCheckboxCellRenderer",
                "width": 115,
                "headerClass": "aetext-center-header",
                "cellClass": "aetext-center-cell",
            },
            {
                "field": "stable_id",
                "headerName": "Stable ID",
                "editable": False,
                "filter": True,
                "flex": 1,
                "minWidth": 220,
                "cellClass": "aetext-text-cell",
            },
        ]
    )
    columns.extend(
        [
            {
                "field": "content_status_label",
                "editable": False,
                "filter": True,
                "filterParams": {"filterOptions": ["equals"], "maxNumConditions": 10},
                "hide": True,
            },
            {"field": "content_status", "hide": True},
            {"field": "validation_message", "hide": True},
        ]
    )
    return {
        "columnDefs": columns,
        "rowData": [row_data(row, text) for row in rows_for_section(session, role)],
        ":getLocaleText": (
            "params => window.aetextAgGridLocale?.[params.key] ?? params.defaultValue"
        ),
        ":onCellValueChanged": (
            "event => { if (event.colDef?.field === 'workflow_stage' || "
            "event.colDef?.field === 'validation_message') return; "
            "window.aetextMarkEdit(event.data, false, "
            + (
                json.dumps(session.workflow.defaults.manual_edit)
                if session.workflow.enabled
                else "undefined"
            )
            + "); event.api.refreshCells({rowNodes: [event.node], "
            + "columns: ['workflow_stage'], force: true}); }"
        ),
        "defaultColDef": {"sortable": True, "resizable": True},
        "maintainColumnOrder": True,
        "stopEditingWhenCellsLoseFocus": True,
        "rowSelection": {"mode": "multiRow"},
        "selectionColumnDef": {
            "width": 54,
            "pinned": "left",
            "lockPinned": True,
            "resizable": False,
            "sortable": False,
            "suppressMovable": True,
            "headerClass": "aetext-center-header",
            "cellClass": "aetext-center-cell",
        },
        ":getRowId": "params => params.data.stable_id",
        "animateRows": False,
        "suppressClickEdit": True,
        "rowHeight": 58,
    }


def section_summary(session: ReviewSession, role: str) -> str:
    rows = rows_for_section(session, role)
    completed = sum(row.content_status in {"valid", "use-source"} for row in rows)
    return f"{completed} / {len(rows)}"


def summary(session: ReviewSession, text: UiText) -> str:
    counts = content_status_counts(session)
    return text.text(
        "summary",
        valid=counts["valid"],
        use_source=counts["use-source"],
        missing=counts["missing"],
        errors=counts["error"],
    )


def content_filter_values(statuses: set[str], text: UiText) -> list[str]:
    return [text.text(f"status.{status}") for status in CONTENT_STATUSES if status in statuses]


def community_text_filter(values: list[str]) -> dict[str, object] | None:
    conditions = [{"filterType": "text", "type": "equals", "filter": value} for value in values]
    if not conditions:
        return None
    if len(conditions) == 1:
        return conditions[0]
    return {"filterType": "text", "operator": "OR", "conditions": conditions}


def community_stage_filter(values: set[str]) -> dict[str, object] | None:
    conditions = [
        {"filterType": "text", "type": "blank"}
        if value == ""
        else {"filterType": "text", "type": "equals", "filter": value}
        for value in sorted(values)
    ]
    if not conditions:
        return None
    if len(conditions) == 1:
        return conditions[0]
    return {"filterType": "text", "operator": "OR", "conditions": conditions}
