#pragma once

/*
 * Localization switch for CreateAlpha.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

 
#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's CreateAlpha"
    #define L10N_PLUGIN_DESC            "与 UnMult 相同"
#else
    #define L10N_PLUGIN_NAME            "F's CreateAlpha"
    #define L10N_PLUGIN_DESC            "UnMultと同じ"
#endif


