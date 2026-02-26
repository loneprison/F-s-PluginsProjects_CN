#pragma once

/*
 * Localization switch for CCplus.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */


#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's CCplus"
    #define L10N_PLUGIN_DESC            "按亮度着色"
    #define L10N_ORG_REV_LABEL          "反转原始亮度"
    #define L10N_ORG_REV_ON             "开"
    #define L10N_COLOR_START            "高光"
    #define L10N_COLOR_CENTER           "中间调"
    #define L10N_COLOR_END              "阴影"
    #define L10N_COLOR_CENTER_POS       "中间调位置"
    #define L10N_ALPHA_START            "高光不透明度"
    #define L10N_ALPHA_END              "阴影不透明度"
    #define L10N_NOISE_VALUE            "杂色数量"
#else
    #define L10N_PLUGIN_NAME            "F's CCplus"
    #define L10N_PLUGIN_DESC            "明るさにあわせて色を付けます"
    #define L10N_ORG_REV_LABEL          "original_reverce"
    #define L10N_ORG_REV_ON             "on"
    #define L10N_COLOR_START            "start_color"
    #define L10N_COLOR_CENTER           "center_color"
    #define L10N_COLOR_END              "end_color"
    #define L10N_COLOR_CENTER_POS       "center_color_pos(%)"
    #define L10N_ALPHA_START            "start_alpha(%)"
    #define L10N_ALPHA_END              "end_alpha(%)"
    #define L10N_NOISE_VALUE            "noise_value"
#endif



