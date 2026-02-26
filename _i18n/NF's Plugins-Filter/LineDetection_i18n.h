#pragma once

/*
 * Localization switch for LineDetection.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's LineDetection"
    #define L10N_PLUGIN_DESC            "检测并生成轮廓线"
    #define L10N_PARAM_ON               "开"
    #define L10N_PARAM_DELTA_CB         "按RGB变化检测"
    #define L10N_PARAM_DELTA_OPACITY    "RGB线条强度"
    #define L10N_PARAM_ALPHA_CB         "按Alpha变化检测"
    #define L10N_PARAM_ALPHA_OPACITY    "Alpha线条强度"
    #define L10N_PARAM_LINE_COLOR       "线条颜色"
#else
    #define L10N_PLUGIN_NAME            "F's LineDetection"
    #define L10N_PLUGIN_DESC            "輪郭線検出"
    #define L10N_PARAM_ON               "ON"
    #define L10N_PARAM_DELTA_CB         "RGB差分検出"
    #define L10N_PARAM_DELTA_OPACITY    "RGB差分検出の濃度"
    #define L10N_PARAM_ALPHA_CB         "Alpha差分検出"
    #define L10N_PARAM_ALPHA_OPACITY    "Alpha差分検出の濃度"
    #define L10N_PARAM_LINE_COLOR       "検出した線の色"
#endif



