#pragma once

/*
 * Localization switch for RandomLineNoise.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's RandomLineNoise"
    #define L10N_PLUGIN_DESC            "随机横线杂色"
    #define L10N_PARAM_NOISE_AMOUNT     "杂色数量"
    #define L10N_PARAM_NOISE_STRONG     "杂色强度"
    #define L10N_PARAM_LEN_MIN          "最小长度"
    #define L10N_PARAM_LEN_MAX          "最大长度"
    #define L10N_PARAM_NOISE_COLOR      "彩色杂色"
    #define L10N_PARAM_COLOR            "开"
    #define L10N_PARAM_NOISE_WIDTH      "宽度"
    #define L10N_PARAM_VERTICAL         "垂直方向"
    #define L10N_PARAM_VERTICAL_SHORT   "开"
#else
    #define L10N_PLUGIN_NAME            "F's RandomLineNoise"
    #define L10N_PLUGIN_DESC            "ランダムな横線ノイズ"
    #define L10N_PARAM_NOISE_AMOUNT     "ノイズ量"
    #define L10N_PARAM_NOISE_STRONG     "ノイズの強さ(%)"
    #define L10N_PARAM_LEN_MIN          "ノイズの長さ(最小)"
    #define L10N_PARAM_LEN_MAX          "ノイズの長さ(最大)"
    #define L10N_PARAM_NOISE_COLOR      "ノイズの色"
    #define L10N_PARAM_COLOR            "カラー"
    #define L10N_PARAM_NOISE_WIDTH      "ノイズの幅"
    #define L10N_PARAM_VERTICAL         "縦方向に"
    #define L10N_PARAM_VERTICAL_SHORT   "縦"
#endif



