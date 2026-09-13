[English](../README.md) | [简体中文](README.zh-CN.md) | **日本語**

# F's Plugins Multilingual Edition

[開発ガイド](DEVELOPMENT.ja.md) · [翻訳レビュー](../_localization/README.ja.md) · [原作者の README](README.original.md)

Adobe After Effects 用 F's Plugins の Windows x64 多言語保守版です。日本語原文、簡体中国語、
英語の UI を提供し、元のプラグイン名と Match Name、および既存プロジェクトとの互換性を維持します。

> [!IMPORTANT]
> `v1.0.0` は準備中です。正式公開後は GitHub Releases の配布パッケージを使用してください。

## インストール

GitHub Releases から `Fs-Plugins-Multilingual-v1.0.0-win.zip` をダウンロードします。After Effects を
終了し、展開した `Fs_Plugins` ディレクトリを構成を保ったままプラグインディレクトリへコピーして、
After Effects を再起動してください。

配布物は手動インストール用の AEX アーカイブで、インストーラーではありません。中・英・日のガイドと
`LICENSE` を含みます。macOS はサポートしません。

## 言語

任意の F's エフェクトの **オプション／Options** から `F's Language Settings` を開きます。

- 自動
- English
- 日本語原文
- 簡体中国語
- 簡体中国語の文字コード環境向け日本語原文

AE 23 以降の自動モードは AE の UI 言語を使用し、簡体中国語では中国語、日本語では日本語原文、
その他では英語を選択します。AE 22 以前は Windows ANSI コードページを使用し、CP936 では中国語、
CP932 では日本語、その他または不明な場合は英語を選択します。

保存した設定を有効にするには After Effects を再起動してください。Language Settings がない、または
利用できない場合、各エフェクトは日本語原文を既定で使用します。

## 配布内容

ソリューションは 116 プロジェクトをビルドします。予定する配布物は 105 個の Production エフェクトと
1 個の Language Settings コンポーネントです。テスト、テンプレート、および次の重複または破損した
エフェクトは配布しません。

- `ChannelBlur`
- `Extract_Edge`
- `FsSSFrame`
- `ShineParallel`
- `VideoLine2nd`

## 主な修正

- `YuvControl`、`PixelSelector`、`Max`、`OpticalDiffusion`、`smokeThreshold`、
  `grayToColorize`、`Extract-Hi` の 16／32 bpc 処理を修正。
- `LineTrace`、`Max_Kasumi`、`TouchDraw`、`TouchDrawStraght` のパラメーターまたは描画動作を修正。
- `LineTrace` の 8／16／32 bpc における半透明ピクセルのカラーチャンネル計算を修正。
- `RandomShift` と `smokeThreshold` の誤ったラベルを修正。
- `GuideFrame` の履歴上の `Smooth` スロットを維持しつつ、無効なコントロールを無効化。
- Filter の About 表示を統一し、必要な不完全なテンプレート説明を置換。

## ソースと開発

ソースビルドと開発については[開発ガイド](DEVELOPMENT.ja.md)を参照してください。

## バージョン、上流、ライセンス

このプロジェクトは [bryful/F-s-PluginsProjects](https://github.com/bryful/F-s-PluginsProjects) の
[`47a9d2c`](https://github.com/bryful/F-s-PluginsProjects/commit/47a9d2c7a322e5ed0ea09c77bbd90cf5a54cb7bf)
を基点としています。配布版は `v1.0.0` から始まり、各 AEX の内部バージョンは置き換えません。
[原作者の README](README.original.md)は別に保存しています。

リポジトリルートの [MIT License](../LICENSE) と原作者の著作権表示を維持します。
