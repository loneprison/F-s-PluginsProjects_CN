#pragma once

/*
 * Localization switch for InnerFlareRot.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's InnerFlareRot"
    #define L10N_PLUGIN_DESC            "内阴影"
    #define L10N_PARAM_BLUR             "模糊度"
    #define L10N_PARAM_MAX              "大小"
    #define L10N_PARAM_HYPERBOLIC       "偏差"
    #define L10N_PARAM_ROT              "方向"
    #define L10N_PARAM_LENGTH           "长度"
    #define L10N_PARAM_OFFSET           "偏移"
    #define L10N_PARAM_COLOR            "颜色"
#else
    #define L10N_PLUGIN_NAME            "F's InnerFlareRot"
    #define L10N_PLUGIN_DESC            "InnerFlareRot"
    #define L10N_PARAM_BLUR             "blur"
    #define L10N_PARAM_MAX              "max"
    #define L10N_PARAM_HYPERBOLIC       "hyperbolic"
    #define L10N_PARAM_ROT              "rot"
    #define L10N_PARAM_LENGTH           "length"
    #define L10N_PARAM_OFFSET           "offset"
    #define L10N_PARAM_COLOR            "color"
#endif



