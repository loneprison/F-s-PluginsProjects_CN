#pragma once

/*
 * Localization switch for RgbToAlpha.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's RgbToAlpha"
    #define L10N_PLUGIN_DESC            "将RGB值写入Alpha。"
    #define L10N_PARAM_FILL_COLOR       "填充颜色"
    #define L10N_PARAM_FILL_ITEMS       "白|黑|指定色"
    #define L10N_PARAM_CUSTOM_COLOR     "指定颜色"
    #define L10N_PARAM_REVERSE_ALPHA    "反转Alpha"
    #define L10N_PARAM_REV              "反转"
#else
    #define L10N_PLUGIN_NAME            "F's RgbToAlpha"
    #define L10N_PLUGIN_DESC            "RGBの値をAlphaへ書き込みます。"
    #define L10N_PARAM_FILL_COLOR       "塗りつぶし色"
    #define L10N_PARAM_FILL_ITEMS       "白|黒|指定色"
    #define L10N_PARAM_CUSTOM_COLOR     "指定色"
    #define L10N_PARAM_REVERSE_ALPHA    "Alphaを反転"
    #define L10N_PARAM_REV              "Rev"
#endif



