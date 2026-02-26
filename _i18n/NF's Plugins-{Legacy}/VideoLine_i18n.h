#pragma once

/*
 * Localization switch for VideoLine.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's VideoLine"
    #define L10N_PLUGIN_DESC            "类似电视扫描线"
    #define L10N_PARAM_LINE_BRIGHTNESS  "线条亮度"
    #define L10N_PARAM_LINE_HEIGHT      "线条宽度"
    #define L10N_PARAM_LINE_POSITION    "反转贴图"
    #define L10N_PARAM_REVERSE          "开"
    #define L10N_PARAM_INTERVAL         "间距补正"
    #define L10N_PARAM_DIR              "方向"
    #define L10N_PARAM_DIR_ITEMS        "水平|垂直"
    #define L10N_PARAM_OFFSET           "相位"
#else
    #define L10N_PLUGIN_NAME            "F's VideoLine"
    #define L10N_PLUGIN_DESC            "テレビの走査線っぽいもの"
    #define L10N_PARAM_LINE_BRIGHTNESS  "ラインの明るさ(%)"
    #define L10N_PARAM_LINE_HEIGHT      "ラインの高さ(dot)"
    #define L10N_PARAM_LINE_POSITION    "ラインの位置"
    #define L10N_PARAM_REVERSE          "反転する"
    #define L10N_PARAM_INTERVAL         "間隔補正(dot)"
    #define L10N_PARAM_DIR              "方向"
    #define L10N_PARAM_DIR_ITEMS        "水平|垂直"
    #define L10N_PARAM_OFFSET           "オフセット"
#endif



