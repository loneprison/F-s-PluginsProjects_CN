#pragma once

/*
 * Localization switch for sputteringCircle.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's sputteringCircle"
    #define L10N_PLUGIN_DESC            "从指定点喷溅圆形像素点"
    #define L10N_PARAM_SEED                 "随机种子"
    #define L10N_PARAM_VALUE                "数量(%)"
    #define L10N_PARAM_OPACITY_RAND         "不透明度"
    #define L10N_PARAM_POSITION             "位置"
    #define L10N_PARAM_RADIUS               "半径"
    #define L10N_PARAM_ASPECT               "长宽比"
    #define L10N_PARAM_LENGTH_SCALE         "锚点缩放"
    #define L10N_PARAM_ANCHOR_ENABLED       "启用单独锚点"
    #define L10N_PARAM_ANCHOR               "锚点"
    #define L10N_PARAM_POINT_VALUE          "点数量"
    #define L10N_PARAM_POINT_LENGTH         "点间距"
    #define L10N_PARAM_POINT_LEN_SYNC       "点间距同步"
    #define L10N_PARAM_ON                   "开"
    #define L10N_PARAM_SIZE                 "尺寸"
    #define L10N_PARAM_SIZE_ITEMS           "极小|小|中|大|特大"
    #define L10N_PARAM_COLOR1               "颜色1"
    #define L10N_PARAM_EXTRA_COLORS         "其他颜色"
    #define L10N_PARAM_COLOR_MAX            "颜色数量"
    #define L10N_PARAM_COLOR2               "颜色2"
    #define L10N_PARAM_COLOR3               "颜色3"
    #define L10N_PARAM_COLOR4               "颜色4"
    #define L10N_PARAM_BLEND_WITH_ORIGINAL  "与原始图像混合"
#else
    #define L10N_PLUGIN_NAME            "F's sputteringCircle"
    #define L10N_PLUGIN_DESC            "指定した点から円形にスパッタリング"
    #define L10N_PARAM_SEED                 "seed"
    #define L10N_PARAM_VALUE                "value"
    #define L10N_PARAM_OPACITY_RAND         "opacity_rand"
    #define L10N_PARAM_POSITION             "Position"
    #define L10N_PARAM_RADIUS               "Radius"
    #define L10N_PARAM_ASPECT               "Aspect"
    #define L10N_PARAM_LENGTH_SCALE         "Length_Scale"
    #define L10N_PARAM_ANCHOR_ENABLED       "Anchor_Enabled"
    #define L10N_PARAM_ANCHOR               "Anchor"
    #define L10N_PARAM_POINT_VALUE          "PointValue"
    #define L10N_PARAM_POINT_LENGTH         "PointLength"
    #define L10N_PARAM_POINT_LEN_SYNC       "Point_length_sysnc"
    #define L10N_PARAM_ON                   "ON"
    #define L10N_PARAM_SIZE                 "size"
    #define L10N_PARAM_SIZE_ITEMS           "極小|小|中|大|特大"
    #define L10N_PARAM_COLOR1               "Color1"
    #define L10N_PARAM_EXTRA_COLORS         "ExtraColors"
    #define L10N_PARAM_COLOR_MAX            "ColorMax"
    #define L10N_PARAM_COLOR2               "Color2"
    #define L10N_PARAM_COLOR3               "Color3"
    #define L10N_PARAM_COLOR4               "Color4"
    #define L10N_PARAM_BLEND_WITH_ORIGINAL  "Blend with original"
#endif



