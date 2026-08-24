#pragma once

/*
 * Localization switch for AlphaHyperbolic.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's AlphaHyperbolic"
    #define L10N_PLUGIN_DESC            "Alpha 边缘偏移调整"
    #define L10N_PARAM_HYPERBOLIC       "Alpha 偏移"
#else
    #define L10N_PLUGIN_NAME            "F's AlphaHyperbolic"
    #define L10N_PLUGIN_DESC            "AlphaHyperbolic"
    #define L10N_PARAM_HYPERBOLIC       "hyperbolic"
#endif



