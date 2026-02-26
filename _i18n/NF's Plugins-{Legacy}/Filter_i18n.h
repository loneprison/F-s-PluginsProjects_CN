#pragma once

/*
 * Localization switch for Filter.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's Filter"
    #define L10N_PLUGIN_DESC            "多层滤镜效果"
    #define L10N_PARAM_ON               "开"
    #define L10N_PARAM_BASE_ENABLED     "显示原始图像"
    #define L10N_PARAM_BASE_OPACITY     "原始图像不透明度"
    #define L10N_PARAM_TOPIC            "滤镜_"
    #define L10N_PARAM_ENABLED          "激活滤镜_"
    #define L10N_PARAM_EXTRACT          "提取_"
    #define L10N_PARAM_EXTRACT_ITEMS    "无|高光|阴影"
    #define L10N_PARAM_BORDER_HI        "高光阈值_"
    #define L10N_PARAM_SOFTNESS_HI      "高光柔和度_"
    #define L10N_PARAM_BORDER_LO        "阴影阈值_"
    #define L10N_PARAM_SOFTNESS_LO      "阴影柔和度_"
    #define L10N_PARAM_BRIGHTNESS       "亮度_"
    #define L10N_PARAM_MINMAX           "最小/最大_"
    #define L10N_PARAM_MAX              "扩展_"
    #define L10N_PARAM_BLUR             "模糊_"
    #define L10N_PARAM_OPACITY          "不透明度_"
    #define L10N_PARAM_BLEND            "混合模式_"
    #define L10N_PARAM_BLEND_ITEMS      "正常|相加|屏幕|变亮|较浅颜色|相乘|变暗|较深颜色|叠加"
    #define L10N_PARAM_FILTER_OPACITY   "滤镜不透明度"
    #define L10N_PARAM_NOISE            "杂色"
    #define L10N_PARAM_ALPHA_ON         "关闭Alpha"
#else
    #define L10N_PLUGIN_NAME            "F's Filter"
    #define L10N_PLUGIN_DESC            "Filter Effect Filter"
    #define L10N_PARAM_ON               "on"
    #define L10N_PARAM_BASE_ENABLED     "BaseEnabled"
    #define L10N_PARAM_BASE_OPACITY     "BaseOpacity"
    #define L10N_PARAM_TOPIC            "Filter_"
    #define L10N_PARAM_ENABLED          "Enabled_"
    #define L10N_PARAM_EXTRACT          "Extract_"
    #define L10N_PARAM_EXTRACT_ITEMS    "None|Hi|Low"
    #define L10N_PARAM_BORDER_HI        "border_hi_"
    #define L10N_PARAM_SOFTNESS_HI      "softness_hi_"
    #define L10N_PARAM_BORDER_LO        "border_lo_"
    #define L10N_PARAM_SOFTNESS_LO      "softness_lo_"
    #define L10N_PARAM_BRIGHTNESS       "Brightness_"
    #define L10N_PARAM_MINMAX           "MinToMax_"
    #define L10N_PARAM_MAX              "Max_"
    #define L10N_PARAM_BLUR             "Blur_"
    #define L10N_PARAM_OPACITY          "Opacity_"
    #define L10N_PARAM_BLEND            "Blend_"
    #define L10N_PARAM_BLEND_ITEMS      "Normal|Add|Screen|Lighten|LighterColor|Multiply|Darken|DarkerColor|Overlay"
    #define L10N_PARAM_FILTER_OPACITY   "FilterOpacity"
    #define L10N_PARAM_NOISE            "Noise"
    #define L10N_PARAM_ALPHA_ON         "Alpha_ON"
#endif



