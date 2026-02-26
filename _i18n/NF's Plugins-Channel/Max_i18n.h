#pragma once

/*
 * Localization switch for Max.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's Max"
    #define L10N_PLUGIN_DESC            "最大/最小"
    #define L10N_PARAM_VALUE            "半径"
    #define L10N_PARAM_SCANLINE         "方向"
    #define L10N_PARAM_SCANLINE_ITEMS   "水平和垂直|水平|垂直"
    #define L10N_PARAM_CHANNEL          "通道"
    #define L10N_PARAM_CHANNEL_ITEMS    "Alpha 和颜色|颜色|Alpha"
    #define L10N_PARAM_OUT_ONLY         "仅输出"
#else
    #define L10N_PLUGIN_NAME            "F's Max"
    #define L10N_PLUGIN_DESC            "最大/最小です"
    #define L10N_PARAM_VALUE            "value"
    #define L10N_PARAM_SCANLINE         "ScanLine"
    #define L10N_PARAM_SCANLINE_ITEMS   "Horizon+Vurtual|Horizon|Vurtual"
    #define L10N_PARAM_CHANNEL          "Channel"
    #define L10N_PARAM_CHANNEL_ITEMS    "RGB+Alpha|RGB|alpha"
    #define L10N_PARAM_OUT_ONLY         "OutOnly"
#endif



