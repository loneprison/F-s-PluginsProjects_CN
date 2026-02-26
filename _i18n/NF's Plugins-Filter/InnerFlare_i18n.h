#pragma once

/*
 * Localization switch for InnerFlare.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's InnerFlare"
    #define L10N_PLUGIN_DESC            "内发光"
    #define L10N_PARAM_BLUR             "模糊度"
    #define L10N_PARAM_MAX              "大小"
    #define L10N_PARAM_HYPERBOLIC       "偏差"
    #define L10N_PARAM_REVERSE          "反转"
    #define L10N_PARAM_COLOR            "颜色"
#else
    #define L10N_PLUGIN_NAME            "F's InnerFlare"
    #define L10N_PLUGIN_DESC            "InnerFlare"
    #define L10N_PARAM_BLUR             "blur"
    #define L10N_PARAM_MAX              "max"
    #define L10N_PARAM_HYPERBOLIC       "hyperbolic"
    #define L10N_PARAM_REVERSE          "reverce"
    #define L10N_PARAM_COLOR            "color"
#endif



