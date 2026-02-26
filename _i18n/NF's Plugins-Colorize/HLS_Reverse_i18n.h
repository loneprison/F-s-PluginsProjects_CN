#pragma once

/*
 * Localization switch for HLS_Reverse.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's HLS_Reverse"
    #define L10N_PLUGIN_DESC            "反转HLS的指定通道"
    #define L10N_PARAM_HUE              "色相"
    #define L10N_PARAM_LIGHTNESS        "明度"
    #define L10N_PARAM_SATURATION       "饱和度"
    #define L10N_PARAM_REVERSE          "反转"
    #define L10N_PARAM_BLEND_ORIGINAL   "与原始图像混合(%)"
#else
    #define L10N_PLUGIN_NAME            "F's HLS_Reverse"
    #define L10N_PLUGIN_DESC            "HLS のLを反転させる"
    #define L10N_PARAM_HUE              "hue"
    #define L10N_PARAM_LIGHTNESS        "lightness"
    #define L10N_PARAM_SATURATION       "saturation"
    #define L10N_PARAM_REVERSE          "Reverse"
    #define L10N_PARAM_BLEND_ORIGINAL   "blend original(%)"
#endif



