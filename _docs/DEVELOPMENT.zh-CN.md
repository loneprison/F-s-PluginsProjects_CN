[English](DEVELOPMENT.en.md) | **简体中文** | [日本語](DEVELOPMENT.ja.md)

# 源码构建与开发

[使用说明](README.zh-CN.md) · [翻译审校](../_localization/README.zh-CN.md) · [原作者 README](README.original.md)

## 获取源码

1. 从 [Adobe After Effects 开发者页面](https://developer.adobe.com/after-effects/)下载
   After Effects SDK 25.2 并解压。
2. 打开 SDK 内的 `AfterEffectsSDK\Examples` 目录，在该目录启动 PowerShell。
3. 克隆仓库并进入项目目录：

```powershell
git clone https://github.com/loneprison/F-s-PluginsProjects_Multilingual.git
cd .\F-s-PluginsProjects_Multilingual
```

## 开发环境

- Visual Studio 2026，安装“使用 C++ 的桌面开发”
- Python 3.12
- `uv`

如果尚未安装 `uv`，在 PowerShell 中运行：

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

重新打开 PowerShell，然后确认安装：

```powershell
uv --version
```

## 本机路径

Visual Studio 使用以下两个变量：

- `AE_PLUGIN_BUILD_DIR`：插件构建输出目录
- `AE_DEBUG_HOST_EXE`：Debug／F5 使用的 `AfterFX.exe` 路径

有两种配置方式。

可以将变量加入 Windows 用户环境变量：在“系统属性”的“环境变量”中手动编辑，或打开 PowerShell
运行：

```powershell
New-Item -ItemType Directory -Force 'D:\AePluginBuild'
[Environment]::SetEnvironmentVariable('AE_PLUGIN_BUILD_DIR', 'D:\AePluginBuild', 'User')
[Environment]::SetEnvironmentVariable(
    'AE_DEBUG_HOST_EXE',
    'C:\Program Files\Adobe\Adobe After Effects 2024\Support Files\AfterFX.exe',
    'User'
)
```

设置后重新打开 Visual Studio 和终端。

也可以在项目目录下的 `Directory.Build.props` 第一个 `PropertyGroup` 中填写：

```xml
<AE_PLUGIN_BUILD_DIR Condition="'$(AE_PLUGIN_BUILD_DIR)'==''">D:\AePluginBuild</AE_PLUGIN_BUILD_DIR>
<AE_DEBUG_HOST_EXE Condition="'$(AE_DEBUG_HOST_EXE)'==''">C:\Program Files\Adobe\Adobe After Effects 2024\Support Files\AfterFX.exe</AE_DEBUG_HOST_EXE>
```

如果不打算打开 Visual Studio，只使用下方的 `BuildPlugins.bat` 构建模式，则不需要配置这两个变量。

## 构建

查看可用模式：

```powershell
.\BuildPlugins.bat --help
```

生成正式多语言 Release：

```powershell
.\BuildPlugins.bat publication
```

该命令对正式项目执行 Release x64 重建，包含四种文字 Variant、Language Settings、日文原文 fallback
和 publication 审校门禁。名称以括号包围的解决方案文件夹不会参与构建。输出目录：

```text
_build\publication\Fs_Plugins
```

## 不使用多语言设置

如果对多语言没有兴趣，可以直接构建不含 Language Settings 的固定语言版本：

```powershell
.\BuildPlugins.bat custom --default-language <language> --single-language
```

将 `<language>` 替换为：

- `en`：英文
- `ja`：日文原文
- `zh`：简体中文
- `ja-for-zh`：适用于简体中文编码环境的日文原文

`--single-language` 只构建所选文字 Variant，不构建 `F's Language Settings.aex`，并禁止效果插件
获取 Runtime；即使 After Effects 中存在 Language Settings，也不会进入多语言设置。

没有 Language Settings／Runtime 时，是否添加该参数的显示结果相同，插件都使用 `<language>`；存在
Runtime 时，不带该参数的版本服从多语言设置，带该参数的版本始终使用 `<language>`。输出位于
`_build\custom\single-<language>\Fs_Plugins`。

正式发布不包含固定语言版本，如有需要请自行构建。

## 本地化代码写法

文字宏的第二段写类型，最后一段写名称。显示文字时使用对应的包装宏。

| 写法 | 分类 | 用途 |
| --- | --- | --- |
| `#define L10N_PARAM_<NAME> "原文"` | — | 定义原文 |
| `AETEXT_PARAM(strings, L10N_PARAM_<NAME>)` | `Param` | 参数名称 |
| `AETEXT_LABEL(strings, L10N_PARAM_<NAME>)` | `Label` | 控件文字 |
| `AETEXT_POPUP(strings, L10N_PARAM_<NAME>_ITEMS)` | `Popup` | 下拉选项 |
| `AETEXT_TOPIC(strings, L10N_PARAM_<NAME>_TOPIC)` | `Topic` | 主题分组 |
| `AETEXT_ABOUT(strings, L10N_PLUGIN_<NAME>)` | `About` | 插件说明 |
| `AETEXT_ERROR(strings, L10N_ERR_<NAME>)` | `Error` | 错误消息 |
| `AETEXT_VERBATIM_PARAM(strings, L10N_PARAM_<NAME>)` | `Param` | 跳过翻译流程，等同于直接使用普通原文宏 |

新增、删除或修改 `L10N_*` 宏的原文，或更换 `AETEXT_*` 包装宏后，在审校工具中重新扫描对应插件。

## 贡献翻译

如果想修改或贡献翻译，请查看[翻译审校指南](../_localization/README.zh-CN.md)。

## 贡献代码

如果想贡献代码，请提交 Pull Request。
