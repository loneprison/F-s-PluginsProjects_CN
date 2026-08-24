#pragma once

/*
 * Localization switch for TargetGradRadical.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's TargetGradRadical"
    #define L10N_PLUGIN_DESC            "在指定目标上生成径向渐变色"
    #define L10N_PARAM_TARGET_MODE      "模式"
    #define L10N_PARAM_TARGET_FORMAT    "颜色%d"
    #define L10N_PARAM_TARGET_ITEMS     "指定目标颜色|仅Alpha|全部"
    #define L10N_PARAM_TARGET_COLORS    "目标颜色"
    #define L10N_PARAM_TARGET_ENABLED   "目标方案"
    #define L10N_PARAM_ON               "开"
    #define L10N_PARAM_GRAD_COLOR       "渐变颜色"
    #define L10N_PARAM_INVERT           "反转"
    #define L10N_PARAM_CENTER           "中心"
    #define L10N_PARAM_RADIUS           "半径"
    #define L10N_PARAM_HYPERBOLIC       "偏差"
    #define L10N_PARAM_ASPECT           "宽高比"
    #define L10N_PARAM_ANGLE            "角度"
    #define L10N_PARAM_FEATHER          "羽化"
    #define L10N_PARAM_COLOR_TABLE      "颜色表"
    #define L10N_PARAM_LOAD             "加载"
    #define L10N_PARAM_SAVE             "保存"
#else
    #define L10N_PLUGIN_NAME            "F's TargetGradRadical"
    #define L10N_PLUGIN_DESC            "TargetGradRadical"
    #define L10N_PARAM_TARGET_MODE      "target"
    #define L10N_PARAM_TARGET_FORMAT    "target%d"
    #define L10N_PARAM_TARGET_ITEMS     "targetColors|alphaOn|all"
    #define L10N_PARAM_TARGET_COLORS    "targetColors"
    #define L10N_PARAM_TARGET_ENABLED   "targetEnabled"
    #define L10N_PARAM_ON               "on"
    #define L10N_PARAM_GRAD_COLOR       "gradColor"
    #define L10N_PARAM_INVERT           "invert"
    #define L10N_PARAM_CENTER           "center"
    #define L10N_PARAM_RADIUS           "radius"
    #define L10N_PARAM_HYPERBOLIC       "hyperbolic"
    #define L10N_PARAM_ASPECT           "aspect"
    #define L10N_PARAM_ANGLE            "angle"
    #define L10N_PARAM_FEATHER          "feather"
    #define L10N_PARAM_COLOR_TABLE      "colorTable"
    #define L10N_PARAM_LOAD             "load"
    #define L10N_PARAM_SAVE             "save"
#endif


