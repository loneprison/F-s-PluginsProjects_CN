#pragma once

/*
 * Localization switch for MaskFromRGB.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's MaskFromRGB"
    #define L10N_PLUGIN_DESC            "根据RGBA值创建遮罩"
    #define L10N_PARAM_MASK             "遮罩通道"
    #define L10N_PARAM_MASK_ITEMS       "红|绿|蓝|黄|洋红|青|最大值"
    #define L10N_PARAM_LEVEL            "强度"
#else
    #define L10N_PLUGIN_NAME            "F's MaskFromRGB"
    #define L10N_PLUGIN_DESC            "RGBAの値からマスク作成"
    #define L10N_PARAM_MASK             "Mask"
    #define L10N_PARAM_MASK_ITEMS       "Red|Green|Blue|Yellow|Magenta|Cyan|Max"
    #define L10N_PARAM_LEVEL            "Level"
#endif



