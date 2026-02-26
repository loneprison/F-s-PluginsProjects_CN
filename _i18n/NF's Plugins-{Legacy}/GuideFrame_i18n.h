#pragma once

/*
 * Localization switch for GuideFrame.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's GuideFrame"
    #define L10N_PLUGIN_DESC            "范围指定"
    #define L10N_PARAM_COLOR            "颜色"
    #define L10N_PARAM_TOP_LEFT         "左上"
    #define L10N_PARAM_BOTTOM_RIGHT     "右下"
    #define L10N_PARAM_CHECK            "检查"
    #define L10N_PARAM_ON               "开"
    #define L10N_PARAM_SMOOTH           "平滑"
#else
    #define L10N_PLUGIN_NAME            "F's GuideFrame"
    #define L10N_PLUGIN_DESC            "範囲指定"
    #define L10N_PARAM_COLOR            "color"
    #define L10N_PARAM_TOP_LEFT         "TopLeft"
    #define L10N_PARAM_BOTTOM_RIGHT     "BottomRight"
    #define L10N_PARAM_CHECK            "Check"
    #define L10N_PARAM_ON               "on"
    #define L10N_PARAM_SMOOTH           "Smooth"
#endif



