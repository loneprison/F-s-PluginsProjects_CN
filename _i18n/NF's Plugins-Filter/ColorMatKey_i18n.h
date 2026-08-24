#pragma once

/*
 * Localization switch for ColorMatKey.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */


#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's ColorMatKey"
    #define L10N_PLUGIN_DESC            "颜色遮罩键"
    #define L10N_PARAM_INVERT_ALPHA     "反转 Alpha"
    #define L10N_PARAM_ON               "开"
    #define L10N_PARAM_ENABLED0         "提取方案1"
    #define L10N_PARAM_COLOR0           "颜色1"
    #define L10N_PARAM_BORDER0          "阈值1"
    #define L10N_PARAM_SOFTNESS0        "柔和度1"
    #define L10N_PARAM_ENABLED1         "提取方案2"
    #define L10N_PARAM_COLOR1           "颜色2"
    #define L10N_PARAM_BORDER1          "阈值2"
    #define L10N_PARAM_SOFTNESS1        "柔和度2"
    #define L10N_PARAM_ENABLED2         "提取方案3"
    #define L10N_PARAM_COLOR2           "颜色3"
    #define L10N_PARAM_BORDER2          "阈值3" 
    #define L10N_PARAM_SOFTNESS2        "柔和度3"
    #define L10N_PARAM_ENABLED3         "提取方案4"
    #define L10N_PARAM_COLOR3           "颜色4"
    #define L10N_PARAM_BORDER3          "阈值4"
    #define L10N_PARAM_SOFTNESS3        "柔和度4"
#else
    #define L10N_PLUGIN_NAME            "F's ColorMatKey"
    #define L10N_PLUGIN_DESC            "カラーマットキー"
    #define L10N_PARAM_INVERT_ALPHA     "InvertAlpha"
    #define L10N_PARAM_ON               "on"
    #define L10N_PARAM_ENABLED0         "Enabled0"
    #define L10N_PARAM_COLOR0           "Color0"
    #define L10N_PARAM_BORDER0          "Border0"
    #define L10N_PARAM_SOFTNESS0        "Softness0"
    #define L10N_PARAM_ENABLED1         "Enabled1"
    #define L10N_PARAM_COLOR1           "Color1"
    #define L10N_PARAM_BORDER1          "Border1"
    #define L10N_PARAM_SOFTNESS1        "Softness1"
    #define L10N_PARAM_ENABLED2         "Enabled2"
    #define L10N_PARAM_COLOR2           "Color2"
    #define L10N_PARAM_BORDER2          "Border2"
    #define L10N_PARAM_SOFTNESS2        "Softness2"
    #define L10N_PARAM_ENABLED3         "Enabled3"
    #define L10N_PARAM_COLOR3           "Color3"
    #define L10N_PARAM_BORDER3          "Border3"
    #define L10N_PARAM_SOFTNESS3        "Softness3"
#endif


