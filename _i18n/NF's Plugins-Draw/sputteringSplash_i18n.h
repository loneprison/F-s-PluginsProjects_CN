#pragma once

/*
 * Localization switch for sputteringSplash.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's sputteringSplash"
    #define L10N_PLUGIN_DESC            "沿Alpha边界指定方向喷溅"
    #define L10N_PARAM_SEED                 "随机种子"
    #define L10N_PARAM_VALUE                "数量(%)"
    #define L10N_PARAM_DIRECTION            "方向"
    #define L10N_PARAM_DIRECTION_ITEMS      "↑上(0)|↗右上(45)|→右(90)|↘右下(135)|↓下(180)|↙左下(235)|←左(270)|↖左上(315)"
    #define L10N_PARAM_OPACITY_RAND         "不透明度"
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
    #define L10N_PLUGIN_NAME            "F's sputteringSplash"
    #define L10N_PLUGIN_DESC            "アルファー境界の指定した方向にスパッタリング"
    #define L10N_PARAM_SEED                 "seed"
    #define L10N_PARAM_VALUE                "value(%)"
    #define L10N_PARAM_DIRECTION            "direction"
    #define L10N_PARAM_DIRECTION_ITEMS      "上(0)|右上(45)|右(90)|右下(135)|下(180)|左下(235)|左(270)|左上(315)"
    #define L10N_PARAM_OPACITY_RAND         "opacity_rand"
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



