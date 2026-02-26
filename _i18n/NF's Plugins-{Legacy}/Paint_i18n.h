#pragma once

/*
 * Localization switch for Paint.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's Paint"
    #define L10N_PLUGIN_DESC            "适用于二值图像的油漆桶填充工具"
    #define L10N_PARAM_EXECUTE          "启用填充"
    #define L10N_PARAM_ON               "开"
    #define L10N_PARAM_POSITION         "填充点"
    #define L10N_PARAM_PAINT_COLOR      "颜色"
    #define L10N_PARAM_OPACITY          "不透明度"
    #define L10N_ERR_GET_PARAMS         "参数错误，抱歉。"
#else
    #define L10N_PLUGIN_NAME            "F's Paint"
    #define L10N_PLUGIN_DESC            "ペイント（俗に言うバケツツール）"
    #define L10N_PARAM_EXECUTE          "塗りつぶす"
    #define L10N_PARAM_ON               "ON"
    #define L10N_PARAM_POSITION         "位置"
    #define L10N_PARAM_PAINT_COLOR      "ペイント色"
    #define L10N_PARAM_OPACITY          "不透明度(%)"
    #define L10N_ERR_GET_PARAMS         "パラメータエラーです。御免なさい。"
#endif



