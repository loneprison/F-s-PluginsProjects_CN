#pragma once

/*
 * Localization switch for TouchDrawStraght.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's TouchDrawStraght"
    #define L10N_PLUGIN_DESC            "绘制触控线"
    #define L10N_PARAM_RANDOM_SEED      "随机种子"
    #define L10N_PARAM_VALUE            "数量"
    #define L10N_PARAM_TARGET           "设置"
    #define L10N_PARAM_MODE             "模式"
    #define L10N_PARAM_MODE_ITEMS       "颜色|亮度差值|Alpha差值"
    #define L10N_PARAM_TARGET_COLOR     "目标颜色"
    #define L10N_PARAM_COLOR_RANGE      "颜色阈值"
    #define L10N_PARAM_DELTA_RANGE      "差值阈值"
    #define L10N_PARAM_ROT              "旋转"
    #define L10N_PARAM_INSIDE_LENGTH    "内侧长度"
    #define L10N_PARAM_INSIDE_LENGTH_RANDOM "内侧长度随机"
    #define L10N_PARAM_OUTSIDE_LENGTH   "外侧长度"
    #define L10N_PARAM_OUTSIDE_LENGTH_RANDOM "外侧长度随机"
    #define L10N_PARAM_COLOR            "颜色"
    #define L10N_PARAM_OPACITY          "不透明度"
    #define L10N_PARAM_OPACITY_RANDOM   "不透明度随机"
    #define L10N_PARAM_POINT_COUNT      "点数量"
    #define L10N_PARAM_POINT_LENGTH     "点长度"
    #define L10N_PARAM_BLOCK_VALUE      "块数量"
    #define L10N_PARAM_BLOCK_SIZE       "块尺寸"
    #define L10N_PARAM_ORIGINAL_BLEND   "与原始图像混合"
    #define L10N_PARAM_ON               "开"
#else
    #define L10N_PLUGIN_NAME            "F's TouchDrawStraght"
    #define L10N_PLUGIN_DESC            "タッチ線を描く"
    #define L10N_PARAM_RANDOM_SEED      "RandomSeed"
    #define L10N_PARAM_VALUE            "Value"
    #define L10N_PARAM_TARGET           "Target"
    #define L10N_PARAM_MODE             "Mode"
    #define L10N_PARAM_MODE_ITEMS       "Color|BrightnessDelta|AlphaDelta"
    #define L10N_PARAM_TARGET_COLOR     "Color"
    #define L10N_PARAM_COLOR_RANGE      "Color_Range"
    #define L10N_PARAM_DELTA_RANGE      "Delta_Range"
    #define L10N_PARAM_ROT              "Rot"
    #define L10N_PARAM_INSIDE_LENGTH    "Inside_Length"
    #define L10N_PARAM_INSIDE_LENGTH_RANDOM "Inside_Length_Random"
    #define L10N_PARAM_OUTSIDE_LENGTH   "Outside_Length"
    #define L10N_PARAM_OUTSIDE_LENGTH_RANDOM "Outside_Length_Random"
    #define L10N_PARAM_COLOR            "Color"
    #define L10N_PARAM_OPACITY          "Opacity"
    #define L10N_PARAM_OPACITY_RANDOM   "Opacity_Random"
    #define L10N_PARAM_POINT_COUNT      "Point_Count"
    #define L10N_PARAM_POINT_LENGTH     "Point_Length"
    #define L10N_PARAM_BLOCK_VALUE      "Block_Value"
    #define L10N_PARAM_BLOCK_SIZE       "Block_Size"
    #define L10N_PARAM_ORIGINAL_BLEND   "Original_Blend"
    #define L10N_PARAM_ON               "ON"
#endif



