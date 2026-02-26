#pragma once

/*
 * Localization switch for ExpsColors.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

 
#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's ExpsColors"
    #define L10N_PLUGIN_DESC            "表达式颜色控制"
    #define L10N_PARAM_ON               "启用"
    #define L10N_PARAM_ON_VALUE         "开"
    #define L10N_PARAM_COLOR            "颜色"
    #define L10N_PARAM_COLOR0           "颜色0"
    #define L10N_PARAM_COLOR1           "颜色1"
    #define L10N_PARAM_COLOR2           "颜色2"
    #define L10N_PARAM_COLOR3           "颜色3"
    #define L10N_PARAM_COLOR4           "颜色4"
    #define L10N_PARAM_COLOR5           "颜色5"
    #define L10N_PARAM_COLOR6           "颜色6"
    #define L10N_PARAM_COLOR7           "颜色7"
    #define L10N_PARAM_COLOR8           "颜色8"
    #define L10N_PARAM_COLOR9           "颜色9"
#else
    #define L10N_PLUGIN_NAME            "F's ExpsColors"
    #define L10N_PLUGIN_DESC            "式用カラー制御"
    #define L10N_PARAM_ON               "ON"
    #define L10N_PARAM_ON_VALUE         "on"
    #define L10N_PARAM_COLOR            "color"
    #define L10N_PARAM_COLOR0           "color0"
    #define L10N_PARAM_COLOR1           "color1"
    #define L10N_PARAM_COLOR2           "color2"
    #define L10N_PARAM_COLOR3           "color3"
    #define L10N_PARAM_COLOR4           "color4"
    #define L10N_PARAM_COLOR5           "color5"
    #define L10N_PARAM_COLOR6           "color6"
    #define L10N_PARAM_COLOR7           "color7"
    #define L10N_PARAM_COLOR8           "color8"
    #define L10N_PARAM_COLOR9           "color9"
#endif

