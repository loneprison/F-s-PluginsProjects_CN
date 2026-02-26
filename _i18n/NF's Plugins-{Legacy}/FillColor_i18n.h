#pragma once

/*
 * Localization switch for FillColor.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's FillColor"
    #define L10N_PLUGIN_DESC            "填充不透明区域"
    #define L10N_PARAM_EXECUTE          "激活"
    #define L10N_PARAM_ON               "开"
    #define L10N_PARAM_COLOR            "颜色"
    #define L10N_PARAM_OPACITY          "不透明度"
#else
    #define L10N_PLUGIN_NAME            "F's FillColor"
    #define L10N_PLUGIN_DESC            "不透明部分の塗りつぶし"
    #define L10N_PARAM_EXECUTE          "実行する"
    #define L10N_PARAM_ON               "ON"
    #define L10N_PARAM_COLOR            "色"
    #define L10N_PARAM_OPACITY          "不透明度"
#endif



