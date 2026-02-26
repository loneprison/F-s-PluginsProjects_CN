#pragma once

/*
 * Localization switch for PixelExtend.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's PixelExtend"
    #define L10N_PLUGIN_DESC            "扩展像素"
    #define L10N_PARAM_TARGET_TOPIC     "目标颜色"
    #define L10N_PARAM_RANGE            "阈值"
    #define L10N_PARAM_ON               "开"
    #define L10N_PARAM_TARGET_COLOR_EN  "启用方案"
    #define L10N_PARAM_TARGET_COLOR     "目标颜色"
    #define L10N_PARAM_EXTEND_TOPIC     "扩展"
    #define L10N_PARAM_TOP              "上"
    #define L10N_PARAM_TOP_RIGHT        "右上"
    #define L10N_PARAM_RIGHT            "右"
    #define L10N_PARAM_BOTTOM_RIGHT     "右下"
    #define L10N_PARAM_BOTTOM           "下"
    #define L10N_PARAM_BOTTOM_LEFT      "左下"
    #define L10N_PARAM_LEFT             "左"
    #define L10N_PARAM_TOP_LEFT         "左上"
    #define L10N_PARAM_NODRAW_TOPIC     "排除颜色"
    #define L10N_PARAM_NODRAW_COLOR_EN  "启用排除方案"
    #define L10N_PARAM_NODRAW_COLOR     "排除颜色"
    #define L10N_PARAM_TARGET_ONLY      "仅显示目标色"
#else
    #define L10N_PLUGIN_NAME            "F's PixelExtend"
    #define L10N_PLUGIN_DESC            "ピクセルの拡張"
    #define L10N_PARAM_TARGET_TOPIC     "Target"
    #define L10N_PARAM_RANGE            "Range"
    #define L10N_PARAM_ON               "on"
    #define L10N_PARAM_TARGET_COLOR_EN  "TargetColorEnabled"
    #define L10N_PARAM_TARGET_COLOR     "TargetColor"
    #define L10N_PARAM_EXTEND_TOPIC     "Extend"
    #define L10N_PARAM_TOP              "Top"
    #define L10N_PARAM_TOP_RIGHT        "Top_Right"
    #define L10N_PARAM_RIGHT            "Right"
    #define L10N_PARAM_BOTTOM_RIGHT     "Bottom_Right"
    #define L10N_PARAM_BOTTOM           "Bottom"
    #define L10N_PARAM_BOTTOM_LEFT      "Bottom_Left"
    #define L10N_PARAM_LEFT             "Left"
    #define L10N_PARAM_TOP_LEFT         "Top_Left"
    #define L10N_PARAM_NODRAW_TOPIC     "NoDraw"
    #define L10N_PARAM_NODRAW_COLOR_EN  "NoneColorEnabled"
    #define L10N_PARAM_NODRAW_COLOR     "NoneColor"
    #define L10N_PARAM_TARGET_ONLY      "TargetOnly"
#endif


