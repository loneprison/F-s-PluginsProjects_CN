# AeText development tools

This directory contains the development-only scanner, catalog validation, migration, and local
review application. It is not copied into effect, Settings, or installer outputs.

From this directory, create the locked environment and run the contract tests with:

```powershell
uv sync --locked --dev
uv run --locked playwright install chromium
uv run --locked pytest
uv run --locked ruff check src tests ../tests
uv run --locked ruff format --check src tests ../tests
```

The only interactive translation-review entry is the local browser application:

```powershell
uv run --locked aetext review
```

This opens the single project-tree workspace. Select an unscanned source-derived plugin and use
**扫描当前插件源码** before editing. Start with one plugin selected by name with:

```powershell
uv run --locked aetext review PluginSkeleton
```

Opening the workspace, choosing a plugin, switching language, saving, and reloading catalogs never
run MSBuild or the C++ scanner. Only the explicit scan menu updates the ignored
`_localization/.cache/aetext-review` source index; normal builds and CI do not read this cache.

The review server must remain loopback-only. Human catalogs stay language-first, Original text is
derived from source, and ordinary generation never starts the review application or writes a
catalog.

Repository classification is also source-derived. Effect categories come from the actual PiPL
`CustomBuild` input and the macro referenced by its `Category` expression; both `FS_CATEGORY` and
`NFS_CATEGORY` are ordinary historical identifiers. `_Support` catalogs are the one explicit AEGP
exception and do not require or emit an Effect category. Preview drift from these authorities,
generated PluginMap, solution folders, and output layout with:

```powershell
uv run --locked aetext sync-classification
```

The preview exits nonzero when derived files are stale. Apply the deterministic repair explicitly,
then rerun it to prove zero diff:

```powershell
uv run --locked aetext sync-classification --apply
uv run --locked aetext sync-classification
```

The transitional legacy generator path must remain until its structural gate reports that no effect
catalog still contains `bindings`. `NFsSkelton` is a maintained historical template ancestor and
participates in normal content progress; after its source-derived migration, any remaining legacy
catalog still blocks infrastructure retirement:

```powershell
uv run --locked aetext check-legacy-retirement
```
