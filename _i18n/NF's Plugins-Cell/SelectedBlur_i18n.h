#pragma once

/*
 * Localization switch for SelectedBlur.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's SelectedBlur"
    #define L10N_PLUGIN_DESC            "仅模糊所选颜色。CS6兼容测试版"
    #define L10N_PARAM_BLUR             "模糊度"
    #define L10N_PARAM_RANGE            "阈值"
    #define L10N_PARAM_ENABLE           "方案"
    #define L10N_PARAM_ON               "开"
    #define L10N_PARAM_TARGET0          "颜色0"
    #define L10N_PARAM_TARGET1          "颜色1"
    #define L10N_PARAM_TARGET2          "颜色2"
    #define L10N_PARAM_TARGET3          "颜色3"
    #define L10N_PARAM_TARGET4          "颜色4"
    #define L10N_PARAM_TARGET5          "颜色5"
    #define L10N_PARAM_TARGET6          "颜色6"
    #define L10N_PARAM_TARGET7          "颜色7"
#else
    #define L10N_PLUGIN_NAME            "F's SelectedBlur"
    #define L10N_PLUGIN_DESC            "選択した色だけぼかします。CS6対応テストバージョン"
    #define L10N_PARAM_BLUR             "blur"
    #define L10N_PARAM_RANGE            "range"
    #define L10N_PARAM_ENABLE           "有効"
    #define L10N_PARAM_ON               "ON"
    #define L10N_PARAM_TARGET0          "target0"
    #define L10N_PARAM_TARGET1          "target1"
    #define L10N_PARAM_TARGET2          "target2"
    #define L10N_PARAM_TARGET3          "target3"
    #define L10N_PARAM_TARGET4          "target4"
    #define L10N_PARAM_TARGET5          "target5"
    #define L10N_PARAM_TARGET6          "target6"
    #define L10N_PARAM_TARGET7          "target7"
#endif



