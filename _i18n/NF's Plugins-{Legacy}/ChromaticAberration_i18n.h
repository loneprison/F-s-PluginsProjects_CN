#pragma once

/*
 * Localization switch for ChromaticAberration.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */


#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's ChromaticAberration"
    #define L10N_PLUGIN_DESC            "色差"
    #define L10N_PARAM_RED              "红色"
    #define L10N_PARAM_GREEN            "绿色"
    #define L10N_PARAM_BLUE             "蓝色"
    #define L10N_PARAM_CENTER           "中心点"
#else
    #define L10N_PLUGIN_NAME            "F's ChromaticAberration"
    #define L10N_PLUGIN_DESC            "ChromaticAberration"
    #define L10N_PARAM_RED              "red"
    #define L10N_PARAM_GREEN            "green"
    #define L10N_PARAM_BLUE             "blue"
    #define L10N_PARAM_CENTER           "center"
#endif



