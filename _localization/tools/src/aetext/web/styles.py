"""Workspace appearance and browser edit bookkeeping."""

from __future__ import annotations

import json

from .i18n import UiText, ag_grid_locale_text

_WORKSPACE_HEAD = r"""
<script>
document.documentElement.lang = '__AETEXT_UI_LOCALE__';
window.aetextDirty = false;
window.aetextDrafts = {};
window.aetextEditVersion = 0;
window.aetextCapturedVersion = 0;
window.aetextMarkEdit = (row, stage = false, manualStage = undefined) => {
  row.edit_revision = ++window.aetextEditVersion;
  if (stage) row.workflow_stage_revision = row.edit_revision;
  else if (manualStage !== undefined) {
    row.workflow_stage = manualStage;
    row.workflow_stage_explicit = false;
  }
  window.aetextDirty = true;
};
window.aetextAgGridLocale = __AETEXT_AG_GRID_LOCALE__;
window.addEventListener('beforeunload', event => {
  if (window.aetextDirty) {
    event.preventDefault();
    event.returnValue = '';
  }
});
</script>
<style>
html, body, #q-app { margin: 0 !important; padding: 0 !important; border-radius: 0 !important; }
.q-layout, .q-layout-container, .aetext-header { border-radius: 0 !important; }
.aetext-save-all { margin-left: auto; min-width: 142px; }
.aetext-save-all .q-btn__content { width: 100%; justify-content: center; text-align: center; }
.aetext-filter-row { row-gap: 10px; column-gap: 12px; }
.aetext-filter-label { min-height: 30px; display: inline-flex; align-items: center; }
.aetext-filter-chip { min-width: 76px; min-height: 30px; margin: 0; padding: 0 10px; }
.aetext-filter-chip .q-chip__content { width: 100%; justify-content: center; text-align: center;
  white-space: nowrap; }
.aetext-translation-wrap { width: 100%; padding: 5px 0; }
.aetext-translation-main { display: flex; align-items: center; gap: 8px; width: 100%;
  min-width: 0; }
.aetext-translation-input { flex: 1; width: auto; min-width: 0; min-height: 34px;
  box-sizing: border-box; border: 1px solid #b8c0cc;
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
.aetext-content-validity { flex: 0 0 20px; width: 20px; height: 20px; margin-left: auto;
  display: inline-flex; align-items: center; justify-content: center; border-radius: 50%;
  box-sizing: border-box; cursor: help; font-size: 13px; font-weight: 700; line-height: 1; }
.aetext-content-validity.is-valid { color: #fff; background: #16843c; }
.aetext-content-validity.is-invalid { color: #fff; background: #c62828; }
.aetext-stage-wrap { display: flex; flex-direction: column; justify-content: center; gap: 3px;
  width: 100%; min-width: 0; height: 100%; }
.aetext-stage-control { position: relative; width: 100%; min-width: 0; height: 34px;
  flex: 0 0 34px; }
.aetext-stage-select { position: absolute; inset: 0; width: 100%; min-width: 0;
  max-width: 100%; box-sizing: border-box; border: 1px solid #b8c0cc;
  border-radius: 6px; padding: 0; background: #fff; color: transparent;
  font: inherit; opacity: 0; pointer-events: none; }
.aetext-stage-select option { background: #fff; color: #1f2937; text-align: center; }
.aetext-stage-trigger { position: absolute; inset: 0; width: 100%; min-width: 0;
  box-sizing: border-box; border: 1px solid #b8c0cc; border-radius: 6px; padding: 0;
  cursor: pointer; background: #fff; color: #1f2937; font: inherit; }
.aetext-stage-trigger:focus-visible { outline: 2px solid var(--q-primary);
  outline-offset: 1px; }
.aetext-stage-indicator { position: absolute; z-index: 1; left: 13px; top: 50%; width: 10px;
  height: 10px; border-radius: 50%; transform: translateY(-50%); pointer-events: none;
  box-shadow: 0 0 0 2px rgba(127,127,127,.13); }
.aetext-stage-label { position: absolute; z-index: 1; inset: 0 36px; display: flex;
  align-items: center; justify-content: center; min-width: 0; overflow: hidden;
  color: #1f2937; text-align: center; white-space: nowrap; text-overflow: ellipsis;
  pointer-events: none; }
.aetext-stage-chevron { position: absolute; z-index: 1; right: 16px; top: 50%; width: 7px;
  height: 7px; border-right: 2px solid #253247; border-bottom: 2px solid #253247;
  transform: translateY(-68%) rotate(45deg); pointer-events: none; }
.aetext-stage-menu { position: fixed; z-index: 10000; overflow: hidden;
  box-sizing: border-box; border: 1px solid #b8c0cc; border-radius: 0 0 6px 6px;
  background: #fff; box-shadow: 0 4px 12px rgba(31,41,55,.18); }
.aetext-stage-menu-option { position: relative; display: block; width: 100%; height: 40px;
  box-sizing: border-box; border: 0; padding: 0; cursor: pointer; background: #fff;
  color: #1f2937; font: inherit; }
.aetext-stage-menu-option:hover, .aetext-stage-menu-option:focus-visible {
  background: #edf4ff; outline: 0; }
.aetext-stage-menu-option.is-selected { background: #858585; color: #fff; }
.aetext-stage-menu-option:disabled { cursor: not-allowed; opacity: .52; }
.aetext-stage-menu-indicator { position: absolute; left: 16px; top: 50%; width: 12px;
  height: 12px; border-radius: 50%; transform: translateY(-50%); pointer-events: none;
  box-shadow: 0 0 0 2px rgba(127,127,127,.13); }
.aetext-stage-menu-label { position: absolute; inset: 0 34px; display: flex;
  align-items: center; justify-content: center; min-width: 0; overflow: hidden;
  text-align: center; white-space: nowrap; text-overflow: ellipsis; pointer-events: none; }
.aetext-original-wrap { display: flex; align-items: center; gap: 6px; width: 100%; height: 100%;
  min-width: 0; overflow: hidden; box-sizing: border-box; padding: 5px 0; }
.aetext-original-text { flex: 1; min-width: 0; white-space: nowrap; overflow: hidden;
  text-overflow: ellipsis; }
.aetext-copy-button { opacity: 0; border: 0; border-radius: 4px; padding: 2px 6px; cursor: pointer;
  flex: 0 0 auto; color: var(--q-primary); background: rgba(127,127,127,.10);
  transition: opacity .12s; }
.aetext-original-wrap:hover .aetext-copy-button, .aetext-copy-button:focus { opacity: 1; }
.aetext-row-validation { color: #c62828; font-size: 12px; white-space: pre-wrap; margin-top: 3px; }
.aetext-review-grid .ag-header-cell.aetext-center-header .ag-header-cell-label {
  position: relative; width: 100%; justify-content: flex-end; }
.aetext-review-grid .ag-header-cell.aetext-center-header .ag-header-cell-text {
  position: absolute; left: 50%; top: 50%; max-width: calc(100% - 52px); overflow: hidden;
  transform: translate(-50%, -50%); text-align: center; text-overflow: ellipsis;
  white-space: nowrap; }
.aetext-review-grid .ag-header-cell.aetext-filtered-center-header .ag-header-cell-text {
  left: calc(50% + 8px); }
.aetext-review-grid .ag-cell { display: flex; align-items: center; }
.aetext-review-grid .ag-cell > .ag-cell-wrapper { width: 100%; }
.aetext-review-grid .ag-cell.aetext-center-cell,
.aetext-review-grid .ag-cell.aetext-center-cell .ag-cell-wrapper {
  align-items: center; justify-content: center; text-align: center; }
.aetext-review-grid .ag-cell.aetext-text-cell { justify-content: flex-start; text-align: left; }
.aetext-review-grid .ag-cell[col-id="ag-Grid-SelectionColumn"] .ag-cell-wrapper,
.aetext-review-grid .ag-cell[col-id="ag-Grid-SelectionColumn"] .ag-selection-checkbox {
  width: 100%; justify-content: center; margin: 0; }
.aetext-review-grid .ag-header-cell[col-id="ag-Grid-SelectionColumn"] .ag-header-select-all {
  margin: 0 auto; transform: translateX(3px); }
</style>
"""


def workspace_head(text: UiText) -> str:
    return _WORKSPACE_HEAD.replace("__AETEXT_UI_LOCALE__", text.locale).replace(
        "__AETEXT_AG_GRID_LOCALE__", json.dumps(ag_grid_locale_text(text), ensure_ascii=False)
    )
