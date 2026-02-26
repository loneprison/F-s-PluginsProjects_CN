#pragma once

/*
 * Localization switch for EdgeBlur.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

 
#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's EdgeBlur"
    #define L10N_PLUGIN_DESC            "模糊图像边缘"
    #define L10N_PARAM_BLUR             "模糊"
    #define L10N_PARAM_OFFSET           "偏移"
#else
    #define L10N_PLUGIN_NAME            "F's EdgeBlur"
    #define L10N_PLUGIN_DESC            "画像の縁をぼかします"
    #define L10N_PARAM_BLUR             "blur"
    #define L10N_PARAM_OFFSET           "offset"
#endif



