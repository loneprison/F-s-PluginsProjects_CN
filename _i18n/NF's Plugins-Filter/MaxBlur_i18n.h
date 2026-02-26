#pragma once

/*
 * Localization switch for MaxBlur.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's MaxBlur"
    #define L10N_PLUGIN_DESC            "带最大值效果的模糊"
    #define L10N_PARAM_BLUR             "模糊度"
    #define L10N_PARAM_MAX              "最大值"
    #define L10N_PARAM_HYPERBOLIC       "偏差"
#else
    #define L10N_PLUGIN_NAME            "F's MaxBlur"
    #define L10N_PLUGIN_DESC            "MaxBlur"
    #define L10N_PARAM_BLUR             "blur"
    #define L10N_PARAM_MAX              "max"
    #define L10N_PARAM_HYPERBOLIC       "hyperbolic"
#endif



