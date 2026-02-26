#pragma once

/*
 * Localization switch for AlphaThreshold.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */


#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's alphaThreshold"
    #define L10N_PLUGIN_DESC            "Alpha 通道阈值化"
    #define L10N_PARAM_ALPHA_THRESHOLD  "Alpha 阈值"
#else
    #define L10N_PLUGIN_NAME            "F's alphaThreshold"
    #define L10N_PLUGIN_DESC            "Threshold the alpha channel."
    #define L10N_PARAM_ALPHA_THRESHOLD  "AlphaThreshold"
#endif



