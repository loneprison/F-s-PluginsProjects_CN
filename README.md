**English** | [简体中文](_docs/README.zh-CN.md) | [日本語](_docs/README.ja.md)

# F's Plugins Multilingual Edition

[Development](_docs/DEVELOPMENT.en.md) · [Translation review](_localization/README.md) · [Original README](_docs/README.original.md)

A maintained Windows x64 edition of F's Plugins for Adobe After Effects, with original Japanese,
Simplified Chinese, and English interfaces. Plugin names and Match Names remain compatible with
existing projects.

> [!IMPORTANT]
> `v1.0.0` is still in preparation. Use the final GitHub Release package when it becomes available.

## Install

Download `Fs-Plugins-Multilingual-v1.0.0-win.zip` from GitHub Releases, close After Effects, and copy
the extracted `Fs_Plugins` directory to an After Effects plugin directory. Keep its directory
structure, then restart After Effects.

The archive is not an installer. It includes user guides in Simplified Chinese, English, and Japanese,
plus `LICENSE`. macOS is not supported.

## Language

Open **Options** from any F's effect to use `F's Language Settings`.

- Automatic
- English
- Original Japanese
- Simplified Chinese
- Original Japanese represented for a Simplified Chinese encoding environment

Automatic mode uses the After Effects UI language on AE 23 and later: Simplified Chinese selects
Chinese, Japanese selects the original Japanese, and other languages select English. AE 22 and earlier
use the Windows ANSI code page: CP936 selects Chinese, CP932 selects Japanese, and other or unknown
code pages select English.

Restart After Effects for saved changes to take effect. If Language Settings is missing or unavailable,
effects default to the original Japanese text.

## Release contents

The solution builds 116 projects. The planned release contains 105 Production effects and one Language
Settings component. Tests, templates, and the following effects are not released because they are
duplicates or broken:

- `ChannelBlur`
- `Extract_Edge`
- `FsSSFrame`
- `ShineParallel`
- `VideoLine2nd`

## Main fixes

- Restored or corrected 16/32-bpc processing in `YuvControl`, `PixelSelector`, `Max`,
  `OpticalDiffusion`, `smokeThreshold`, `grayToColorize`, and `Extract-Hi`.
- Fixed parameter or rendering behavior in `LineTrace`, `Max_Kasumi`, `TouchDraw`, and
  `TouchDrawStraght`.
- Corrected `LineTrace`'s color-channel calculations for semitransparent pixels in 8/16/32 bpc.
- Corrected labels in `RandomShift` and `smokeThreshold`.
- Disabled `GuideFrame`'s unused `Smooth` control while preserving its historical parameter slot.
- Aligned Filter About windows and replaced incomplete template descriptions where needed.

## Source and development

For source builds and development, see the [developer guide](_docs/DEVELOPMENT.en.md).

## Version, upstream, and license

This edition continues from
[`47a9d2c`](https://github.com/bryful/F-s-PluginsProjects/commit/47a9d2c7a322e5ed0ea09c77bbd90cf5a54cb7bf)
of [bryful/F-s-PluginsProjects](https://github.com/bryful/F-s-PluginsProjects). Its suite version starts
at `v1.0.0` and does not replace the internal versions of individual AEX files. The
[original README](_docs/README.original.md) is preserved separately.

Licensed under the repository's [MIT License](LICENSE), with the original copyright notice retained.
