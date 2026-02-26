#pragma once

/*
 * Localization switch for ToGray.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's ToGray"
    #define L10N_PLUGIN_DESC            "多种不同方法的灰度化"
    #define L10N_PARAM_MODE             "模式"
    #define L10N_PARAM_MODE_ITEMS       "(Y)uv|h(L)s|(R+G+B)/3|(R)gb|r(G)b|rg(B)|RGB最大|(L)ab"
    #define L10N_PARAM_BLEND_ORIGINAL   "与原始图像混合"
#else
    #define L10N_PLUGIN_NAME            "F's ToGray"
    #define L10N_PLUGIN_DESC            "色々な方法でグレー化します"
    #define L10N_PARAM_MODE             "mode"
    #define L10N_PARAM_MODE_ITEMS       "(Y)uv|h(L)s|(R+G+B)/3|(R)gb|r(G)b|rg(B)|RGBMax|(L)ab"
    #define L10N_PARAM_BLEND_ORIGINAL   "blend original(%)"
#endif



