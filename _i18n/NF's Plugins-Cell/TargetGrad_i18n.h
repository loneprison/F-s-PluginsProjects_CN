#pragma once

/*
 * Localization switch for TargetGrad.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's TargetGrad"
    #define L10N_PLUGIN_DESC            "在指定目标上生成渐变色"
    #define L10N_PARAM_TARGET_MODE      "模式"
    #define L10N_PARAM_TARGET_FORMAT    "颜色%d"
    #define L10N_PARAM_TARGET_ITEMS     "指定目标颜色|仅Alpha|全部"
    #define L10N_PARAM_TARGET_COLORS    "目标颜色"
    #define L10N_PARAM_TARGET_ENABLED   "方案"
    #define L10N_PARAM_ON               "开"
    #define L10N_PARAM_GRAD_COLOR       "渐变颜色"
    #define L10N_PARAM_SWAP_POINT       "交换颜色"
    #define L10N_PARAM_HYPERBOLIC       "偏差"
    #define L10N_PARAM_AUTO_POS         "自适应位置"
    #define L10N_PARAM_TWO_POINT        "渐变端点"
    #define L10N_PARAM_START            "渐变起点"
    #define L10N_PARAM_LAST             "渐变终点"
    #define L10N_PARAM_ROT              "旋转"
    #define L10N_PARAM_START_PERCENT    "起点百分比"
    #define L10N_PARAM_LAST_PERCENT     "终点百分比"
    #define L10N_PARAM_OFFSET_X         "X 偏移"
    #define L10N_PARAM_OFFSET_Y         "Y 偏移"
    #define L10N_PARAM_COLOR_TABLE      "颜色表"
    #define L10N_PARAM_LOAD             "加载"
    #define L10N_PARAM_SAVE             "保存"
    #define L10N_PARAM_GUIDE_DRAW       "绘制参考线"
    #define L10N_PARAM_GUIDE_COLOR      "参考线颜色"
#else
    #define L10N_PLUGIN_NAME            "F's TargetGrad"
    #define L10N_PLUGIN_DESC            "TargetGrad"
    #define L10N_PARAM_TARGET_MODE      "target"
    #define L10N_PARAM_TARGET_FORMAT    "target%d"
    #define L10N_PARAM_TARGET_ITEMS     "targetColors|alphaOn|all"
    #define L10N_PARAM_TARGET_COLORS    "targetColors"
    #define L10N_PARAM_TARGET_ENABLED   "targetEnabled"
    #define L10N_PARAM_ON               "on"
    #define L10N_PARAM_GRAD_COLOR       "gradColor"
    #define L10N_PARAM_SWAP_POINT       "swapPoint"
    #define L10N_PARAM_HYPERBOLIC       "hyperbolic"
    #define L10N_PARAM_AUTO_POS         "autoPos"
    #define L10N_PARAM_TWO_POINT        "2Point"
    #define L10N_PARAM_START            "start"
    #define L10N_PARAM_LAST             "last"
    #define L10N_PARAM_ROT              "rot"
    #define L10N_PARAM_START_PERCENT    "startPercent"
    #define L10N_PARAM_LAST_PERCENT     "lastPercent"
    #define L10N_PARAM_OFFSET_X         "offsetX"
    #define L10N_PARAM_OFFSET_Y         "offsetY"
    #define L10N_PARAM_COLOR_TABLE      "colorTable"
    #define L10N_PARAM_LOAD             "load"
    #define L10N_PARAM_SAVE             "save"
    #define L10N_PARAM_GUIDE_DRAW       "guideDraw"
    #define L10N_PARAM_GUIDE_COLOR      "guideColor"
#endif


