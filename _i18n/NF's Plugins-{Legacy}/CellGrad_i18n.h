#pragma once

/*
 * Localization switch for CellGrad.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */


#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's CellGrad"
    #define L10N_PLUGIN_DESC            "用于二值图像区域的渐变"
    #define L10N_PARAM_TARGET_TOPIC     "方案"
    #define L10N_PARAM_TARGET_LEVEL     "阈值"
    #define L10N_PARAM_TARGET_COUNT     "方案数量"
    #define L10N_PARAM_TARGET_COL1      "颜色1"
    #define L10N_PARAM_TARGET_COL2      "颜色2"
    #define L10N_PARAM_TARGET_COL3      "颜色3"
    #define L10N_PARAM_TARGET_COL4      "颜色4"
    #define L10N_PARAM_TARGET_COL5      "颜色5"
    #define L10N_PARAM_TARGET_COL6      "颜色6"
    #define L10N_PARAM_TARGET_COL7      "颜色7"
    #define L10N_PARAM_TARGET_COL8      "颜色8"
    #define L10N_PARAM_ANGLE            "角度"
    #define L10N_PARAM_START_OVER       "起点偏移"
    #define L10N_PARAM_LAST_OVER        "终点偏移"
    #define L10N_PARAM_START_COL        "起始颜色"
    #define L10N_PARAM_LAST_COL         "结束颜色"
    #define L10N_PARAM_GUIDE_SHOW       "显示参考线"
    #define L10N_PARAM_GUIDE_COLOR      "参考线颜色"
    #define L10N_PARAM_ON               "开"
#else
    #define L10N_PLUGIN_NAME            "F's CellGrad"
    #define L10N_PLUGIN_DESC            "セルにかけるグラデ"
    #define L10N_PARAM_TARGET_TOPIC     "target"
    #define L10N_PARAM_TARGET_LEVEL     "targetLevel"
    #define L10N_PARAM_TARGET_COUNT     "targetCount"
    #define L10N_PARAM_TARGET_COL1      "color1"
    #define L10N_PARAM_TARGET_COL2      "color2"
    #define L10N_PARAM_TARGET_COL3      "color3"
    #define L10N_PARAM_TARGET_COL4      "color4"
    #define L10N_PARAM_TARGET_COL5      "color5"
    #define L10N_PARAM_TARGET_COL6      "color6"
    #define L10N_PARAM_TARGET_COL7      "color7"
    #define L10N_PARAM_TARGET_COL8      "color8"
    #define L10N_PARAM_ANGLE            "angle"
    #define L10N_PARAM_START_OVER       "startOver"
    #define L10N_PARAM_LAST_OVER        "lastOver"
    #define L10N_PARAM_START_COL        "startCol"
    #define L10N_PARAM_LAST_COL         "lastCol"
    #define L10N_PARAM_GUIDE_SHOW       "showGuide"
    #define L10N_PARAM_GUIDE_COLOR      "showGuide"
    #define L10N_PARAM_ON               "on"
#endif



