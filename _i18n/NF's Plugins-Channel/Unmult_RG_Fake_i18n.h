#pragma once

/*
 * Localization switch for Unmult_RG_Fake.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's Unmult_RG_Fake"
    #define L10N_PLUGIN_DESC            "伪 RG 反预乘"
#else
    #define L10N_PLUGIN_NAME            "F's Unmult_RG_Fake"
    #define L10N_PLUGIN_DESC            "Fake RG unmult"
#endif



