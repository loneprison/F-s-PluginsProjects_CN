#pragma once

/*
 * Localization switch for Premultiply.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's Premultiply"
    #define L10N_PLUGIN_DESC            "切换素材的Alpha遮罩方式为直接或预乘"
    #define L10N_PARAM_MODE             "模式"
    #define L10N_PARAM_MODE_ITEMS       "直接转预乘|预乘转直接"
    #define L10N_PARAM_MAT_COLOR        "预乘遮罩颜色"
#else
    #define L10N_PLUGIN_NAME            "F's Premultiply"
    #define L10N_PLUGIN_DESC            "ストレート合成　マット合成を切り替え"
    #define L10N_PARAM_MODE             "mode"
    #define L10N_PARAM_MODE_ITEMS       "マットからストレート|ストレートからマット"
    #define L10N_PARAM_MAT_COLOR        "マットカラー"
#endif



