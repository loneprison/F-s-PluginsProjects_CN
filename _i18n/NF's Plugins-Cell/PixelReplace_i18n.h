#pragma once

/*
 * Localization switch for PixelReplace.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's PixelReplace"
    #define L10N_PLUGIN_DESC            "替换颜色"
    #define L10N_PARAM_TOPIC            "方案"
    #define L10N_PARAM_TARGET_FORMAT    "方案%d"
    #define L10N_PARAM_ENABLED          "启用"
    #define L10N_PARAM_ON               "开"
    #define L10N_PARAM_SOURCE_COLOR     "目标颜色"
    #define L10N_PARAM_REPLACE_COLOR    "替换色"
    #define L10N_PARAM_REPLACE_OPACITY  "替换色不透明度"
    #define L10N_PARAM_LEVEL            "阈值"
    #define L10N_PARAM_DISP             "显示数量"
    #define L10N_PARAM_DISP_ITEMS       "1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24"
#else
    #define L10N_PLUGIN_NAME            "F's PixelReplace"
    #define L10N_PLUGIN_DESC            "色変えします"
    #define L10N_PARAM_TOPIC            "Target"
    #define L10N_PARAM_TARGET_FORMAT    "target%d"
    #define L10N_PARAM_ENABLED          "Enabled"
    #define L10N_PARAM_ON               "ON"
    #define L10N_PARAM_SOURCE_COLOR     "targetColor"
    #define L10N_PARAM_REPLACE_COLOR    "replaceColor"
    #define L10N_PARAM_REPLACE_OPACITY  "replaceOpacity"
    #define L10N_PARAM_LEVEL            "lebel"
    #define L10N_PARAM_DISP             "Disp"
    #define L10N_PARAM_DISP_ITEMS       "1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24"
#endif

