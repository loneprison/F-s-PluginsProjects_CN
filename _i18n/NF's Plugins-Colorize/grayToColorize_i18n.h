#pragma once

/*
 * Localization switch for grayToColorize.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's grayToColorize"
    #define L10N_PLUGIN_DESC            "给素材快速上色"
    #define L10N_PARAM_ALPHA_THRESHOLD  "Alpha阈值"
    #define L10N_PARAM_MAT              "遮罩"
    #define L10N_PARAM_MAT_COLOR        "遮罩颜色"
    #define L10N_PARAM_COLOR_LEVEL      "颜色强度"
    #define L10N_PARAM_COLOR_COUNT      "颜色数量"
    #define L10N_PARAM_TARGET_COLOR     "目标颜色"
    #define L10N_PARAM_COLOR1           "颜色1"
    #define L10N_PARAM_COLOR2           "颜色2"
    #define L10N_PARAM_COLOR3           "颜色3"
    #define L10N_PARAM_COLOR4           "颜色4"
    #define L10N_PARAM_COLOR5           "颜色5"
    #define L10N_PARAM_ON               "开"
#else
    #define L10N_PLUGIN_NAME            "F's grayToColorize"
    #define L10N_PLUGIN_DESC            "適当な素材を適当に色を付ける"
    #define L10N_PARAM_ALPHA_THRESHOLD  "AlphaThreshold"
    #define L10N_PARAM_MAT              "Mat"
    #define L10N_PARAM_MAT_COLOR        "MatColor"
    #define L10N_PARAM_COLOR_LEVEL      "ColorLevel"
    #define L10N_PARAM_COLOR_COUNT      "ColorCount"
    #define L10N_PARAM_TARGET_COLOR     "TargetColor"
    #define L10N_PARAM_COLOR1           "Color1"
    #define L10N_PARAM_COLOR2           "Color2"
    #define L10N_PARAM_COLOR3           "Color3"
    #define L10N_PARAM_COLOR4           "Color4"
    #define L10N_PARAM_COLOR5           "Color5"
    #define L10N_PARAM_ON               "on"
#endif



