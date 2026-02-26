#pragma once

/*
 * Localization switch for TouchDrawCenter.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's TouchDrawCenter"
    #define L10N_PLUGIN_DESC            "绘制从周围汇聚的线条"
    #define L10N_PARAM_RANDOM_SEED      "随机种子"
    #define L10N_PARAM_CENTER           "中心点"
    #define L10N_PARAM_LENGTH           "长度"
    #define L10N_PARAM_LENGTH_RANDOM    "随机长度"
    #define L10N_PARAM_VALUE            "数量"
    #define L10N_PARAM_COLOR            "颜色"
    #define L10N_PARAM_OPACITY          "不透明度"
    #define L10N_PARAM_OPACITY_RANDOM   "随机不透明度"
    #define L10N_PARAM_POINT_COUNT      "点数量"
    #define L10N_PARAM_POINT_LENGTH     "点长度"
    #define L10N_PARAM_ORIGINAL_BLEND   "与原始图像混合"
    #define L10N_PARAM_ON               "开"
#else
    #define L10N_PLUGIN_NAME            "F's TouchDrawCenter"
    #define L10N_PLUGIN_DESC            "周囲からの集中線を描きます"
    #define L10N_PARAM_RANDOM_SEED      "RandomSeed"
    #define L10N_PARAM_CENTER           "Center"
    #define L10N_PARAM_LENGTH           "Length"
    #define L10N_PARAM_LENGTH_RANDOM    "Length_Random"
    #define L10N_PARAM_VALUE            "Value"
    #define L10N_PARAM_COLOR            "Color"
    #define L10N_PARAM_OPACITY          "Opacity"
    #define L10N_PARAM_OPACITY_RANDOM   "Opacity_Random"
    #define L10N_PARAM_POINT_COUNT      "Point_Count"
    #define L10N_PARAM_POINT_LENGTH     "Point_Length"
    #define L10N_PARAM_ORIGINAL_BLEND   "Original_Blend"
    #define L10N_PARAM_ON               "ON"
#endif



