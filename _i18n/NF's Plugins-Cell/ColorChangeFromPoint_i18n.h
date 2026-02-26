#pragma once

/*
 * Localization switch for ColorChangeFromPoint.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

 
#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's ColorChangeFromPoint"
    #define L10N_PLUGIN_DESC            "按取样点颜色替换匹配像素"
    #define L10N_PARAM_TARGET_POINT     "取样点"
    #define L10N_PARAM_COLOR            "替换颜色"
#else
    #define L10N_PLUGIN_NAME            "F's ColorChangeFromPoint"
    #define L10N_PLUGIN_DESC            "指定点の色と一致する画素を置換"
    #define L10N_PARAM_TARGET_POINT     "TargetColorPoint"
    #define L10N_PARAM_COLOR            "Color"
#endif



