#pragma once

/*
 * Localization switch for Posterization8bit.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's Posterization8bit"
    #define L10N_PLUGIN_DESC            "色调分离，内部全部按8Bit处理"
    #define L10N_PARAM_LEVEL            "级别"
    #define L10N_PARAM_GRAY_ONLY        "仅灰度"
    #define L10N_PARAM_ON               "开"
#else
    #define L10N_PLUGIN_NAME            "F's Posterization8bit"
    #define L10N_PLUGIN_DESC            "ポスタリゼーション　内部的に8Bitですべて行います"
    #define L10N_PARAM_LEVEL            "level"
    #define L10N_PARAM_GRAY_ONLY        "grayOnly"
    #define L10N_PARAM_ON               "on"
#endif



