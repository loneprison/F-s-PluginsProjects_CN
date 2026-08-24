#pragma once

/*
 * Localization switch for Flare.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's Flare"
    #define L10N_PLUGIN_DESC            "发光滤镜"
    #define L10N_PARAM_ON               "开"
    #define L10N_PARAM_BASE_ON          "显示图像"
    #define L10N_PARAM_BASE_COLOR       "着色"
    #define L10N_PARAM_BASE_OPACITY     "图像不透明度"
    #define L10N_PARAM_MODE             "提取模式"
    #define L10N_PARAM_MODE_ITEMS       "明亮度(反向)|明亮度|Alpha|原始图像"
    #define L10N_PARAM_TOPIC            "发光_"
    #define L10N_PARAM_ENABLED          "启用_"
    #define L10N_PARAM_BORDER_TOPIC     "边框 (图像模式除外)_"
    #define L10N_PARAM_BORDER           "启用边框_"
    #define L10N_PARAM_INSIDE           "内边框_"
    #define L10N_PARAM_OUTSIDE          "外边框_"
    #define L10N_PARAM_REV              "反向 (图像模式除外)_1"
    #define L10N_PARAM_REV_ITEMS        "无|反向|反向并保留原 Alpha"
    #define L10N_PARAM_MAX              "扩展_"
    #define L10N_PARAM_BLUR             "模糊_"
    #define L10N_PARAM_COLOR            "颜色 (图像模式除外)_"
    #define L10N_PARAM_BLEND            "混合模式_"
    #define L10N_PARAM_BLEND_ITEMS      "屏幕|相加|正常"
    #define L10N_PARAM_OPACITY          "不透明度_"
#else
    #define L10N_PLUGIN_NAME            "F's Flare"
    #define L10N_PLUGIN_DESC            "透過光フレア"
    #define L10N_PARAM_ON               "on"
    #define L10N_PARAM_BASE_ON          "baseOn"
    #define L10N_PARAM_BASE_COLOR       "baseColor"
    #define L10N_PARAM_BASE_OPACITY     "baseOpacity"
    #define L10N_PARAM_MODE             "mode"
    #define L10N_PARAM_MODE_ITEMS       "WhitebackMask|BlackbackMask|Alpha|Image"
    #define L10N_PARAM_TOPIC            "flare_"
    #define L10N_PARAM_ENABLED          "enabled_"
    #define L10N_PARAM_BORDER_TOPIC     "border(except_image)_"
    #define L10N_PARAM_BORDER           "border_"
    #define L10N_PARAM_INSIDE           "inside_"
    #define L10N_PARAM_OUTSIDE          "outside_"
    #define L10N_PARAM_REV              "reverse(except_image)_"
    #define L10N_PARAM_REV_ITEMS        "none|reverse|reverseAndOriginalAlpha"
    #define L10N_PARAM_MAX              "max_"
    #define L10N_PARAM_BLUR             "blur_"
    #define L10N_PARAM_COLOR            "color(except_image)_"
    #define L10N_PARAM_BLEND            "blend_"
    #define L10N_PARAM_BLEND_ITEMS      "screen|add|normal"
    #define L10N_PARAM_OPACITY          "opacity_"
#endif



