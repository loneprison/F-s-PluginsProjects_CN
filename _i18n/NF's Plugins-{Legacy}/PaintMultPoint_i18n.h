#pragma once

/*
 * Localization switch for PaintMultPoint.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's PaintMultPoint"
    #define L10N_PLUGIN_DESC            "适用于二值图像的油漆桶填充工具（多点版）"
    #define L10N_PARAM_TOPIC_FMT        "方案_%d"
    #define L10N_PARAM_EXECUTE_FMT      "启用_%d"
    #define L10N_PARAM_ON               "开"
    #define L10N_PARAM_POS_FMT          "填充点_%d"
    #define L10N_PARAM_COLOR_FMT        "颜色_%d"
    #define L10N_PARAM_GUIDE_FMT        "显示参考线_%d"
    #define L10N_PARAM_GUIDE_ALL        "隐藏所有参考线"
    #define L10N_PARAM_GUIDE_ALL_OFF    "开"
#else
    #define L10N_PLUGIN_NAME            "F's PaintMultPoint"
    #define L10N_PLUGIN_DESC            "ペイント（俗に言うバケツツール）を改造"
    #define L10N_PARAM_TOPIC_FMT        "Point_%d"
    #define L10N_PARAM_EXECUTE_FMT      "塗りつぶす_%d"
    #define L10N_PARAM_ON               "ON"
    #define L10N_PARAM_POS_FMT          "位置_%d"
    #define L10N_PARAM_COLOR_FMT        "ペイント色_%d"
    #define L10N_PARAM_GUIDE_FMT        "ガイド表示_%d"
    #define L10N_PARAM_GUIDE_ALL        "ガイドをすべて非表示にする"
    #define L10N_PARAM_GUIDE_ALL_OFF    "非表示"
#endif



