#pragma once

/*
 * Localization switch for Shine.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's Shine"
    #define L10N_PLUGIN_DESC            "伪shine插件"
    #define L10N_PARAM_POS              "位置"
    #define L10N_PARAM_LENGTH           "长度"
    #define L10N_PARAM_STRONG           "强度"
    #define L10N_PARAM_USE_COLOR        "填充颜色"
    #define L10N_PARAM_COLOR            "颜色"
    #define L10N_PARAM_ON               "开"
#else
    #define L10N_PLUGIN_NAME            "F's Shine"
    #define L10N_PLUGIN_DESC            "Fake shine"
    #define L10N_PARAM_POS              "pos"
    #define L10N_PARAM_LENGTH           "length"
    #define L10N_PARAM_STRONG           "strong"
    #define L10N_PARAM_USE_COLOR        "useColor"
    #define L10N_PARAM_COLOR            "color"
    #define L10N_PARAM_ON               "on"
#endif



