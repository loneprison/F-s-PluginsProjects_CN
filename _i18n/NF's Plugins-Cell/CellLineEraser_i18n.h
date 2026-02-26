#pragma once

/*
 * Localization switch for CellLineEraser.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's CellLineEraser"
    #define L10N_PLUGIN_DESC            "去除二值图像主线"
    #define L10N_PARAM_TARGET_COUNT     "目标颜色数量"
    #define L10N_PARAM_COLOR1           "颜色1"
    #define L10N_PARAM_COLOR2           "颜色2"
    #define L10N_PARAM_COLOR3           "颜色3"
    #define L10N_PARAM_COLOR4           "颜色4"
    #define L10N_PARAM_COLOR5           "颜色5"
    #define L10N_PARAM_COLOR6           "颜色6"
    #define L10N_PARAM_COLOR7           "颜色7"
    #define L10N_PARAM_COLOR8           "颜色8"
    #define L10N_PARAM_COLOR9           "颜色9"
    #define L10N_PARAM_COLOR10          "颜色10"
    #define L10N_PARAM_KEEP_PIXELS      "保留未清除像素"
    #define L10N_PARAM_FILL_UNKNOWN     "填充未清除像素"
    #define L10N_PARAM_FILL_COLOR       "填充颜色"
    #define L10N_PARAM_WHITE_TRANS      "白色转透明"
#else
    #define L10N_PLUGIN_NAME            "F's CellLineEraser"
    #define L10N_PLUGIN_DESC            "セル画の主線を無くします"
    #define L10N_PARAM_TARGET_COUNT     "TargetColorCount"
    #define L10N_PARAM_COLOR1           "color1"
    #define L10N_PARAM_COLOR2           "color2"
    #define L10N_PARAM_COLOR3           "color3"
    #define L10N_PARAM_COLOR4           "color4"
    #define L10N_PARAM_COLOR5           "color5"
    #define L10N_PARAM_COLOR6           "color6"
    #define L10N_PARAM_COLOR7           "color7"
    #define L10N_PARAM_COLOR8           "color8"
    #define L10N_PARAM_COLOR9           "color9"
    #define L10N_PARAM_COLOR10          "color10"
    #define L10N_PARAM_KEEP_PIXELS      "KeepPixels"
    #define L10N_PARAM_FILL_UNKNOWN     "Fill unremoved pixels"
    #define L10N_PARAM_FILL_COLOR       "FillColor"
    #define L10N_PARAM_WHITE_TRANS      "Make White Transparent"
#endif



