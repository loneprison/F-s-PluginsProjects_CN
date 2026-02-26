#pragma once

/*
 * Localization switch for NoiseHiLo_RGB.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's NoiseHiLo_RGB"
    #define L10N_PLUGIN_DESC            "按RGB通道亮/暗区域分别添加噪声的滤镜"
    #define L10N_PARAM_HIGH_POS         "高光范围"
    #define L10N_PARAM_LOW_POS          "阴影范围"
    #define L10N_PARAM_HIGH_LEVEL       "高光杂色数量"
    #define L10N_PARAM_MID_LEVEL        "中间调杂色数量"
    #define L10N_PARAM_LOW_LEVEL        "阴影杂色数量"
#else
    #define L10N_PLUGIN_NAME            "F's NoiseHiLo_RGB"
    #define L10N_PLUGIN_DESC            "RGBチャンネルの明るい・暗いところ別にノイズを加えるフィルタ"
    #define L10N_PARAM_HIGH_POS         "HightPos(%)"
    #define L10N_PARAM_LOW_POS          "LoPos(%)"
    #define L10N_PARAM_HIGH_LEVEL       "HighLevel(%)"
    #define L10N_PARAM_MID_LEVEL        "MidLevel(%)"
    #define L10N_PARAM_LOW_LEVEL        "LoLevel(%)"
#endif



