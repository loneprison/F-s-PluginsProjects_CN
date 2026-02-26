# F-s-PluginsProjects_CN
- 该项目Fork于原f's项目的(47a9d2c)版本
- 该项目的目的有三个
    1. 编译在中文电脑上可以正确显示日文版本的插件（原作者已做适配但并没有人编译并传播）
    2. 制作中文的汉化版本
    
## 该项目与原项目的主代码区别
- 为了更优雅的实现目的2而引入了一个i18n方案，此改动会影响到所有项目文件
- 为部分遗漏的16bpc适配进行支持(即便那不是必要的,但黄色感叹号确实看上去令人烦躁)
- 由于原项目已经停止支持,所以大范围调整了原本散落的项目工程结构,方便正确高效的的管理文件
- 我注意到了部分不应该编译的项目,我不准备动它们或者编译
    - 三个未构建完成的插件，ShineParallel,Extract_Edge，ChannelBlur
    - 一个测试用插件Spark_Test
    - 一个模板工程NFsSkelton

## 主代码功能改动:
- 修正了一个bug,该bug曾导致F's PixelSelector的fillColor_opacity功能在16/32bpc下失效
- 修正了一个bug,该bug曾导致F's VideoLine2nd的功能在16/32bpc下失效
- 修正了一个bug,该bug曾导致F's grayToColorize的Mat在16bpc下的意外结果
- 修正了一个bug,该bug曾导致F's YuvControl在16/32bpc下的意外结果
- 修复 FsLibrary 中的多处关键问题
    - 修复 FsMat 中多个颜色通道写入错误（blue 误写为 green）
        - 该问题曾导致 F's OpticalDiffusion 颜色严重偏差
        - 该问题曾导致 F's Max 在含半透明像素且使用负值时出现错误的蓝色边缘
    - 修复 32bpc 路径中通过调用 16bpc 逻辑规避崩溃的历史问题；根因是 32bpc 缓冲区分配错误
        - 该问题曾导致上述插件及 F's smokeThreshold 在 32bpc 下实际精度被限制到 16bpc
        - 该问题还会导致在强制切回 32bpc 逻辑时，上述三个插件可能引发 AE 崩溃
- 修正了一个bug,该bug曾导致LineTrace的填充黑不生效的问题

- ！！！2026-02-26 请注意！当前上诉修改并未拉取Fork并合并到原项目,这一工作将在汉化完成后一次性进行（避免反复提交）

## 汉化版本 V0.1（待校对）
- 截至 2026-02-26：已完成第一轮批量汉化接入与预校对，当前阶段为“可用但待人工逐项校对”。
- 当前仓库主线以中文可维护性为目标，后续会继续做术语统一、界面文案校对与回归验证。

---
## 以下为AI记录
---

## 提交简报（最近一次）
### 1) 中文翻译版本V0.1(待校对)（2026-02-26）
- 提交标题：`中文翻译版本V0.1(待校对)`
- 变更统计：`673 files changed, 9355 insertions(+), 5568 deletions(-)`
- 本次提交覆盖范围：
  - 批量接入与补齐 `_i18n/` 多分类插件头文件，形成统一的本地化入口。
  - 大量更新 `Win/*.vcxproj` 与 `Win/*.vcxproj.filters`，把 i18n 头文件纳入工程并保持过滤器映射一致。
  - 新增 `Directory.Build.Category.props`、`Directory.Build.i18n.props`，并配合 `_tools/i18n_build.ps1` 统一构建与汉化处理流程。
  - 清理多处历史 `.sln` 入口，进一步收敛工程结构，减少重复维护点。
  - 同步更新主 README，明确当前版本状态与后续人工校对计划。
- 当前结论：
  - 当前已完成一个版本的完全汉化。
  - 下一阶段将等待校对工作者进行专业术语校对。

------ 原README ------
# F's Plugins New and Next
Adone After EffectsのEffectsPlugin集のソース一式とWindowsバイナリです。<br>
(**No macOS support** / **不支持 macOS**)<br>
　

昔から趣味でコツコツと作っていたものです。<br>
趣味といっても僕自身日本のアニメ制作者なので業務に使えます。<br>
<br>

ダウンロードは今ページの右上あたりにある<b>Releases</b>でできます。<br>
2026/02/01 更新しました。大きなバグがない限りしばらく更新しません<br>
<br>

## <b>**残念なお知らせ**</b><br>
2025年度からAdobeCCの料金がかなり高価に値上がりしたので、プライベートではとっても払えないので次回の更新はしないことにしました。
その為F's Pluginsの更新は今以上にかなりスローペースになります。<br>
一応僕も仕事でたまには使うのでAfter Effects自体のバージョンに合わせて再ビルドは行うつもりです(SDKの更新に合わせます)<br>

## 今後の予定
今後F's Pluginsの開発はメンテナンスにとどめて、NF-Pluginsという新しいプラグイン集を開発する予定です。<br>
NF-Pluginsはあえて互換性(matchName)を無くしてモダンな開発環境を目指します。<br>
F’sは、ラッパー関数の嵐でコードが読みにくくなっているので、NF-Pluginsではシンプルで他のプラグインへの移植性を重視する予定です。<br>


***

最近モチベーションが全然無くてメンテナンスさぼり気味です。自分でほとんど使わなくなってしまったせいですかな？<br>
少しでもやる気が出るようにAmazonの欲しいものリストを試しに公開してみます。<br>
* [bry-fulの欲しいものリスト(https://www.amazon.co.jp/hz/wishlist/ls/2ME5VSS8WJOX8?ref_=wl_sha)<br>


## _tools フォルダについて<br>
_toolsフォルダ内にはプラグイン開発に便利なツールを入れています。<br>
今までC#で作ってましたが、PowerShellスクリプトに置き換えました。<br>
詳細は_toolsフォルダ内のREADME.mdを見てください。<br>


## 関連プロジェクト ##
F-s-PluginsProjects_TLed<br>
(Oops, sorry!　^^;) 詳細はリンク先で<br>
[https://github.com/ilyasok/F-s-PluginsProjects_TLed](https://github.com/ilyasok/F-s-PluginsProjects_TLed)
<br>
F's Plugins for MacOS<br>
詳細はリンク先で<br>
[https://github.com/CubeZeero/F-s-PluginsProjects_forMac](https://github.com/CubeZeero/F-s-PluginsProjects_forMac)<br>

DaVinci Resolve - Fusion 移植版<br>
詳細はリンク先で<br>
[https://github.com/akahito-ot/Fs-Plugins-Fusion-Ports](https://github.com/akahito-ot/Fs-Plugins-Fusion-Ports)<br>

chinese translated version<br>
[https://www.lookae.com/fsplugins/](https://www.lookae.com/fsplugins/)<br>

## ビルド時の注意 ##
今回から**Directory.Build.props**/**Directory.Build.Targets**を使ってプロジェクト設定の一括変更を行っています。<br>
VS2026でSDK2025を使うとものすごいWarnigが出るのでDirectory.Build.propsで抑制しています。プロパティのUIで変更しても上書きされるので注意です。<br>
<br>
出力ファイル名にDirectory.Build.Targetで指定して自動的に日付が入るようにしました。Debug時の出力先もここで変更しています。<br>
<br>
こんな便利な機能あるの知らなかった。<br>
<br>

## 進捗
バージョン管理の方法をいろいろ考えましたが、プラグインファイル名に日付を入れるという一番チープな方法を採用しました。<br>
<br>
Visual studio 2026に変更。SDKを2025に変更（まだ動作確認できていません）<br>
Visual studioのプロジェクト設定を一括で変更できるDirectory.Build.props/Directory.Build.targetsを使って、出力ファイル名に日付を入れるようにしました。<br>
<br>
CellLineEraset.aexの高速化<br>
MaxFast.aexの追加。<br>
[FsCellLineEraser_20260123.zip](https://github.com/bryful/F-s-PluginsProjects/raw/refs/heads/master/_DL_windowsbinary/FsCellLineEraser_20260123.zip)<br>
<br>
TargetGrad.aex/TargetGradradical.aex<br>
グラデーションエフェクトを追加<br>
[FsTargetGrad_finalBeta.zip](https://github.com/bryful/F-s-PluginsProjects/raw/refs/heads/master/_DL_windowsbinary/FsTargetGrad_finalBeta.zip) からDLしてください。近いうちに正式版出します。
<br>
F's sputteringAlpha.aex/F's sputteringSplash.aexが内部エラーで落ちるバグに対処。<br>
まだ原因が特定できていないので、直っていないかも。<br>
MainLineReplaceも同様なバグがあったので修正。<br>
[Fssputtering_MainLineReplace20250109.zip](https://github.com/bryful/F-s-PluginsProjects/raw/refs/heads/master/_DL_windowsbinary/Fssputtering_MainLineReplace20250109.zip)<br>
[FssputteringAS20241229.zip](https://github.com/bryful/F-s-PluginsProjects/raw/refs/heads/master/_DL_windowsbinary/FssputteringAS20241229.zip)<br>

AE2022のマルチフレームレンダーに対応させました。<br>
***

Fs_Target.hの
```
#if defined(SUPPORT_SMARTFX)
#define FS_OUT_FLAGS2 134222921
#else
#define FS_OUT_FLAGS2 134217801
#endif
```
に変えただけなので中国語バージョン作る時はそこだけの変更で良いはずです。

CC2019用からgithubでバイナリーの配布も行います。
**_DL_windowsbinary**フォルダの中に入っています。



<br>

# 変更点
2026/0２/01<br>
とりあえず今回の更新はこれで最後にします。<br>
2025/07/21<br>
プラグインファイル名の規則を変更。詳細は添付ファイル内の「必ず読んでください.txt」を見てください。<br>
<br>
2024/04/14<br>
SDK2023でbuildし直しました。<br>
<br>
2022/03/15<br>
AE2022のマルチフレームレンダリングに対応しました。 <br>
<br>
2020/11/11<br>
NFsライブラリのひな型を作成しました。<br>
<br>
2020/08/15<br>
コンパイラを VS2017からVS2019へ変更。<br>
それに伴い、構造体メンバーのアライメントを16byteに変更。/Zp16<br>

* F'sgrayToCountourLine.aexを追加
ポスタリゼーションの変形バージョンです、諧調を均等に割らずにHi/Mid/Loで諧調を変えられます。
* F's grayToWaveLine.aexを追加
グレー画像を疑似３Dプロッタ風に描画します。昔のSF映画のモニタぽいものができます。

2020/07/26
CC2020 SDKに変更。

2020/03/20
CC2019 SDKに変更。
数が多くなって使いにくくなったので、カテゴリーを整理しました。
* F's Plugins-Cell
 アニメのスムージングなしのセルをターゲットにしたものです。
* F's Plugins-Channel
 チャンネル操作系です。
* F's Plugins-Colorize
 色を付けるものです。
* F's Plugins-Draw
 描画系のものです。
* F's Plugins-Filter
 フィルターエフェクト系です。
* F's Plugins-Noise
 ノイズフィルタ系です。
* F's Plugins-{Legacy}
 もう使って欲しくない。或いは使い道のないものです。
 デバッグ前のものや、紙飛行機作成補助プラグインとかになります。
### 追加プラグイン
* F's EdgeLine-Hi.aex  指定した2色の境界に線を描きます。その時描く向きを指定できます。
* F's Flare.aex 白黒マスクにグローを付けます。透過光です。
* F's graytoneToColorize.aex 簡易コロラマです。ゴールド処理やサーモグラフ処理に使います。
* F's PixelExtend.aex 指定した色を指定した方向に膨張させます。
* F's Posterization8bit.aex ポスタリゼーションです。標準と違って内部は8bit処理です。
* F's Scanline.aex スキャンライン。昔の古いパソコンの偶数列が黒いラインの状態ができます。
* F's YuvControl.aex YUV版のRGBAコントロールです。

# 開発環境
Visual studio 2026 Community C++

AfterEffectsSDK CC2025
SDKはCC2025を使用しています。

# Setup
プロジェクト等はSDKフォルダ内のExampleフォルダ内へ配置してください。

こんな感じです。

        /AfterEffectsSDK
        └─Examples
            ├─AEGP
            ├─Effect
            ├─F's PluginsProjects
            │  ├─AlphaFix
            │  ├─AlphaThreshold
            │  ├─AnimatedNoise
            <省略>
            │  ├─PluginSkeleton
            <省略>
            │  ├─whiteInOut
            ├─GP
            ├─Headers
            ├─Resources
            ├─Template
            ├─UI
            └─Util

# 使い方

SDKはCC2025を想定しています。

**NFsLibrary**ではCC2020以降のサポートとなります。

F's PluginsProjectsフォルダを各バージョンのExamplesフォルダに移動すればできます。


PluginのBinaryはAfter EffectsのPlug-insへコピーしてください。

例)
"C:\Program Files\Adobe\Adobe After Effects CC 2024\Support Files\Plug-ins"

# デバッグ

1. デバッグ構成時のプロパティでバイナリの出力先をインストールされたAEの**Plug-ins**フォルダに設定します。SDKでは"[Program Files]\Adobe\Common\Plug-ins\[**version**]\MediaCore\"が推奨されていますが、バージョンがこっそり上がって困ったことがありました。
> C:\Program Files\Adobe\Adobe After Effects 2040\Support Files\Plug-ins\debug\
2. プロパティ「デバッグ」のコマンドをAEの実行ファイルにします。
> C:\Program Files\Adobe\Adobe After Effects 2040\Support Files\AfterFX.exe
3. その他必要な項目（作業ディレクトリ）も設定します。
4. 念のためにプラグインフォルダの設定をフルコントロールにしておきます。アクセス権が無くて書き出しができなことがあります。

以上の設定を行えば、デバッグが可能になります。



# ライセンス

This software is released under the MIT License, see LICENSE.

このソースコードを使用する時はMITライセンスに準じてください。
独自にビルドして映像制作使う場合は、使用プラグインリスト等にここの[url](https://github.com/bryful)を入れてもらえればOKです（まぁ入れなくても僕は気にしません）

このプログラムを映像制作に使用した場合も特に制限ありません。一応MITライセンスの条件である著作権表示および本許諾表示として

**プラグイン協力 bry-ful**

とクレジットしてくれると嬉しいです。プラグイン協力以外でも適当な肩書であれば別のものに変えても構いません。<br>

パチンコパチスロ遊技機開発会社の方へ<br>
使用に関しては特に制限ありません。許諾も必要ありません。使用料も発生しません。
これは今後絶対に変わりません。



# Authors

bry-ful [Hiroshi Furuhashi]<br>
github: [https://github.com/bryful](https://github.com/bryful)<br>
twitter:[bryful](https://twitter.com/bryful)<br>

# Thanks

Nanae Furuhashi

My daughter,
May her soul rest in peace．




