[English](../README.md) | **简体中文** | [日本語](README.ja.md)

# F's Plugins Multilingual Edition

[开发文档](DEVELOPMENT.zh-CN.md) · [翻译审校](../_localization/README.zh-CN.md) · [原作者 README](README.original.md)

F's Plugins 的 Windows x64 多语言维护版，面向 Adobe After Effects，提供日文原文、简体中文和英文
界面，并保留原插件名称与 Match Name，兼容既有工程。

> [!IMPORTANT]
> `v1.0.0` 仍在准备中。正式发布后请使用 GitHub Releases 中的发行包。

## 安装

从 GitHub Releases 下载 `Fs-Plugins-Multilingual-v1.0.0-win.zip`。关闭 After Effects，将解压后的
`Fs_Plugins` 完整复制到 After Effects 插件目录，保留原目录结构，然后重新启动 After Effects。

发行物是手动安装的 AEX 压缩包，不是安装程序。包内包含中、英、日三语说明及 `LICENSE`。不支持 macOS。

## 语言

从任一 F's 效果的“选项／Options”打开 `F's Language Settings`。

- 自动
- English
- 日文原文
- 简体中文
- 适用于简体中文编码环境的日文原文表示

AE 23 及以上的“自动”模式按 AE 界面语言选择：简体中文使用中文，日文使用日文原文，其他语言使用英文。
AE 22 及以下按 Windows ANSI 代码页选择：CP936 使用中文，CP932 使用日文，其他或未知代码页使用英文。

保存后需要重新启动 After Effects 才可生效。如果 Language Settings 缺失或不可用，各效果会默认使用
日文原文。

## 发行内容

解决方案共构建 116 个项目。计划发行 105 个 Production 效果和 1 个 Language Settings 组件。测试、
模板以及以下效果由于重复或损坏不发布：

- `ChannelBlur`
- `Extract_Edge`
- `FsSSFrame`
- `ShineParallel`
- `VideoLine2nd`

## 主要修复

- 修复 `YuvControl`、`PixelSelector`、`Max`、`OpticalDiffusion`、`smokeThreshold`、
  `grayToColorize` 和 `Extract-Hi` 的 16／32 bpc 处理问题。
- 修复 `LineTrace`、`Max_Kasumi`、`TouchDraw` 和 `TouchDrawStraght` 的参数或渲染问题。
- 修复 `LineTrace` 在 8／16／32 bpc 下处理半透明像素时的颜色通道计算错误。
- 修正 `RandomShift` 和 `smokeThreshold` 的错误标签。
- 保留 `GuideFrame` 的历史 `Smooth` 参数槽位，但禁用无效控件。
- 统一 Filter 的 About 窗口，并替换必要的不完整模板说明。

## 源码与开发

源码构建与开发见[开发文档](DEVELOPMENT.zh-CN.md)。

## 版本、上游与许可

本项目基于 [bryful/F-s-PluginsProjects](https://github.com/bryful/F-s-PluginsProjects) 的
[`47a9d2c`](https://github.com/bryful/F-s-PluginsProjects/commit/47a9d2c7a322e5ed0ea09c77bbd90cf5a54cb7bf)
继续维护。整套发行版本从 `v1.0.0` 开始，不替代各 AEX 的内部版本；[原作者 README](README.original.md)
单独保留。

项目沿用仓库根目录的 [MIT License](../LICENSE)，并保留原作者版权声明。
