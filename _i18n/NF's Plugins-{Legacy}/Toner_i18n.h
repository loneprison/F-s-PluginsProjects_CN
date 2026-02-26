#pragma once

/*
 * Localization switch for Toner.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's Toner"
    #define L10N_PLUGIN_DESC            "与三色调相同"
    #define L10N_PARAM_HIGHLIGHTS           "高光"
    #define L10N_PARAM_MIDTONES             "中间调"
    #define L10N_PARAM_SHADOWS              "阴影"
    #define L10N_PARAM_MIDTONES_OFFSET      "中间调偏移"
    #define L10N_PARAM_BLEND_WITH_ORIGINAL  "与原始图像混合"
#else
    #define L10N_PLUGIN_NAME            "F's Toner"
    #define L10N_PLUGIN_DESC            "トライトーンと同じ"
    #define L10N_PARAM_HIGHLIGHTS           "Highlights"
    #define L10N_PARAM_MIDTONES             "Midtones"
    #define L10N_PARAM_SHADOWS              "Shadows"
    #define L10N_PARAM_MIDTONES_OFFSET      "MidtonesOffset"
    #define L10N_PARAM_BLEND_WITH_ORIGINAL  "Blend w. Original"
#endif



