#pragma once

/*
 * Localization switch for MaxFast.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's MaxFast"
    #define L10N_PLUGIN_DESC            "快速最大值"
    #define L10N_PARAM_MAX              "半径"
#else
    #define L10N_PLUGIN_NAME            "F's MaxFast"
    #define L10N_PLUGIN_DESC            "MaxFast"
    #define L10N_PARAM_MAX              "max"
#endif



