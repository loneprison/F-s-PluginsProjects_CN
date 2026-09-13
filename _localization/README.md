**English** | [简体中文](README.zh-CN.md) | [日本語](README.ja.md)

# Translation review Web tool

Use the local Web workspace for translation and review. Do not edit translation or review JSON by hand.

## Start

Install `uv`, then start from `_localization\tools`:

```powershell
cd .\_localization\tools
uv sync --locked --dev
uv run --locked aetext review
```

You can also start it from the repository root:

```powershell
uv run --project .\_localization\tools --locked aetext review
```

The first run prepares the Python environment. Keep the terminal open. If the browser does not open,
use the local URL printed after `AeText review:`.

**Interface language** changes the Web UI. **Translation language** selects the text being edited.

## Scan

- On a new checkout, choose **Scan > Scan all plugin sources**.
- For one effect, select it and choose **Scan > Scan current plugin source**.
- Scan again when the page reports stale data.

## Edit and review

1. Select a plugin and translation language.
2. Enter the translation in **Translation**; enable **Use source** to keep the source text.
3. Change dropdown text through **Edit popup items…**.
4. After checking the translation, set **Status** to **Reviewed**.

## Save

`*` marks unsaved changes. Use **Save this plugin** or **Save all changes** to save them.

## Check publication review

After saving, select an effect or Language Settings and choose **Scan > Check current plugin publication review**.

## Stop or reopen

Press `Ctrl+C` in the terminal to stop the service. Run it again with the start command.
