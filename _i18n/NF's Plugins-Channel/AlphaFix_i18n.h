#pragma once

/*
 * Localization switch for AlphaFix.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's AlphaFix"
    #define L10N_PLUGIN_DESC            "填充透明区域(类固态合成效果)"
    #define L10N_PARAM_BASE_COLOR       "背景色"
#else
    #define L10N_PLUGIN_NAME            "F's AlphaFix"
    #define L10N_PLUGIN_DESC            "Fill transparent areas."
    #define L10N_PARAM_BASE_COLOR       "背景色"
#endif


