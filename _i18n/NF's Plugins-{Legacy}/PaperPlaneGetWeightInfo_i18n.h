#pragma once

/*
 * Localization switch for PaperPlaneGetWeightInfo.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's PaperPlaneGetWeightInfo"
    #define L10N_PLUGIN_DESC            "从加算后的权重图计算重心与重量并绘制结果"
    #define L10N_PARAM_DRAW_GRAPH       "绘制分布图"
    #define L10N_PARAM_GLUE             "胶水重量补偿"
#else
    #define L10N_PLUGIN_NAME            "F's PaperPlaneGetWeightInfo"
    #define L10N_PLUGIN_DESC            "加算合成後の重み画像から重心と重量を算出して描画"
    #define L10N_PARAM_DRAW_GRAPH       "分布グラフを描画"
    #define L10N_PARAM_GLUE             "のり重量補正"
#endif

