#pragma once

/*
 * Localization switch for EdgeLine.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's EdgeLine"
    #define L10N_PLUGIN_DESC            "绘制边缘线条"
    #define L10N_PARAM_TARGET_COLOR     "目标颜色"
    #define L10N_PARAM_SAMPLE_COLOR     "相邻颜色"
    #define L10N_PARAM_LEVEL            "阈值"
    #define L10N_PARAM_LENGTH           "大小"
    #define L10N_PARAM_DRAW_COLOR       "描边颜色"
#else
    #define L10N_PLUGIN_NAME            "F's EdgeLine"
    #define L10N_PLUGIN_DESC            "境界線を描く"
    #define L10N_PARAM_TARGET_COLOR     "TargetColor"
    #define L10N_PARAM_SAMPLE_COLOR     "SampleColor"
    #define L10N_PARAM_LEVEL            "level(%)"
    #define L10N_PARAM_LENGTH           "length(px)"
    #define L10N_PARAM_DRAW_COLOR       "DrawColor"
#endif


