#pragma once

/*
 * Localization switch for colorThreshold.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

 
#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's colorThreshold"
    #define L10N_PLUGIN_DESC            "将颜色约束为指定的颜色"
    #define L10N_PARAM_ALPHA_LEVEL      "Alpha 阈值"
    #define L10N_PARAM_MATCH_LEVEL      "色相/饱和度 阈值"
    #define L10N_PARAM_LIGHT_LEVEL      "亮度 阈值"
    #define L10N_PARAM_MAIN_ON1         "启用1"
    #define L10N_PARAM_MAIN_ON2         "启用2"
    #define L10N_PARAM_MAIN_ON3         "启用3"
    #define L10N_PARAM_ON               "开"
    #define L10N_PARAM_MAIN_COLOR1      "主线颜色1"
    #define L10N_PARAM_MAIN_COLOR2      "主线颜色2"
    #define L10N_PARAM_MAIN_COLOR3      "主线颜色3"
    #define L10N_PARAM_MAIN_LEVEL1      "主线颜色1_色相饱和阈值"
    #define L10N_PARAM_MAIN_LEVEL2      "主线颜色2_色相饱和阈值"
    #define L10N_PARAM_MAIN_LEVEL3      "主线颜色3_色相饱和阈值"
    #define L10N_PARAM_MAIN_HS1         "主线颜色1_hs阈值"
    #define L10N_PARAM_MAIN_HS2         "主线颜色2_hs阈值"
    #define L10N_PARAM_MAIN_HS3         "主线颜色3_hs阈值"
    #define L10N_PARAM_TOPIC_MAIN       "线条颜色"
    #define L10N_PARAM_TOPIC_SUB        "匹配颜色"
    #define L10N_PARAM_SUB_COUNT        "匹配颜色数量"
    #define L10N_PARAM_USER_COLOR_FORMAT "匹配颜色_%d"
#else
    #define L10N_PLUGIN_NAME            "F's colorThreshold"
    #define L10N_PLUGIN_DESC            "色を単色化します。"
    #define L10N_PARAM_ALPHA_LEVEL      "alpha_Level"
    #define L10N_PARAM_MATCH_LEVEL      "colorMatch_level"
    #define L10N_PARAM_LIGHT_LEVEL      "colorLightness_level"
    #define L10N_PARAM_MAIN_ON1         "Enabled_1"
    #define L10N_PARAM_MAIN_ON2         "Enabled_2"
    #define L10N_PARAM_MAIN_ON3         "Enabled_3"
    #define L10N_PARAM_ON               "on"
    #define L10N_PARAM_MAIN_COLOR1      "color1"
    #define L10N_PARAM_MAIN_COLOR2      "color2"
    #define L10N_PARAM_MAIN_COLOR3      "color3"
    #define L10N_PARAM_MAIN_LEVEL1      "color1_level"
    #define L10N_PARAM_MAIN_LEVEL2      "color2_level"
    #define L10N_PARAM_MAIN_LEVEL3      "color3_level"
    #define L10N_PARAM_MAIN_HS1         "color1_hs"
    #define L10N_PARAM_MAIN_HS2         "color2_hs"
    #define L10N_PARAM_MAIN_HS3         "color3_hs"
    #define L10N_PARAM_TOPIC_MAIN       "LineColors"
    #define L10N_PARAM_TOPIC_SUB        "UseColor"
    #define L10N_PARAM_SUB_COUNT        "UseColor_count"
    #define L10N_PARAM_USER_COLOR_FORMAT "UserColor_%d"
#endif


