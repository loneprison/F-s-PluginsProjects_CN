#pragma once

/*
 * Localization switch for Thin.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's Thin"
    #define L10N_PLUGIN_DESC            "将目标颜色细线化"
    #define L10N_PARAM_THIN_VALUE       "收缩值"
    #define L10N_PARAM_ON               "开"
    #define L10N_PARAM_ENABLED_COLOR1   "方案1"
    #define L10N_PARAM_ENABLED_COLOR2   "方案2"
    #define L10N_PARAM_ENABLED_COLOR3   "方案3"
    #define L10N_PARAM_ENABLED_COLOR4   "方案4"
    #define L10N_PARAM_COLOR1           "颜色1"
    #define L10N_PARAM_COLOR2           "颜色2"
    #define L10N_PARAM_COLOR3           "颜色3"
    #define L10N_PARAM_COLOR4           "颜色4"
    #define L10N_PARAM_NO_WHITE         "不处理白色"
    #define L10N_PARAM_NO_ALPHA_ZERO    "不处理Alpha为0"
    #define L10N_PARAM_EDGE_FILTER      "边缘过滤"
    #define L10N_PARAM_LEVEL            "阈值"
#else
    #define L10N_PLUGIN_NAME            "F's Thin"
    #define L10N_PLUGIN_DESC            "ターゲット色を細線化します"
    #define L10N_PARAM_THIN_VALUE       "ThinValue"
    #define L10N_PARAM_ON               "on"
    #define L10N_PARAM_ENABLED_COLOR1   "EnabledColor1"
    #define L10N_PARAM_ENABLED_COLOR2   "EnabledColor2"
    #define L10N_PARAM_ENABLED_COLOR3   "EnabledColor3"
    #define L10N_PARAM_ENABLED_COLOR4   "EnabledColor4"
    #define L10N_PARAM_COLOR1           "Color1"
    #define L10N_PARAM_COLOR2           "Color2"
    #define L10N_PARAM_COLOR3           "Color3"
    #define L10N_PARAM_COLOR4           "Color4"
    #define L10N_PARAM_NO_WHITE         "NoWhite"
    #define L10N_PARAM_NO_ALPHA_ZERO    "NoAlphaZero"
    #define L10N_PARAM_EDGE_FILTER      "EdgeFilter"
    #define L10N_PARAM_LEVEL            "level"
#endif



