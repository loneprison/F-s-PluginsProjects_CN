#pragma once

/*
 * Localization switch for SelectColor.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's SelectColor"
    #define L10N_PLUGIN_DESC            "从上色单元创建颜色遮罩"
    #define L10N_PARAM_TARGET0          "方案0"
    #define L10N_PARAM_TARGET1          "方案1"
    #define L10N_PARAM_TARGET2          "方案2"
    #define L10N_PARAM_TARGET3          "方案3"
    #define L10N_PARAM_TARGET4          "方案4"
    #define L10N_PARAM_TARGET5          "方案5"
    #define L10N_PARAM_TARGET6          "方案6"
    #define L10N_PARAM_TARGET7          "方案7"
    #define L10N_PARAM_ENABLE           "启用"
    #define L10N_PARAM_COLOR0           "颜色0"
    #define L10N_PARAM_COLOR1           "颜色1"
    #define L10N_PARAM_COLOR2           "颜色2"
    #define L10N_PARAM_COLOR3           "颜色3"
    #define L10N_PARAM_COLOR4           "颜色4"
    #define L10N_PARAM_COLOR5           "颜色5"
    #define L10N_PARAM_COLOR6           "颜色6"
    #define L10N_PARAM_COLOR7           "颜色7"
    #define L10N_PARAM_REVERSE          "反转"
    #define L10N_PARAM_REVERSE_ON       "开"
    #define L10N_PARAM_TOLERANCE        "阈值"
#else
    #define L10N_PLUGIN_NAME            "F's SelectColor"
    #define L10N_PLUGIN_DESC            "ペイントセルから色マスク作成"
    #define L10N_PARAM_TARGET0          "Target0"
    #define L10N_PARAM_TARGET1          "Target1"
    #define L10N_PARAM_TARGET2          "Target2"
    #define L10N_PARAM_TARGET3          "Target3"
    #define L10N_PARAM_TARGET4          "Target4"
    #define L10N_PARAM_TARGET5          "Target5"
    #define L10N_PARAM_TARGET6          "Target6"
    #define L10N_PARAM_TARGET7          "Target7"
    #define L10N_PARAM_ENABLE           "実行する"
    #define L10N_PARAM_COLOR0           "color0"
    #define L10N_PARAM_COLOR1           "color1"
    #define L10N_PARAM_COLOR2           "color2"
    #define L10N_PARAM_COLOR3           "color3"
    #define L10N_PARAM_COLOR4           "color4"
    #define L10N_PARAM_COLOR5           "color5"
    #define L10N_PARAM_COLOR6           "color6"
    #define L10N_PARAM_COLOR7           "元の色7"
    #define L10N_PARAM_REVERSE          "Rev"
    #define L10N_PARAM_REVERSE_ON       "反転する"
    #define L10N_PARAM_TOLERANCE        "許容値"
#endif



