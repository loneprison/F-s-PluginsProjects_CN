#pragma once

/*
 * Localization switch for PaperPlaneGetWeight.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's PaperPlaneGetWeight"
    #define L10N_PLUGIN_DESC            "用于纸飞机重心计算的权重编码填色（纸制手工模型用）"
    #define L10N_PARAM_HALF_SIZE        "半尺寸"
    #define L10N_PARAM_COUNT            "层数"
    #define L10N_PARAM_WEIGHT           "纸张克重(g/m2)"
    #define L10N_PARAM_WEIGHT_ITEMS     "180|225|310|360"
    #define L10N_PARAM_ON                  "开"
#else
    #define L10N_PLUGIN_NAME            "F's PaperPlaneGetWeight"
    #define L10N_PLUGIN_DESC            "紙飛行機の重心計算用の重みエンコード塗りつぶし"
    #define L10N_PARAM_HALF_SIZE        "ハーフサイズ"
    #define L10N_PARAM_COUNT            "枚数"
    #define L10N_PARAM_WEIGHT           "紙の坪量(g/m2)"
    #define L10N_PARAM_WEIGHT_ITEMS     "180|225|310|360"
    #define L10N_PARAM_ON                  "on"
#endif


