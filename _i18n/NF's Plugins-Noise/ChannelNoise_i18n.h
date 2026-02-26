#pragma once

/*
 * Localization switch for ChannelNoise.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */


#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's ChannelNoise"
    #define L10N_PLUGIN_DESC            "按通道添加杂色"
    #define L10N_PARAM_RED_NOISE        "红色杂色"
    #define L10N_PARAM_RED_OPACITY      "红色不透明度"
    #define L10N_PARAM_GREEN_NOISE      "绿色杂色"
    #define L10N_PARAM_GREEN_OPACITY    "绿色不透明度"
    #define L10N_PARAM_BLUE_NOISE       "蓝色杂色"
    #define L10N_PARAM_BLUE_OPACITY     "蓝色不透明度"
#else
    #define L10N_PLUGIN_NAME            "F's ChannelNoise"
    #define L10N_PLUGIN_DESC            "チャンネルごとにノイズをかけます"
    #define L10N_PARAM_RED_NOISE        "Red Noise(%)"
    #define L10N_PARAM_RED_OPACITY      "Red Opacity(%)"
    #define L10N_PARAM_GREEN_NOISE      "Green Noise(%)"
    #define L10N_PARAM_GREEN_OPACITY    "Green Opacity(%)"
    #define L10N_PARAM_BLUE_NOISE       "Blue Noise(%)"
    #define L10N_PARAM_BLUE_OPACITY     "Blue Opacity(%)"
#endif



