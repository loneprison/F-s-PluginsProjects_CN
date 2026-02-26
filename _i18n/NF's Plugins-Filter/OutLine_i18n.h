#pragma once

/*
 * Localization switch for OutLine.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's OutLine"
    #define L10N_PLUGIN_DESC            "绘制描边"
    #define L10N_PARAM_VALUE            "大小"
    #define L10N_PARAM_COLOR            "颜色"
    #define L10N_PARAM_LEVEL            "不透明度"
#else
    #define L10N_PLUGIN_NAME            "F's OutLine"
    #define L10N_PLUGIN_DESC            "アウトラインの描画"
    #define L10N_PARAM_VALUE            "Value"
    #define L10N_PARAM_COLOR            "Color"
    #define L10N_PARAM_LEVEL            "Level(%)"
#endif



