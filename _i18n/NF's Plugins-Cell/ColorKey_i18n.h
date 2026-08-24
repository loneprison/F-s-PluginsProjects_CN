#pragma once

/*
 * Localization switch for ColorKey.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

 
#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's ColorKey"
    #define L10N_PLUGIN_DESC            "颜色键控"
    #define L10N_PARAM_COLOR            "主色"
    #define L10N_PARAM_RANGE            "容差"
    #define L10N_PARAM_UNDER_COLOR      "底色"
#else
    #define L10N_PLUGIN_NAME            "F's ColorKey"
    #define L10N_PLUGIN_DESC            "カラーキー"
    #define L10N_PARAM_COLOR            "color"
    #define L10N_PARAM_RANGE            "range"
    #define L10N_PARAM_UNDER_COLOR      "Undercolor"
#endif



