#pragma once

/*
 * Localization switch for EdgeLine-Hi.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

 
#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's EdgeLine-Hi"
    #define L10N_PLUGIN_DESC            "按照指定方向绘制边缘线"
    #define L10N_PARAM_TARGET_COLOR     "目标颜色"
    #define L10N_PARAM_SAMPLE_COLOR     "相邻颜色"
    #define L10N_PARAM_LENGTH           "大小"
    #define L10N_PARAM_ROT              "角度"
    #define L10N_PARAM_LEVEL            "阈值"
    #define L10N_PARAM_DRAW_COLOR       "描边颜色"
    #define L10N_PARAM_SCAN_FLAG        "仅在连续像素区域生成"
    #define L10N_PARAM_SCAN_FLAG2       "开"
#else
    #define L10N_PLUGIN_NAME            "F's EdgeLine-Hi"
    #define L10N_PLUGIN_DESC            "境界線を指定方向のみ描きます"
    #define L10N_PARAM_TARGET_COLOR     "TargetColor"
    #define L10N_PARAM_SAMPLE_COLOR     "SampleColor"
    #define L10N_PARAM_LENGTH           "Length(px)"
    #define L10N_PARAM_ROT              "Rot"
    #define L10N_PARAM_LEVEL            "Level(%)"
    #define L10N_PARAM_DRAW_COLOR       "frame rander"
    #define L10N_PARAM_SCAN_FLAG        "scanFlag"
    #define L10N_PARAM_SCAN_FLAG2       "GiveUpSoon"
#endif



