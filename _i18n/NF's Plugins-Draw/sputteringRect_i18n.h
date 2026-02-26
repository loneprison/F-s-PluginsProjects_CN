#pragma once

/*
 * Localization switch for sputteringRect.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's sputteringRect"
    #define L10N_PLUGIN_DESC            "在矩形范围内喷溅"
    #define L10N_PARAM_SEED                 "随机种子"
    #define L10N_PARAM_VALUE                "强度"
    #define L10N_PARAM_OPACITY_RAND         "不透明度"
    #define L10N_PARAM_TOP_LEFT             "左上"
    #define L10N_PARAM_BOTTOM_RIGHT         "右下"
    #define L10N_PARAM_POINT_VALUE          "点数量"
    #define L10N_PARAM_POINT_LENGTH         "点间距"
    #define L10N_PARAM_SIZE                 "尺寸"
    #define L10N_PARAM_SIZE_ITEMS           "极小|小|中|大|特大"
    #define L10N_PARAM_COLOR1               "颜色1"
    #define L10N_PARAM_EXTRA_COLORS         "其他颜色"
    #define L10N_PARAM_COLOR_MAX            "颜色数量"
    #define L10N_PARAM_COLOR2               "颜色2"
    #define L10N_PARAM_COLOR3               "颜色3"
    #define L10N_PARAM_COLOR4               "颜色4"
    #define L10N_PARAM_BLEND_WITH_ORIGINAL  "与原始图像混合"
    #define L10N_PARAM_ON                   "开"
#else
    #define L10N_PLUGIN_NAME            "F's sputteringRect"
    #define L10N_PLUGIN_DESC            "矩形範囲にスパッタリング"
    #define L10N_PARAM_SEED                 "seed"
    #define L10N_PARAM_VALUE                "value"
    #define L10N_PARAM_OPACITY_RAND         "opacity_rand"
    #define L10N_PARAM_TOP_LEFT             "TopLeft"
    #define L10N_PARAM_BOTTOM_RIGHT         "BottomRight"
    #define L10N_PARAM_POINT_VALUE          "PointValue"
    #define L10N_PARAM_POINT_LENGTH         "PointLength"
    #define L10N_PARAM_SIZE                 "size"
    #define L10N_PARAM_SIZE_ITEMS           "極小|小|中|大|特大"
    #define L10N_PARAM_COLOR1               "Color1"
    #define L10N_PARAM_EXTRA_COLORS         "ExtraColors"
    #define L10N_PARAM_COLOR_MAX            "ColorMax"
    #define L10N_PARAM_COLOR2               "Color2"
    #define L10N_PARAM_COLOR3               "Color3"
    #define L10N_PARAM_COLOR4               "Color4"
    #define L10N_PARAM_BLEND_WITH_ORIGINAL  "Blend with original"
    #define L10N_PARAM_ON                   "ON"
#endif



