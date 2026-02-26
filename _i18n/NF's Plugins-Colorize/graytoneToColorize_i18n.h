#pragma once

/*
 * Localization switch for graytoneToColorize.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's graytoneToColorize"
    #define L10N_PLUGIN_DESC            "给素材快速上色2"
    #define L10N_PARAM_TARGET           "通道"
    #define L10N_PARAM_TARGET_ITEMS     "亮度|红|绿|蓝|Alpha"
    #define L10N_PARAM_COLOR0           "颜色0"
    #define L10N_PARAM_COLOR1           "颜色1"
    #define L10N_PARAM_COLOR2           "颜色2"
    #define L10N_PARAM_COLOR3           "颜色3"
    #define L10N_PARAM_COLOR4           "颜色4"
    #define L10N_PARAM_COLOR5           "颜色5"
    #define L10N_PARAM_COLOR6           "颜色6"
    #define L10N_PARAM_COLOR7           "颜色7"
    #define L10N_PARAM_COLOR8           "颜色8"
    #define L10N_PARAM_OFFSET           "偏移"
    #define L10N_PARAM_OFFSET_ENABLED   "启用偏移"
    #define L10N_PARAM_ON               "开"
    #define L10N_PARAM_OFFSET_SPEED     "偏移速度"
    #define L10N_PARAM_REPEAT           "重复"
#else
    #define L10N_PLUGIN_NAME            "F's graytoneToColorize"
    #define L10N_PLUGIN_DESC            "適当な素材を適当に色を付ける2"
    #define L10N_PARAM_TARGET           "target"
    #define L10N_PARAM_TARGET_ITEMS     "brightness|red|green|blue|alpha"
    #define L10N_PARAM_COLOR0           "color0"
    #define L10N_PARAM_COLOR1           "color1"
    #define L10N_PARAM_COLOR2           "color2"
    #define L10N_PARAM_COLOR3           "color3"
    #define L10N_PARAM_COLOR4           "color4"
    #define L10N_PARAM_COLOR5           "color5"
    #define L10N_PARAM_COLOR6           "color6"
    #define L10N_PARAM_COLOR7           "color7"
    #define L10N_PARAM_COLOR8           "color8"
    #define L10N_PARAM_OFFSET           "offset"
    #define L10N_PARAM_OFFSET_ENABLED   "offset_enabled"
    #define L10N_PARAM_ON               "on"
    #define L10N_PARAM_OFFSET_SPEED     "offset_speed"
    #define L10N_PARAM_REPEAT           "repeat"
#endif


