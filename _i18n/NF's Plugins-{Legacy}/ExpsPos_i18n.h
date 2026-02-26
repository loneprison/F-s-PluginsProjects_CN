#pragma once

/*
 * Localization switch for ExpsPos.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

 
#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's ExpsPos"
    #define L10N_PLUGIN_DESC            "表达式位置控制"
    #define L10N_PARAM_ON               "启用"
    #define L10N_PARAM_ON_VALUE         "开"
    #define L10N_PARAM_POS0             "位置0"
    #define L10N_PARAM_POS1             "位置1"
    #define L10N_PARAM_POS2             "位置2"
    #define L10N_PARAM_POS3             "位置3"
    #define L10N_PARAM_POS4             "位置4"
    #define L10N_PARAM_POS5             "位置5"
    #define L10N_PARAM_POS6             "位置6"
    #define L10N_PARAM_POS7             "位置7"
    #define L10N_PARAM_POS8             "位置8"
    #define L10N_PARAM_POS9             "位置9"
#else
    #define L10N_PLUGIN_NAME            "F's ExpsPos"
    #define L10N_PLUGIN_DESC            "式用位置制御"
    #define L10N_PARAM_ON               "ON"
    #define L10N_PARAM_ON_VALUE         "on"
    #define L10N_PARAM_POS0             "pos0"
    #define L10N_PARAM_POS1             "pos1"
    #define L10N_PARAM_POS2             "pos2"
    #define L10N_PARAM_POS3             "pos3"
    #define L10N_PARAM_POS4             "pos4"
    #define L10N_PARAM_POS5             "pos5"
    #define L10N_PARAM_POS6             "pos6"
    #define L10N_PARAM_POS7             "pos7"
    #define L10N_PARAM_POS8             "pos8"
    #define L10N_PARAM_POS9             "pos9"
#endif


