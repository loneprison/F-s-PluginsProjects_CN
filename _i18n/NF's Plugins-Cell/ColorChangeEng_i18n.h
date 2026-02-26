#pragma once

/*
 * Localization switch for ColorChangeEng.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

// 不汉化
#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's ColorChangeEng"
    #define L10N_PLUGIN_DESC            "将目标颜色替换为另一种颜色"
    #define L10N_PARAM_LEVEL            "Tolerance"
    #define L10N_PARAM_MODE             "Mode"
    #define L10N_PARAM_EXEC             "Execute"
    #define L10N_PARAM_TARGET0          "Target"
    #define L10N_PARAM_SRCCOL0          "SourceColor"
    #define L10N_PARAM_DSTCOL0          "DestColor"
#else
    #define L10N_PLUGIN_NAME            "F's ColorChangeEng"
    #define L10N_PLUGIN_DESC            "Replace target colors with another."
    #define L10N_PARAM_LEVEL            "Tolerance"
    #define L10N_PARAM_MODE             "Mode"
    #define L10N_PARAM_EXEC             "Execute"
    #define L10N_PARAM_TARGET0          "Target"
    #define L10N_PARAM_SRCCOL0          "SourceColor"
    #define L10N_PARAM_DSTCOL0          "DestColor"
#endif



