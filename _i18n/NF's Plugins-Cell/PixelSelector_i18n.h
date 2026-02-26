#pragma once

/*
 * Localization switch for PixelSelector.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's PixelSelector"
    #define L10N_PLUGIN_DESC            "将所选颜色以外设为透明。"
    #define L10N_PARAM_TOPIC            "选项"
    #define L10N_PARAM_ON               "开"
    #define L10N_PARAM_REVERSE          "反转"
    #define L10N_PARAM_FILL             "填充"
    #define L10N_PARAM_FILL_COLOR       "填充颜色"
    #define L10N_PARAM_FILL_OPACITY     "填充不透明度"
    #define L10N_PARAM_ENABLED          "启用"
    #define L10N_PARAM_TARGET           "方案"
    #define L10N_PARAM_TARGET_COLOR     "目标颜色"
    #define L10N_PARAM_LEVEL            "阈值"
    #define L10N_PARAM_DISP             "显示数量"
    #define L10N_PARAM_DISP_ITEMS       "1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24"
    #define L10N_ERR_GET_AEPRM          "抱歉，发生错误。\\nAfterEffects_Params error!"
    #define L10N_ERR_GET_PRM            "抱歉，发生错误。\\nPixelSelector_Params error!"
#else
    #define L10N_PLUGIN_NAME            "F's PixelSelector"
    #define L10N_PLUGIN_DESC            "選択した色以外を透明にします。"
    #define L10N_PARAM_TOPIC            "Option"
    #define L10N_PARAM_ON               "ON"
    #define L10N_PARAM_REVERSE          "反転する"
    #define L10N_PARAM_FILL             "塗りつぶす"
    #define L10N_PARAM_FILL_COLOR       "fillColor"
    #define L10N_PARAM_FILL_OPACITY     "fillColor_opacity"
    #define L10N_PARAM_ENABLED          "Enabled"
    #define L10N_PARAM_TARGET           "target"
    #define L10N_PARAM_TARGET_COLOR     "targetColor"
    #define L10N_PARAM_LEVEL            "level"
    #define L10N_PARAM_DISP             "Disp"
    #define L10N_PARAM_DISP_ITEMS       "1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24"
    #define L10N_ERR_GET_AEPRM          "すみませんエラーです。\\nAfterEffects_Params error!"
    #define L10N_ERR_GET_PRM            "すみませんエラーです。\\nPixelSelector_Params error!"
#endif

