#pragma once

/*
 * Localization switch for RandomMosaic.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's RandomMosaic"
    #define L10N_PLUGIN_DESC            "随机马赛克"
    #define L10N_PARAM_AMOUNT           "数量"
    #define L10N_PARAM_SIZE_MAX         "最大尺寸"
    #define L10N_PARAM_SIZE_MIN         "最小尺寸"
    #define L10N_PARAM_ASPECT_RANDOM    "随机长宽比"
    #define L10N_PARAM_BRIGHT_RANDOM    "随机亮度"
#else
    #define L10N_PLUGIN_NAME            "F's RandomMosaic"
    #define L10N_PLUGIN_DESC            "ランダムモザイク"
    #define L10N_PARAM_AMOUNT           "量"
    #define L10N_PARAM_SIZE_MAX         "サイズ(最大)"
    #define L10N_PARAM_SIZE_MIN         "サイズ(最小)"
    #define L10N_PARAM_ASPECT_RANDOM    "縦横のばらつき"
    #define L10N_PARAM_BRIGHT_RANDOM    "明るさのばらつき"
#endif



