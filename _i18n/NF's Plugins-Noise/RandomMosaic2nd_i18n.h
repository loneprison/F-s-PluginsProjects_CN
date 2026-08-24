#pragma once

/*
 * Localization switch for RandomMosaic2nd.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's RandomMosaic2nd"
    #define L10N_PLUGIN_DESC            "随机马赛克2"
    #define L10N_PARAM_AMOUNT           "数量"
    #define L10N_PARAM_STRENGTH         "随机亮度"
    #define L10N_PARAM_SIZE_X           "块宽度"
    #define L10N_PARAM_SIZE_Y           "块高度"
#else
    #define L10N_PLUGIN_NAME            "F's RandomMosaic2nd"
    #define L10N_PLUGIN_DESC            "ランダムモザイクその２"
    #define L10N_PARAM_AMOUNT           "量(%)"
    #define L10N_PARAM_STRENGTH         "強さ"
    #define L10N_PARAM_SIZE_X           "横サイズ"
    #define L10N_PARAM_SIZE_Y           "縦サイズ"
#endif



