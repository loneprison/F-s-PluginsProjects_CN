#pragma once

/*
 * Localization switch for ColorChangeSimple.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

 
#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's ColorChangeSimple"
    #define L10N_PLUGIN_DESC            "单色替换"
    #define L10N_PARAM_LEVEL            "阈值"
    #define L10N_PARAM_SRC_COLOR        "原始颜色"
    #define L10N_PARAM_DST_COLOR        "替换颜色"
#else
    #define L10N_PLUGIN_NAME            "F's ColorChangeSimple"
    #define L10N_PLUGIN_DESC            "単色の色変えをします"
    #define L10N_PARAM_LEVEL            "許容値"
    #define L10N_PARAM_SRC_COLOR        "元の色"
    #define L10N_PARAM_DST_COLOR        "新しい色"
#endif



