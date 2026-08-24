#pragma once

/*
 * Localization switch for Star.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's Star"
    #define L10N_PLUGIN_DESC            "简易十字滤镜"
    #define L10N_PARAM_LENGTH               "长度 (%)"
    #define L10N_PARAM_STRONG               "强度 (%)"
    #define L10N_PARAM_ROT                  "旋转"
    #define L10N_PARAM_COLOR_TOPIC          "颜色"
    #define L10N_PARAM_COLOR_KIND           "模式"
    #define L10N_PARAM_COLOR_KIND_ITEMS     "A 到 B|B 到 A|仅 A|仅 B|屏幕"
    #define L10N_PARAM_COLOR_A              "颜色 A"
    #define L10N_PARAM_COLOR_B              "颜色 B"
    #define L10N_PARAM_COLOR_BORDER         "颜色 AB 占比 (%)"
    #define L10N_PARAM_LINE1_TOPIC          "线1"
    #define L10N_PARAM_LINE1_LENGTH         "线1 长度"
    #define L10N_PARAM_LINE1_STRONG         "线1 强度"
    #define L10N_PARAM_LINE1_ROT            "线1 旋转"
    #define L10N_PARAM_LINE2_TOPIC          "线2"
    #define L10N_PARAM_LINE2_LENGTH         "线2 长度"
    #define L10N_PARAM_LINE2_STRONG         "线2 强度"
    #define L10N_PARAM_LINE2_ROT            "线2 旋转"
    #define L10N_PARAM_LINE3_TOPIC          "线3"
    #define L10N_PARAM_LINE3_LENGTH         "线3 长度"
    #define L10N_PARAM_LINE3_STRONG         "线3 强度"
    #define L10N_PARAM_LINE3_ROT            "线3 旋转"
    #define L10N_PARAM_LINE4_TOPIC          "线4"
    #define L10N_PARAM_LINE4_LENGTH         "线4 长度"
    #define L10N_PARAM_LINE4_STRONG         "线4 强度"
    #define L10N_PARAM_LINE4_ROT            "线4 旋转"
#else
    #define L10N_PLUGIN_NAME            "F's Star"
    #define L10N_PLUGIN_DESC            "簡単なクロスフィルタ"
    #define L10N_PARAM_LENGTH               "Length(%)"
    #define L10N_PARAM_STRONG               "Strong(%)"
    #define L10N_PARAM_ROT                  "Rot"
    #define L10N_PARAM_COLOR_TOPIC          "Color"
    #define L10N_PARAM_COLOR_KIND           "Kind"
    #define L10N_PARAM_COLOR_KIND_ITEMS     "A To B|B To A|A Only|B Only|Screen"
    #define L10N_PARAM_COLOR_A              "Color A"
    #define L10N_PARAM_COLOR_B              "Color B"
    #define L10N_PARAM_COLOR_BORDER         "Color Border(%)"
    #define L10N_PARAM_LINE1_TOPIC          "Line1"
    #define L10N_PARAM_LINE1_LENGTH         "Line1 Length"
    #define L10N_PARAM_LINE1_STRONG         "Line1 Strong"
    #define L10N_PARAM_LINE1_ROT            "Line1 Rot"
    #define L10N_PARAM_LINE2_TOPIC          "Line2"
    #define L10N_PARAM_LINE2_LENGTH         "Line2 Length"
    #define L10N_PARAM_LINE2_STRONG         "Line2 Strong"
    #define L10N_PARAM_LINE2_ROT            "Line2 Rot"
    #define L10N_PARAM_LINE3_TOPIC          "Line3"
    #define L10N_PARAM_LINE3_LENGTH         "Line3 Length"
    #define L10N_PARAM_LINE3_STRONG         "Line3 Strong"
    #define L10N_PARAM_LINE3_ROT            "Line3 Rot"
    #define L10N_PARAM_LINE4_TOPIC          "Line4"
    #define L10N_PARAM_LINE4_LENGTH         "Line4 Length"
    #define L10N_PARAM_LINE4_STRONG         "Line4 Strong"
    #define L10N_PARAM_LINE4_ROT            "Line4 Rot"
#endif



