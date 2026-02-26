#pragma once

/*
 * Localization switch for IroToreAdjacent.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's IroToreAdjacent"
    #define L10N_PLUGIN_DESC            "将与指定颜色相邻的主线强制转化为带颜色的线条"
    #define L10N_PARAM_LINE_ONLY        "仅线条"
    #define L10N_PARAM_NEW_COLOR        "颜色"
    #define L10N_PARAM_VALUE            "半径"
    #define L10N_PARAM_LINE_MINMAX      "最小/最大"
    #define L10N_PARAM_LINE_BLUR        "底色模糊度"
    #define L10N_PARAM_ON               "开"
    #define L10N_PARAM_MAIN1_ON         "主线条方案1"
    #define L10N_PARAM_MAIN2_ON         "主线条方案2"
    #define L10N_PARAM_MAIN1            "主线色1"
    #define L10N_PARAM_MAIN2            "主线色2"
    #define L10N_PARAM_ADJ1_ON          "相邻方案1"
    #define L10N_PARAM_ADJ2_ON          "相邻方案2"
    #define L10N_PARAM_ADJ3_ON          "相邻方案3"
    #define L10N_PARAM_ADJ4_ON          "相邻方案4"
    #define L10N_PARAM_ADJ5_ON          "相邻方案5"
    #define L10N_PARAM_ADJ6_ON          "相邻方案6"
    #define L10N_PARAM_ADJ1             "相邻颜色1"
    #define L10N_PARAM_ADJ2             "相邻颜色2"
    #define L10N_PARAM_ADJ3             "相邻颜色3"
    #define L10N_PARAM_ADJ4             "相邻颜色4"
    #define L10N_PARAM_ADJ5             "相邻颜色5"
    #define L10N_PARAM_ADJ6             "相邻颜色6"
    #define L10N_PARAM_LEVEL            "阈值"
#else
    #define L10N_PLUGIN_NAME            "F's IroToreAdjacent"
    #define L10N_PLUGIN_DESC            "指定した色に隣接した主線を無理やり色トレスにします"
    #define L10N_PARAM_LINE_ONLY        "LineOnly"
    #define L10N_PARAM_NEW_COLOR        "NewColor"
    #define L10N_PARAM_VALUE            "Value"
    #define L10N_PARAM_LINE_MINMAX      "Min/Max"
    #define L10N_PARAM_LINE_BLUR        "Blur"
    #define L10N_PARAM_ON               "on"
    #define L10N_PARAM_MAIN1_ON         "EnabledMain1"
    #define L10N_PARAM_MAIN2_ON         "EnabledMain2"
    #define L10N_PARAM_MAIN1            "MainColor1"
    #define L10N_PARAM_MAIN2            "MainColor2"
    #define L10N_PARAM_ADJ1_ON          "EnabledAdjacent1"
    #define L10N_PARAM_ADJ2_ON          "EnabledAdjacent2"
    #define L10N_PARAM_ADJ3_ON          "EnabledAdjacent3"
    #define L10N_PARAM_ADJ4_ON          "EnabledAdjacent4"
    #define L10N_PARAM_ADJ5_ON          "EnabledAdjacent5"
    #define L10N_PARAM_ADJ6_ON          "EnabledAdjacent6"
    #define L10N_PARAM_ADJ1             "AdjacentColor1"
    #define L10N_PARAM_ADJ2             "AdjacentColor2"
    #define L10N_PARAM_ADJ3             "AdjacentColor3"
    #define L10N_PARAM_ADJ4             "AdjacentColor4"
    #define L10N_PARAM_ADJ5             "AdjacentColor5"
    #define L10N_PARAM_ADJ6             "AdjacentColor6"
    #define L10N_PARAM_LEVEL            "level"
#endif



