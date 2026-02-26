#pragma once

/*
 * Localization switch for grayToWaveLine.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's grayToWaveLine"
    #define L10N_PLUGIN_DESC            "由灰度图绘制图形"
    #define L10N_PARAM_SAMPLE_X_COUNT   "X采样数"
    #define L10N_PARAM_SAMPLE_Y_COUNT   "Y采样数"
    #define L10N_PARAM_DRAW_POS         "位置"
    #define L10N_PARAM_GRAPH_X_SCALE    "X缩放"
    #define L10N_PARAM_GRAPH_Y_MAX      "最大高度"
    #define L10N_PARAM_GRAPH_TILT       "图形倾斜"
    #define L10N_PARAM_GRAPH_X_OFFSET   "图形X偏移"
    #define L10N_PARAM_GRAPH_Y_OFFSET   "图形Y偏移"
    #define L10N_PARAM_LINE_HEIGHT      "波形宽度"
    #define L10N_PARAM_GRAPH_COLOR      "波形颜色"
    #define L10N_PARAM_BASE_COLOR       "基线颜色"
    #define L10N_PARAM_MODE             "显示模式"
    #define L10N_PARAM_MODE_ITEMS       "波形+基线|仅波形|仅基线"
#else
    #define L10N_PLUGIN_NAME            "F's grayToWaveLine"
    #define L10N_PLUGIN_DESC            "グレー画像からグラフを描画"
    #define L10N_PARAM_SAMPLE_X_COUNT   "SampleXCount"
    #define L10N_PARAM_SAMPLE_Y_COUNT   "SampleYCount"
    #define L10N_PARAM_DRAW_POS         "DrawPos"
    #define L10N_PARAM_GRAPH_X_SCALE    "GraphXScale"
    #define L10N_PARAM_GRAPH_Y_MAX      "GraphYMax"
    #define L10N_PARAM_GRAPH_TILT       "GraphTilt"
    #define L10N_PARAM_GRAPH_X_OFFSET   "GraphXOffset"
    #define L10N_PARAM_GRAPH_Y_OFFSET   "GraphYOffset"
    #define L10N_PARAM_LINE_HEIGHT      "LineHeight"
    #define L10N_PARAM_GRAPH_COLOR      "GraphColor"
    #define L10N_PARAM_BASE_COLOR       "BaseColor"
    #define L10N_PARAM_MODE             "mode"
    #define L10N_PARAM_MODE_ITEMS       "Wave+Base|WaveOnly|BaseOnly"
#endif



