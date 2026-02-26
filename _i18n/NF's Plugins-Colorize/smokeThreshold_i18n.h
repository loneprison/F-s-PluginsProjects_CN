#pragma once

/*
 * Localization switch for smokeThreshold.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's smokeThreshold"
    #define L10N_PLUGIN_DESC            "将真实烟雾转为动画风格"
    #define L10N_PARAM_ALPHA_THRESHOLD      "Alpha 阈值"
    #define L10N_PARAM_HILIGHT              "高光"
    #define L10N_PARAM_SHADOW1              "阴影1"
    #define L10N_PARAM_SHADOW2              "阴影2"
    #define L10N_PARAM_ON                   "开"
    #define L10N_PARAM_ALPHA_ENABLED        "启用 Alpha 阈值"
    #define L10N_PARAM_HILIGHT_ENABLED      "启用高光"
    #define L10N_PARAM_SHADOW1_ENABLED      "启用阴影1"
    #define L10N_PARAM_SHADOW2_ENABLED      "启用阴影2"
    #define L10N_PARAM_HILIGHT_COLOR        "高光颜色"
    #define L10N_PARAM_NORMAL_COLOR         "正常颜色"
    #define L10N_PARAM_SHADOW1_COLOR        "阴影1颜色"
    #define L10N_PARAM_SHADOW2_COLOR        "阴影2颜色"
    #define L10N_PARAM_LINE_WEIGHT          "描边大小"
    #define L10N_PARAM_OUTLINE              "描边"
    #define L10N_PARAM_NORMAL_LINE          "正常描边"
    #define L10N_PARAM_SHADOW1_LINE         "阴影1描边"
    #define L10N_PARAM_SHADOW2_LINE         "阴影2描边"
    #define L10N_PARAM_NORMAL_LINE_ENABLED  "启用正常描边"
    #define L10N_PARAM_SHADOW1_LINE_ENABLED "启用阴影1描边"
    #define L10N_PARAM_SHADOW2_LINE_ENABLED "启用阴影2描边"
#else
    #define L10N_PLUGIN_NAME            "F's smokeThreshold"
    #define L10N_PLUGIN_DESC            "リアル煙をセルちっくに"
    #define L10N_PARAM_ALPHA_THRESHOLD      "alphaThreshold"
    #define L10N_PARAM_HILIGHT              "hilight"
    #define L10N_PARAM_SHADOW1              "shadow1"
    #define L10N_PARAM_SHADOW2              "shadow2"
    #define L10N_PARAM_ON                   "on"
    #define L10N_PARAM_ALPHA_ENABLED        "alphaThresholdEnabled"
    #define L10N_PARAM_HILIGHT_ENABLED      "hilightEnabled"
    #define L10N_PARAM_SHADOW1_ENABLED      "shadow1Enabled"
    #define L10N_PARAM_SHADOW2_ENABLED      "shadow2Enabled"
    #define L10N_PARAM_HILIGHT_COLOR        "hilightColor"
    #define L10N_PARAM_NORMAL_COLOR         "normalColor"
    #define L10N_PARAM_SHADOW1_COLOR        "shadow1Color"
    #define L10N_PARAM_SHADOW2_COLOR        "shadow2Color"
    #define L10N_PARAM_LINE_WEIGHT          "LineWeight"
    #define L10N_PARAM_OUTLINE              "OutLine"
    #define L10N_PARAM_NORMAL_LINE          "normalLine"
    #define L10N_PARAM_SHADOW1_LINE         "shadow1Line"
    #define L10N_PARAM_SHADOW2_LINE         "shadow2Line"
    #define L10N_PARAM_NORMAL_LINE_ENABLED  "normalLine_Enabled"
    #define L10N_PARAM_SHADOW1_LINE_ENABLED "shadow1Line_Enabled"
    #define L10N_PARAM_SHADOW2_LINE_ENABLED "shadow2Line_Enabled"
#endif



