#pragma once

/*
 * Localization switch for VideoLine2nd.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's VideoLine2nd"
    #define L10N_PLUGIN_DESC            "类似电视扫描线（修复版）"
    #define L10N_PARAM_LINE_BRIGHTNESS  "线条亮度"
    #define L10N_PARAM_LINE_HEIGHT      "线条宽度"
    #define L10N_PARAM_INTERVAL         "间距补正"
    #define L10N_PARAM_DIR              "方向"
    #define L10N_PARAM_DIR_ITEMS        "水平|垂直"
#else
    #define L10N_PLUGIN_NAME            "F's VideoLine2nd"
    #define L10N_PLUGIN_DESC            "テレビの走査線っぽいもの バグフィックスバージョン"
    #define L10N_PARAM_LINE_BRIGHTNESS  "ラインの明るさ(%)"
    #define L10N_PARAM_LINE_HEIGHT      "ラインの高さ(dot)"
    #define L10N_PARAM_INTERVAL         "間隔補正(dot)"
    #define L10N_PARAM_DIR              "方向"
    #define L10N_PARAM_DIR_ITEMS        "水平|垂直"
#endif



