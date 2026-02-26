#pragma once

/*
 * Localization switch for Scanline.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's Scanline"
    #define L10N_PLUGIN_DESC            "扫描线插件"
    #define L10N_PARAM_HEIGHT           "扫描线宽度"
    #define L10N_PARAM_LEVEL0           "奇数行亮度"
    #define L10N_PARAM_OPACITY0         "奇数行不透明度"
    #define L10N_PARAM_LEVEL1           "偶数行亮度"
    #define L10N_PARAM_OPACITY1         "偶数行不透明度"
    #define L10N_PARAM_DIR              "方向"
    #define L10N_PARAM_DIR_ITEMS        "水平|垂直"
#else
    #define L10N_PLUGIN_NAME            "F's Scanline"
    #define L10N_PLUGIN_DESC            "スキャンラインプラグイン"
    #define L10N_PARAM_HEIGHT           "ラインの太さ(pixel)"
    #define L10N_PARAM_LEVEL0           "奇数列ラインの明るさ(%)"
    #define L10N_PARAM_OPACITY0         "奇数列ラインの不透明度(%)"
    #define L10N_PARAM_LEVEL1           "偶数列ラインの明るさ(%)"
    #define L10N_PARAM_OPACITY1         "偶数列ラインの不透明度(%)"
    #define L10N_PARAM_DIR              "方向"
    #define L10N_PARAM_DIR_ITEMS        "水平|垂直"
#endif



