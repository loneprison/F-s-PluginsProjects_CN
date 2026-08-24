#pragma once

/*
 * Localization switch for OpticalDiffusion.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's OpticalDiffusion"
    #define L10N_PLUGIN_DESC            "DF/Fog滤镜"
    #define L10N_PARAM_EXTRACT_ENABLED  "启用提取"
    #define L10N_PARAM_EXTRACT_TOPIC    "提取亮度"
    #define L10N_PARAM_BLACK_POINT      "黑场"
    #define L10N_PARAM_WHITE_POINT      "白场"
    #define L10N_PARAM_BLACK_SOFTNESS   "黑场柔和度"
    #define L10N_PARAM_WHITE_SOFTNESS   "白场柔和度"
    #define L10N_PARAM_INVERT           "反转"
    #define L10N_PARAM_EXTRACT_COLOR_TOPIC "追加选择的颜色"
    #define L10N_PARAM_USE_COUNT        "追加数量"
    #define L10N_PARAM_RANGE            "阈值"
    #define L10N_PARAM_COLOR1           "颜色1"
    #define L10N_PARAM_COLOR2           "颜色2"
    #define L10N_PARAM_COLOR3           "颜色3"
    #define L10N_PARAM_COLOR4           "颜色4"
    #define L10N_PARAM_COLOR5           "颜色5"
    #define L10N_PARAM_COLOR6           "颜色6"
    #define L10N_PARAM_COLOR7           "颜色7"
    #define L10N_PARAM_COLOR8           "颜色8"
    #define L10N_PARAM_MINIMAX_1ST      "最小最大1"
    #define L10N_PARAM_MINIMAX_2ND      "最小最大2"
    #define L10N_PARAM_BLUR             "模糊度"
    #define L10N_PARAM_BLEND_MODE       "混合模式"
    #define L10N_PARAM_BLEND_ITEMS      "无|正常|变亮|变暗|屏幕|相乘"
    #define L10N_PARAM_BLEND_OPACITY    "混合不透明度"
    #define L10N_PARAM_NOISE            "杂色"
#else
    #define L10N_PLUGIN_NAME            "F's OpticalDiffusion"
    #define L10N_PLUGIN_DESC            "DF/Fogフィルタ"
    #define L10N_PARAM_EXTRACT_ENABLED  "Extract Enabled"
    #define L10N_PARAM_EXTRACT_TOPIC    "Extract lightness"
    #define L10N_PARAM_BLACK_POINT      "Black Point"
    #define L10N_PARAM_WHITE_POINT      "White Point"
    #define L10N_PARAM_BLACK_SOFTNESS   "Black Softness"
    #define L10N_PARAM_WHITE_SOFTNESS   "White Softness"
    #define L10N_PARAM_INVERT           "Invert"
    #define L10N_PARAM_EXTRACT_COLOR_TOPIC "Extract TargetColor"
    #define L10N_PARAM_USE_COUNT        "Use Count"
    #define L10N_PARAM_RANGE            "Range"
    #define L10N_PARAM_COLOR1           "Color1"
    #define L10N_PARAM_COLOR2           "Color2"
    #define L10N_PARAM_COLOR3           "Color3"
    #define L10N_PARAM_COLOR4           "Color4"
    #define L10N_PARAM_COLOR5           "Color5"
    #define L10N_PARAM_COLOR6           "Color6"
    #define L10N_PARAM_COLOR7           "Color7"
    #define L10N_PARAM_COLOR8           "Color8"
    #define L10N_PARAM_MINIMAX_1ST      "Minimax 1st"
    #define L10N_PARAM_MINIMAX_2ND      "Minimax 2nd"
    #define L10N_PARAM_BLUR             "Blur"
    #define L10N_PARAM_BLEND_MODE       "Blend mode"
    #define L10N_PARAM_BLEND_ITEMS      "None|Normal|Lighten|Darkne|Screen|Multiply"
    #define L10N_PARAM_BLEND_OPACITY    "Blend Opacity"
    #define L10N_PARAM_NOISE            "Noise"
#endif



