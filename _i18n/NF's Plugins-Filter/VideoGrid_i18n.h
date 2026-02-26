#pragma once

/*
 * Localization switch for VideoGrid.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's VideoGrid"
    #define L10N_PLUGIN_DESC            "Video网格滤镜"
    #define L10N_PARAM_GRID_SIZE        "网格尺寸"
    #define L10N_PARAM_MODE             "马赛克"
    #define L10N_PARAM_MOSAIC           "开"
    #define L10N_PARAM_HILIGHT          "高光"
    #define L10N_PARAM_SHADOW           "阴影"
    #define L10N_PARAM_LINE_WIDTH       "边框宽度"
#else
    #define L10N_PLUGIN_NAME            "F's VideoGrid"
    #define L10N_PLUGIN_DESC            "Videoグリッドフィルタ"
    #define L10N_PARAM_GRID_SIZE        "グリッドサイズ"
    #define L10N_PARAM_MODE             "モード"
    #define L10N_PARAM_MOSAIC           "モザイク"
    #define L10N_PARAM_HILIGHT          "ハイライト(%)"
    #define L10N_PARAM_SHADOW           "シャドウ(%)"
    #define L10N_PARAM_LINE_WIDTH       "ライン幅"
#endif



