#pragma once

/*
 * Localization switch for whiteInOut.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's whiteInOut"
    #define L10N_PLUGIN_DESC            "简易的白入白出插件"
    #define L10N_PARAM_VALUE            "过渡完成"
#else
    #define L10N_PLUGIN_NAME            "F's whiteInOut"
    #define L10N_PLUGIN_DESC            "簡易的な白入白出プラグイン"
    #define L10N_PARAM_VALUE            "value"
#endif



