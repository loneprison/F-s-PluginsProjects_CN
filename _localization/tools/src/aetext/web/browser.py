"""Read and acknowledge grid edits in one browser operation per snapshot."""

from __future__ import annotations

import json

from nicegui import ui

BROWSER_RESPONSE_TIMEOUT = 10.0


async def read_grid_rows(grid_ids: list[int], *, capture: bool = False) -> list[dict[str, object]]:
    return await ui.run_javascript(
        """
        const rows = [];
        const drafts = window.aetextDrafts || {};
        for (const id of __GRID_IDS__) {
          const api = getElement(id).api;
          api.stopEditing();
          api.forEachNode(node => {
            const row = {...node.data};
            if (Object.hasOwn(drafts, row.stable_id)) row.translation = drafts[row.stable_id];
            rows.push(row);
          });
        }
        if (__CAPTURE__) {
          window.aetextDrafts = {};
          window.aetextCapturedVersion = window.aetextEditVersion;
        }
        return rows;
        """.replace("__GRID_IDS__", json.dumps(grid_ids)).replace(
            "__CAPTURE__", json.dumps(capture)
        ),
        timeout=BROWSER_RESPONSE_TIMEOUT,
    )


async def acknowledge_grid_save(
    grid_ids: list[int],
    submitted: list[dict[str, object]],
    saved: list[dict[str, object]],
    *,
    other_dirty: bool,
) -> dict[str, object]:
    payload = {
        "grids": grid_ids,
        "submitted": {str(row["stable_id"]): row for row in submitted},
        "saved": {str(row["stable_id"]): row for row in saved},
        "otherDirty": other_dirty,
    }
    return await ui.run_javascript(
        """
        const state = __STATE__;
        const drafts = window.aetextDrafts || {};
        const rows = [];
        let dirty = false;
        for (const id of state.grids) {
          const api = getElement(id).api;
          const unchanged = [];
          const changed = [];
          api.stopEditing();
          api.forEachNode(node => {
            const current = {...node.data};
            const key = current.stable_id;
            if (Object.hasOwn(drafts, key)) current.translation = drafts[key];
            const sent = state.submitted[key];
            const baseline = state.saved[key];
            const merged = {...baseline};
            let newer = false;
            for (const field of ['translation', 'use_source', 'workflow_stage']) {
              if (current[field] !== sent[field]) {
                merged[field] = current[field];
                newer = true;
              }
            }
            if ((current.workflow_stage_revision || 0) !== (sent.workflow_stage_revision || 0)) {
              merged.workflow_stage = current.workflow_stage;
              merged.workflow_stage_explicit = current.workflow_stage_explicit;
              newer = true;
            }
            merged.edit_revision = current.edit_revision;
            merged.workflow_stage_revision = current.workflow_stage_revision;
            rows.push(merged);
            if (newer) {
              // Keep the live text input and its selection while updating the saved baseline.
              Object.assign(node.data, merged);
              changed.push(node);
              dirty = true;
            } else {
              unchanged.push(merged);
            }
          });
          if (unchanged.length) api.applyTransaction({update: unchanged});
          if (changed.length) api.refreshCells({
            rowNodes: changed, columns: ['workflow_stage'], force: true});
        }
        window.aetextDrafts = {};
        window.aetextCapturedVersion = window.aetextEditVersion;
        window.aetextDirty = dirty || state.otherDirty;
        return {rows, revision: window.aetextEditVersion};
        """.replace("__STATE__", json.dumps(payload)),
        timeout=BROWSER_RESPONSE_TIMEOUT,
    )
