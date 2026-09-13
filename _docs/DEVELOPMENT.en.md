**English** | [简体中文](DEVELOPMENT.zh-CN.md) | [日本語](DEVELOPMENT.ja.md)

# Source build and development

[User guide](../README.md) · [Translation review](../_localization/README.md) · [Original README](README.original.md)

## Get the source

1. Download After Effects SDK 25.2 from the
   [Adobe After Effects developer page](https://developer.adobe.com/after-effects/) and extract it.
2. Open `AfterEffectsSDK\Examples` from the SDK and start PowerShell there.
3. Clone the repository and enter its directory:

```powershell
git clone https://github.com/loneprison/F-s-PluginsProjects_Multilingual.git
cd .\F-s-PluginsProjects_Multilingual
```

## Development environment

- Visual Studio 2026 with **Desktop development with C++**
- Python 3.12
- `uv`

If `uv` is not installed, run:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Open a new PowerShell window and verify it:

```powershell
uv --version
```

## Local paths

Visual Studio uses these variables:

- `AE_PLUGIN_BUILD_DIR`: plug-in build output directory
- `AE_DEBUG_HOST_EXE`: path to `AfterFX.exe` for Debug/F5

There are two ways to configure them.

Add them to your Windows user environment variables, either through the Environment Variables dialog
in System Properties or by running this in PowerShell:

```powershell
New-Item -ItemType Directory -Force 'D:\AePluginBuild'
[Environment]::SetEnvironmentVariable('AE_PLUGIN_BUILD_DIR', 'D:\AePluginBuild', 'User')
[Environment]::SetEnvironmentVariable(
    'AE_DEBUG_HOST_EXE',
    'C:\Program Files\Adobe\Adobe After Effects 2024\Support Files\AfterFX.exe',
    'User'
)
```

Reopen Visual Studio and terminals after setting them.

Alternatively, fill in the first `PropertyGroup` of `Directory.Build.props` in the project directory:

```xml
<AE_PLUGIN_BUILD_DIR Condition="'$(AE_PLUGIN_BUILD_DIR)'==''">D:\AePluginBuild</AE_PLUGIN_BUILD_DIR>
<AE_DEBUG_HOST_EXE Condition="'$(AE_DEBUG_HOST_EXE)'==''">C:\Program Files\Adobe\Adobe After Effects 2024\Support Files\AfterFX.exe</AE_DEBUG_HOST_EXE>
```

If you do not plan to open Visual Studio and only use the `BuildPlugins.bat` modes below, you do not
need to configure these variables.

## Build

Show the available modes:

```powershell
.\BuildPlugins.bat --help
```

Create the formal multilingual Release build:

```powershell
.\BuildPlugins.bat publication
```

This rebuilds the release projects for Release x64 with all four text variants, Language Settings, the
original-Japanese fallback, and publication validation. Solution folders whose names are enclosed in
parentheses are not built. Output:

```text
_build\publication\Fs_Plugins
```

## Use without multilingual settings

If you do not need multilingual settings, build a fixed-language version without Language Settings:

```powershell
.\BuildPlugins.bat custom --default-language <language> --single-language
```

Replace `<language>` with:

- `en`: English
- `ja`: original Japanese
- `zh`: Simplified Chinese
- `ja-for-zh`: original Japanese for a Simplified Chinese encoding environment

`--single-language` builds only the selected text variant, does not build
`F's Language Settings.aex`, and prevents the effects from acquiring the Runtime. They therefore do
not use multilingual settings even when Language Settings is installed in After Effects.

Without Language Settings/Runtime, builds with and without this option display the same `<language>`.
When the Runtime is available, a build without the option follows the multilingual setting, while a
build with the option always uses `<language>`. Output is under
`_build\custom\single-<language>\Fs_Plugins`.

Formal releases do not include fixed-language builds. Build one from source if needed.

## Localization code style

The second segment of a text macro is its type, and the final segment is its name. Use the matching
wrapper where the text is displayed.

| Form | Classification | Use |
| --- | --- | --- |
| `#define L10N_PARAM_<NAME> "Source text"` | — | Define source text |
| `AETEXT_PARAM(strings, L10N_PARAM_<NAME>)` | `Param` | Parameter names |
| `AETEXT_LABEL(strings, L10N_PARAM_<NAME>)` | `Label` | Control labels |
| `AETEXT_POPUP(strings, L10N_PARAM_<NAME>_ITEMS)` | `Popup` | Dropdown items |
| `AETEXT_TOPIC(strings, L10N_PARAM_<NAME>_TOPIC)` | `Topic` | Topic groups |
| `AETEXT_ABOUT(strings, L10N_PLUGIN_<NAME>)` | `About` | Plug-in descriptions |
| `AETEXT_ERROR(strings, L10N_ERR_<NAME>)` | `Error` | Error messages |
| `AETEXT_VERBATIM_PARAM(strings, L10N_PARAM_<NAME>)` | `Param` | Skip translation, equivalent to using an ordinary source-text macro directly |

After adding, deleting, or changing an `L10N_*` source string, or changing an `AETEXT_*` wrapper, scan
that plugin again in the review tool.

## Contributing translations

To change or contribute translations, see the [translation review guide](../_localization/README.md).

## Contributing

To contribute code, submit a pull request.
