#pragma once

/*
 * Localization switch for MaskFromRGB_Multi.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's MaskFromRGB_Multi"
    #define L10N_PLUGIN_DESC            "根据RGBA值创建遮罩"
    #define L10N_PARAM_LEVEL            "强度"
    #define L10N_PARAM_RED              "红"
    #define L10N_PARAM_GREEN            "绿"
    #define L10N_PARAM_BLUE             "蓝"
    #define L10N_PARAM_YELLOW           "黄"
    #define L10N_PARAM_MAGENTA          "洋红"
    #define L10N_PARAM_CYAN             "青"
    #define L10N_PARAM_ON               "开"
#else
    #define L10N_PLUGIN_NAME            "F's MaskFromRGB_Multi"
    #define L10N_PLUGIN_DESC            "RGBAの値からマスク作成"
    #define L10N_PARAM_LEVEL            "Level"
    #define L10N_PARAM_RED              "Red"
    #define L10N_PARAM_GREEN            "Green"
    #define L10N_PARAM_BLUE             "Blue"
    #define L10N_PARAM_YELLOW           "Yellow"
    #define L10N_PARAM_MAGENTA          "Magenta"
    #define L10N_PARAM_CYAN             "Cyan"
    #define L10N_PARAM_ON               "on"
#endif



