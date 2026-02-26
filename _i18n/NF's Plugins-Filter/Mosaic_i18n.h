#pragma once

/*
 * Localization switch for Mosaic.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's Mosaic"
    #define L10N_PLUGIN_DESC            "马赛克"
    #define L10N_PARAM_SIZE             "大小"
    #define L10N_PARAM_POSITION         "位置"
    #define L10N_PARAM_FLICKER          "随机颜色"
    #define L10N_PARAM_FLICKER_GRAY     "仅亮度"
    #define L10N_PARAM_FRAME_FLICKER    "动态变化"
    #define L10N_PARAM_ON               "开"
#else
    #define L10N_PLUGIN_NAME            "F's Mosaic"
    #define L10N_PLUGIN_DESC            "モザイク"
    #define L10N_PARAM_SIZE             "サイズ"
    #define L10N_PARAM_POSITION         "位置"
    #define L10N_PARAM_FLICKER          "ちらつき"
    #define L10N_PARAM_FLICKER_GRAY     "ちらつきをグレーに"
    #define L10N_PARAM_FRAME_FLICKER    "フレーム毎にちらつかせる"
    #define L10N_PARAM_ON               "ON"
#endif



