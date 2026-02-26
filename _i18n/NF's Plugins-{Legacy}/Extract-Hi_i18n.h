#pragma once

/*
 * Localization switch for Extract-Hi.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's Extract-Hi"
    #define L10N_PLUGIN_DESC            "提取高亮区域（与标准算法不同）"
    #define L10N_PARAM_BORDER           "阈值"
    #define L10N_PARAM_SOFTNESS         "柔和度"
    #define L10N_PARAM_TARGET           "通道"
    #define L10N_PARAM_TARGET_ITEMS     "亮度|红色|绿色|蓝色|青色|洋红|黄色|RGB最大值|自定义"
    #define L10N_PARAM_CUSTOM_COLOR     "自定义颜色"
    #define L10N_PARAM_INVERT           "反转"
    #define L10N_PARAM_ON               "开"
#else
    #define L10N_PLUGIN_NAME            "F's Extract-Hi"
    #define L10N_PLUGIN_DESC            "明るいところを抽出するフィルタ（標準のものアルゴリズムが違う）"
    #define L10N_PARAM_BORDER           "Border"
    #define L10N_PARAM_SOFTNESS         "Softness"
    #define L10N_PARAM_TARGET           "Target"
    #define L10N_PARAM_TARGET_ITEMS     "Luminance|Red|Green|Blue|Cyan|Magenta|Yellow|RGB_Max|Custum"
    #define L10N_PARAM_CUSTOM_COLOR     "CustumColor"
    #define L10N_PARAM_INVERT           "Invert"
    #define L10N_PARAM_ON               "on"
#endif



