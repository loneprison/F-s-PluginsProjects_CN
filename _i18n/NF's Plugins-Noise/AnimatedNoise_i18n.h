#pragma once

/*
 * Localization switch for AnimatedNoise.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */


#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's AnimatedNoise"
    #define L10N_PLUGIN_DESC            "动画风格的杂色"
    #define L10N_ON_LABEL               "开"
    #define L10N_PARAM_ANIM_EVERY_FRAME "每帧变化"
    #define L10N_PARAM_ANIM_MOTION      "随机种子"
    #define L10N_PARAM_NOISE_AMOUNT     "杂色数量"
    #define L10N_PARAM_NOISE_STRENGTH   "杂色强度"
    #define L10N_PARAM_COLOR_NOISE      "彩色杂色"
    #define L10N_PARAM_BLOCK_AMOUNT     "块状杂色数量"
    #define L10N_PARAM_BLOCK_STRENGTH   "块状杂色强度"
    #define L10N_PARAM_BLOCK_WIDTH      "块宽度"
    #define L10N_PARAM_BLOCK_HEIGHT     "块高度"
    #define L10N_PARAM_COLOR_BLOCK      "彩色块状杂色"
#else
    #define L10N_PLUGIN_NAME            "F's AnimatedNoise"
    #define L10N_PLUGIN_DESC            "アニメチックなノイズ"
    #define L10N_ON_LABEL               "ON"
    #define L10N_PARAM_ANIM_EVERY_FRAME "毎フレームでノイズ変化"
    #define L10N_PARAM_ANIM_MOTION      "ノイズの動き"
    #define L10N_PARAM_NOISE_AMOUNT     "ノイズの量"
    #define L10N_PARAM_NOISE_STRENGTH   "ノイズの強さ"
    #define L10N_PARAM_COLOR_NOISE      "カラーノイズ"
    #define L10N_PARAM_BLOCK_AMOUNT     "ブロックの量"
    #define L10N_PARAM_BLOCK_STRENGTH   "ブロックの強さ"
    #define L10N_PARAM_BLOCK_WIDTH      "ブロックの横幅(px)"
    #define L10N_PARAM_BLOCK_HEIGHT     "ブロックの縦幅(px)"
    #define L10N_PARAM_COLOR_BLOCK      "カラーブロック"
#endif



