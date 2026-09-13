[English](DEVELOPMENT.en.md) | [简体中文](DEVELOPMENT.zh-CN.md) | **日本語**

# ソースビルドと開発

[ユーザーガイド](README.ja.md) · [翻訳レビュー](../_localization/README.ja.md) · [原作者の README](README.original.md)

## ソースを取得する

1. [Adobe After Effects 開発者ページ](https://developer.adobe.com/after-effects/)から
   After Effects SDK 25.2 をダウンロードして展開します。
2. SDK の `AfterEffectsSDK\Examples` を開き、そのディレクトリで PowerShell を起動します。
3. リポジトリを clone し、プロジェクトディレクトリへ移動します。

```powershell
git clone https://github.com/loneprison/F-s-PluginsProjects_Multilingual.git
cd .\F-s-PluginsProjects_Multilingual
```

## 開発環境

- Visual Studio 2026 の **C++ によるデスクトップ開発**
- Python 3.12
- `uv`

`uv` が未インストールの場合は、PowerShell で次を実行します。

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

PowerShell を開き直して確認します。

```powershell
uv --version
```

## ローカルパス

Visual Studio は次の 2 つの変数を使用します。

- `AE_PLUGIN_BUILD_DIR`：プラグインのビルド出力先
- `AE_DEBUG_HOST_EXE`：Debug／F5 で使う `AfterFX.exe` のパス

設定方法は 2 つあります。

Windows のユーザー環境変数に追加します。「システムのプロパティ」の「環境変数」で手動編集するか、
PowerShell で次を実行します。

```powershell
New-Item -ItemType Directory -Force 'D:\AePluginBuild'
[Environment]::SetEnvironmentVariable('AE_PLUGIN_BUILD_DIR', 'D:\AePluginBuild', 'User')
[Environment]::SetEnvironmentVariable(
    'AE_DEBUG_HOST_EXE',
    'C:\Program Files\Adobe\Adobe After Effects 2024\Support Files\AfterFX.exe',
    'User'
)
```

設定後、Visual Studio とターミナルを開き直してください。

または、プロジェクトディレクトリにある `Directory.Build.props` の最初の `PropertyGroup` に記入します。

```xml
<AE_PLUGIN_BUILD_DIR Condition="'$(AE_PLUGIN_BUILD_DIR)'==''">D:\AePluginBuild</AE_PLUGIN_BUILD_DIR>
<AE_DEBUG_HOST_EXE Condition="'$(AE_DEBUG_HOST_EXE)'==''">C:\Program Files\Adobe\Adobe After Effects 2024\Support Files\AfterFX.exe</AE_DEBUG_HOST_EXE>
```

Visual Studio を開かず、下記の `BuildPlugins.bat` ビルドモードだけを使う場合、これらの変数を設定する
必要はありません。

## ビルド

利用できるモードを表示：

```powershell
.\BuildPlugins.bat --help
```

正式な多言語 Release を作成：

```powershell
.\BuildPlugins.bat publication
```

正式プロジェクトを Release x64 でリビルドし、4 種類の文字 Variant、Language Settings、日本語原文
fallback、publication レビューゲートを含めます。名前が括弧で囲まれたソリューションフォルダーは
ビルドされません。出力先：

```text
_build\publication\Fs_Plugins
```

## 多言語設定を使わない場合

多言語設定が不要な場合は、Language Settings を含まない固定言語版をビルドできます。

```powershell
.\BuildPlugins.bat custom --default-language <language> --single-language
```

`<language>` は次のいずれかに置き換えます。

- `en`：英語
- `ja`：日本語原文
- `zh`：簡体中国語
- `ja-for-zh`：簡体中国語の文字コード環境向け日本語原文

`--single-language` は選択した文字 Variant だけをビルドし、`F's Language Settings.aex` を
ビルドせず、各 effect による Runtime の取得も無効にします。このため、After Effects に別の
Language Settings が存在しても多言語設定は使用されません。

Language Settings／Runtime がない環境では、この引数の有無にかかわらず表示は同じ
`<language>` になります。Runtime がある環境では、引数なしの版は多言語設定に従い、引数ありの版は
常に `<language>` を使用します。出力先は `_build\custom\single-<language>\Fs_Plugins` です。

正式リリースには固定言語版を含めません。必要な場合はソースからビルドしてください。

## ローカライズコードの書き方

文字マクロの 2 番目の部分には種類、最後の部分には名前を書きます。文字を表示する場所では対応する
ラッパーを使用します。

| 書き方 | 分類 | 用途 |
| --- | --- | --- |
| `#define L10N_PARAM_<NAME> "原文"` | — | 原文を定義 |
| `AETEXT_PARAM(strings, L10N_PARAM_<NAME>)` | `Param` | パラメーター名 |
| `AETEXT_LABEL(strings, L10N_PARAM_<NAME>)` | `Label` | コントロールラベル |
| `AETEXT_POPUP(strings, L10N_PARAM_<NAME>_ITEMS)` | `Popup` | ドロップダウン項目 |
| `AETEXT_TOPIC(strings, L10N_PARAM_<NAME>_TOPIC)` | `Topic` | トピックグループ |
| `AETEXT_ABOUT(strings, L10N_PLUGIN_<NAME>)` | `About` | プラグインの説明 |
| `AETEXT_ERROR(strings, L10N_ERR_<NAME>)` | `Error` | エラーメッセージ |
| `AETEXT_VERBATIM_PARAM(strings, L10N_PARAM_<NAME>)` | `Param` | 翻訳処理を通さず、通常の原文マクロを直接使う場合と同じ |

`L10N_*` の原文を追加、削除、変更した場合、または `AETEXT_*` ラッパーを変更した場合は、
レビューツールで対応するプラグインを再スキャンします。

## 翻訳への貢献

翻訳を変更または提供する場合は、[翻訳レビューガイド](../_localization/README.ja.md)を参照してください。

## コードへの貢献

コードを提供する場合は、Pull Request を送信してください。
