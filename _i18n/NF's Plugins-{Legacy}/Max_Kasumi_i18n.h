#pragma once

/*
 * Localization switch for Max_Kasumi.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's Max_Kasumi"
    #define L10N_PLUGIN_DESC            "最大最小值插件"
    #define L10N_PARAM_VALUE            "半径"
    #define L10N_PARAM_SCANLINE         "方向"
    #define L10N_PARAM_SCANLINE_ITEMS   "水平和垂直|水平|垂直"
    #define L10N_PARAM_CHANNEL          "通道"
    #define L10N_PARAM_CHANNEL_ITEMS    "RGB+Alpha|RGB|Alpha"
#else
    #define L10N_PLUGIN_NAME            "F's Max_Kasumi"
    #define L10N_PLUGIN_DESC            "最大最小値プラグイン"
    #define L10N_PARAM_VALUE            "Value"
    #define L10N_PARAM_SCANLINE         "ScanLine"
    #define L10N_PARAM_SCANLINE_ITEMS   "Horizon+Vertical|Horizon|Vertical"
    #define L10N_PARAM_CHANNEL          "Channel"
    #define L10N_PARAM_CHANNEL_ITEMS    "RGB+Alpha|RGB|Alpha"
#endif



