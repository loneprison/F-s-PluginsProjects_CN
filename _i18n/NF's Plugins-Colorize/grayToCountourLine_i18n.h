#pragma once

/*
 * Localization switch for grayToCountourLine.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's grayToCountourLine"
    #define L10N_PLUGIN_DESC            "由灰度图生成等高线"
    #define L10N_PARAM_COUNT_LO         "阴影颜色数量"
    #define L10N_PARAM_COUNT_MID        "中间调颜色数量"
    #define L10N_PARAM_COUNT_HI         "高光颜色数量"
    #define L10N_PARAM_DRAW_COLOR       "显示颜色列表"
    #define L10N_PARAM_ON               "开"
#else
    #define L10N_PLUGIN_NAME            "F's grayToCountourLine"
    #define L10N_PLUGIN_DESC            "グレー画像から等高線を作成"
    #define L10N_PARAM_COUNT_LO         "Count_Lo"
    #define L10N_PARAM_COUNT_MID        "Count_Mid"
    #define L10N_PARAM_COUNT_HI         "Count_Hi"
    #define L10N_PARAM_DRAW_COLOR       "DrawCol"
    #define L10N_PARAM_ON               "on"
#endif



