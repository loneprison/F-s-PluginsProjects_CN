#pragma once

/*
 * Localization switch for ColorChange.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

 
#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's ColorChange"
    #define L10N_PLUGIN_DESC            "替换指定颜色"

    #define L10N_PARAM_LEVEL            "阈值"
    #define L10N_PARAM_MODE             "激活方案"
    #define L10N_PARAM_EXEC             "开"

    #define L10N_PARAM_TARGET0          "方案0"
    #define L10N_PARAM_SRCCOL0          "原始颜色0"
    #define L10N_PARAM_DSTCOL0          "替换颜色0"

    #define L10N_PARAM_TARGET1          "方案1"
    #define L10N_PARAM_SRCCOL1          "原始颜色1"
    #define L10N_PARAM_DSTCOL1          "替换颜色1"

    #define L10N_PARAM_TARGET2          "方案2"
    #define L10N_PARAM_SRCCOL2          "原始颜色2"
    #define L10N_PARAM_DSTCOL2          "替换颜色2"

    #define L10N_PARAM_TARGET3          "方案3"
    #define L10N_PARAM_SRCCOL3          "原始颜色3"
    #define L10N_PARAM_DSTCOL3          "替换颜色3"

    #define L10N_PARAM_TARGET4          "方案4"
    #define L10N_PARAM_SRCCOL4          "原始颜色4"
    #define L10N_PARAM_DSTCOL4          "替换颜色4"

    #define L10N_PARAM_TARGET5          "方案5"
    #define L10N_PARAM_SRCCOL5          "原始颜色5"
    #define L10N_PARAM_DSTCOL5          "替换颜色5"

    #define L10N_PARAM_TARGET6          "方案6"
    #define L10N_PARAM_SRCCOL6          "原始颜色6"
    #define L10N_PARAM_DSTCOL6          "替换颜色6"

    #define L10N_PARAM_TARGET7          "方案7"
    #define L10N_PARAM_SRCCOL7          "原始颜色7"
    #define L10N_PARAM_DSTCOL7          "替换颜色7"
#else
    #define L10N_PLUGIN_NAME            "F's ColorChange"
    #define L10N_PLUGIN_DESC            "単色の色変えをします"

    #define L10N_PARAM_LEVEL            "許容値"
    #define L10N_PARAM_MODE             "モード"
    #define L10N_PARAM_EXEC             "実行する"

    #define L10N_PARAM_TARGET0          "Target0"
    #define L10N_PARAM_SRCCOL0          "元の色0"
    #define L10N_PARAM_DSTCOL0          "新しい色0"

    #define L10N_PARAM_TARGET1          "Target1"
    #define L10N_PARAM_SRCCOL1          "元の色1"
    #define L10N_PARAM_DSTCOL1          "新しい色1"

    #define L10N_PARAM_TARGET2          "Target2"
    #define L10N_PARAM_SRCCOL2          "元の色2"
    #define L10N_PARAM_DSTCOL2          "新しい色2"

    #define L10N_PARAM_TARGET3          "Target3"
    #define L10N_PARAM_SRCCOL3          "元の色3"
    #define L10N_PARAM_DSTCOL3          "新しい色3"

    #define L10N_PARAM_TARGET4          "Target4"
    #define L10N_PARAM_SRCCOL4          "元の色4"
    #define L10N_PARAM_DSTCOL4          "新しい色4"

    #define L10N_PARAM_TARGET5          "Target5"
    #define L10N_PARAM_SRCCOL5          "元の色5"
    #define L10N_PARAM_DSTCOL5          "新しい色5"

    #define L10N_PARAM_TARGET6          "Target6"
    #define L10N_PARAM_SRCCOL6          "元の色6"
    #define L10N_PARAM_DSTCOL6          "新しい色6"

    #define L10N_PARAM_TARGET7          "Target7"
    #define L10N_PARAM_SRCCOL7          "元の色7"
    #define L10N_PARAM_DSTCOL7          "新しい色7"
#endif



