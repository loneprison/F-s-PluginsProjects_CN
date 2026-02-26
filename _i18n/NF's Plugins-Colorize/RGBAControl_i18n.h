#pragma once

/*
 * Localization switch for RGBAControl.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's RGBAControl"
    #define L10N_PLUGIN_DESC            "RGB单独亮度调整"
    #define L10N_PARAM_RED              "红"
    #define L10N_PARAM_GREEN            "绿"
    #define L10N_PARAM_BLUE             "蓝"
    #define L10N_PARAM_ALPHA            "Alpha"
#else
    #define L10N_PLUGIN_NAME            "F's RGBAControl"
    #define L10N_PLUGIN_DESC            "RGB個別の明るさ調整"
    #define L10N_PARAM_RED              "Red(%)"
    #define L10N_PARAM_GREEN            "Green(%)"
    #define L10N_PARAM_BLUE             "Blue(%)"
    #define L10N_PARAM_ALPHA            "Alpha(%)"
#endif



