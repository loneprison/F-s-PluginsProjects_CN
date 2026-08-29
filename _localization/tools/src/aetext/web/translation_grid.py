# ruff: noqa: RUF001
"""Per-Role AG Grid configuration for one cached review session."""

from __future__ import annotations

import json

from ..catalog.review import ReviewRow, ReviewSession
from ..core.scanner_contract import ROLE_ORDER as ROLE_INDEX

CONTENT_STATUS_LABELS = {
    "missing": "待翻译",
    "use-source": "使用原文",
    "valid": "有效",
    "error": "错误",
    "unscanned": "未扫描",
}
ROLE_ORDER = tuple(sorted(ROLE_INDEX, key=ROLE_INDEX.__getitem__))
ROLE_LABELS = {
    "Param": "参数名称",
    "Label": "控件文字",
    "Popup": "下拉选项",
    "Topic": "主题分组",
    "About": "About",
    "Error": "错误消息",
}


def row_data(row: ReviewRow) -> dict[str, object]:
    result = row.model_dump()
    result["content_status_label"] = CONTENT_STATUS_LABELS[row.content_status]
    result["panel_order_display"] = row.panel_order + 1
    result["roles_label"] = " · ".join(ROLE_LABELS[role] for role in row.roles)
    result["popup_item_count"] = len(row.original.split("|")) if row.primary_role == "Popup" else 0
    result["validation_message"] = "\n".join(row.validation_messages)
    return result


def all_row_data(session: ReviewSession) -> list[dict[str, object]]:
    return [row_data(row) for row in session.rows]


def rows_for_section(session: ReviewSession, role: str) -> list[ReviewRow]:
    return [row for row in session.rows if row.primary_role == role]


def content_status_counts(session: ReviewSession) -> dict[str, int]:
    counts = {name: 0 for name in CONTENT_STATUS_LABELS}
    for row in session.rows:
        counts[row.content_status] += 1
    return counts


def workflow_stage_counts(session: ReviewSession) -> dict[str, int]:
    counts = {"": 0, **{stage.id: 0 for stage in session.workflow.stages}}
    for row in session.rows:
        counts[row.workflow_stage or ""] = counts.get(row.workflow_stage or "", 0) + 1
    return counts


def _translation_renderer() -> str:
    return r"""params => {
        const wrapper = document.createElement('div');
        wrapper.className = 'aetext-translation-wrap';
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
          button.textContent = `编辑下拉项…（${params.data.popup_item_count} 项）`;
          button.disabled = Boolean(params.data.use_source);
          button.title = button.disabled ? '已启用使用原文' : '打开结构化下拉菜单编辑器';
          button.addEventListener('click', event => {
            event.stopPropagation();
            params.api.dispatchEvent({
              type: 'popupEditRequested',
              data: params.data,
              node: params.node,
              column: params.column,
            });
          });
          wrapper.append(button);
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
          editor.placeholder = editor.disabled ? '使用原文' : '请输入译文';
          editor.setAttribute('aria-label', `${params.data.stable_id} 译文`);
          const resize = () => {
            if (!multiline) return;
            editor.style.height = 'auto';
            editor.style.height = `${Math.max(52, editor.scrollHeight)}px`;
          };
          editor.addEventListener('input', () => {
            clearValidation();
            window.aetextDirty = true;
            params.data.translation = editor.value;
            drafts[params.data.stable_id] = editor.value;
            const expansion = editor.closest('.q-expansion-item');
            const title = expansion?.querySelector('.q-item__label');
            if (title && !title.textContent.includes('● 未保存')) {
              title.textContent += '  ● 未保存';
            }
            resize();
          });
          editor.addEventListener('click', event => event.stopPropagation());
          wrapper.append(editor);
          queueMicrotask(resize);
        }
        if (validation.textContent) wrapper.append(validation);
        return wrapper;
    }"""


def _original_renderer() -> str:
    return r"""params => {
        const wrapper = document.createElement('div');
        wrapper.className = 'aetext-original-wrap';
        wrapper.title = '双击复制原文';
        const text = document.createElement('span');
        text.className = 'aetext-original-text';
        text.textContent = params.value ?? '';
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'aetext-copy-button';
        button.textContent = '复制';
        button.title = '复制原文';
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
          Quasar.Notify.create({message: '已复制原文', timeout: 900, position: 'top'});
        };
        wrapper.addEventListener('dblclick', copy);
        button.addEventListener('click', copy);
        wrapper.append(text, button);
        return wrapper;
    }"""


def _workflow_renderer(session: ReviewSession) -> str:
    stage_options = [
        {"id": "", "label": "无", "color": "grey", "enabled": True},
        *[
            {
                "id": stage.id,
                "label": stage.label if stage.enabled else f"已停用：{stage.label}",
                "color": stage.color,
                "enabled": stage.enabled,
            }
            for stage in session.workflow.stages
        ],
    ]
    return f"""params => {{
        const stages = {json.dumps(stage_options, ensure_ascii=False)};
        const select = document.createElement('select');
        select.className = 'aetext-stage-select';
        const current = params.value ?? '';
        for (const stage of stages) {{
          const option = document.createElement('option');
          option.value = stage.id;
          option.textContent = stage.label;
          option.disabled = !stage.enabled && stage.id !== current;
          select.append(option);
        }}
        select.value = current;
        const applyStyle = () => {{
          const stage = stages.find(item => item.id === select.value) ?? stages[0];
          const color = getComputedStyle(document.documentElement)
            .getPropertyValue(`--q-${{stage.color}}`).trim() || stage.color;
          select.style.backgroundColor = color;
          select.style.color = stage.id ? 'white' : 'inherit';
          select.style.opacity = stage.enabled ? '1' : '0.65';
        }};
        select.addEventListener('change', () => {{
          params.node.setDataValue('workflow_stage', select.value || null);
          applyStyle();
        }});
        select.addEventListener('click', event => event.stopPropagation());
        applyStyle();
        return select;
    }}"""


def grid_options_for_section(session: ReviewSession, role: str) -> dict[str, object]:
    columns: list[dict[str, object]] = [
        {
            "field": "panel_order_display",
            "headerName": "AE 序号",
            "editable": False,
            "width": 100,
            "pinned": "left",
            "lockPinned": True,
        },
        {
            "field": "content_status_label",
            "headerName": "内容状态",
            "editable": False,
            "filter": True,
            "filterParams": {"filterOptions": ["equals"], "maxNumConditions": 10},
            "width": 115,
        },
    ]
    if session.workflow.enabled:
        columns.append(
            {
                "field": "workflow_stage",
                "headerName": "审校阶段",
                "editable": False,
                "filter": True,
                "filterParams": {"filterOptions": ["equals"], "maxNumConditions": 10},
                ":cellRenderer": _workflow_renderer(session),
                "width": 145,
            }
        )
    columns.extend(
        [
            {
                "field": "original",
                "headerName": "原文",
                "editable": False,
                "filter": True,
                "pinned": "left",
                "lockPinned": True,
                "width": 280,
                "wrapText": True,
                "autoHeight": True,
                ":cellRenderer": _original_renderer(),
            },
            {
                "field": "translation",
                "headerName": "译文",
                "editable": False,
                "filter": True,
                "flex": 2,
                "wrapText": True,
                "autoHeight": True,
                ":cellRenderer": _translation_renderer(),
            },
            {
                "field": "use_source",
                "headerName": "使用原文",
                "editable": True,
                "cellEditor": "agCheckboxCellEditor",
                "cellRenderer": "agCheckboxCellRenderer",
                "width": 115,
            },
            {
                "field": "roles_label",
                "headerName": "用途",
                "editable": False,
                "filter": True,
                ":cellRenderer": (
                    "params => (params.value || '').split(' · ').map(value => "
                    '`<span style="display:inline-block;padding:1px 7px;margin-right:4px;'
                    "border-radius:10px;background:#e8eef9\">${value}</span>`).join('')"
                ),
                "width": 180,
            },
            {
                "field": "stable_id",
                "headerName": "Stable ID",
                "editable": False,
                "filter": True,
                "flex": 1,
            },
        ]
    )
    columns.extend(
        [
            {"field": "content_status", "hide": True},
            {"field": "validation_message", "hide": True},
        ]
    )
    return {
        "columnDefs": columns,
        "rowData": [row_data(row) for row in rows_for_section(session, role)],
        "defaultColDef": {"sortable": True, "resizable": True},
        "stopEditingWhenCellsLoseFocus": True,
        "rowSelection": {"mode": "multiRow"},
        ":getRowId": "params => params.data.stable_id",
        "animateRows": False,
        "suppressClickEdit": True,
        "rowHeight": 58,
    }


def section_summary(session: ReviewSession, role: str) -> str:
    rows = rows_for_section(session, role)
    completed = sum(row.content_status in {"valid", "use-source"} for row in rows)
    return f"{completed} / {len(rows)}"


def summary(session: ReviewSession) -> str:
    counts = content_status_counts(session)
    return (
        f"有效 {counts['valid']} · 使用原文 {counts['use-source']} · "
        f"待翻译 {counts['missing']} · 错误 {counts['error']}"
    )


def content_filter_values(statuses: set[str]) -> list[str]:
    return [CONTENT_STATUS_LABELS[status] for status in CONTENT_STATUS_LABELS if status in statuses]


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
