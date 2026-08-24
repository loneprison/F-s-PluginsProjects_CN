#pragma once

/*
 * Localization switch for LineTrace.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's LineTrace"
    #define L10N_PLUGIN_DESC            "快速二值化临摹 (仿RETAS TraceMan)"
    #define L10N_PARAM_ENABLED_BLACK    "黑"
    #define L10N_PARAM_ENABLED_RED      "红"
    #define L10N_PARAM_ENABLED_GREEN    "绿"
    #define L10N_PARAM_ENABLED_BLUE     "蓝"
    #define L10N_PARAM_ENABLED_YELLOW   "黄"
    #define L10N_PARAM_ENABLED_VIOLET   "紫"
    #define L10N_PARAM_ENABLED_ON       "开"
    #define L10N_PARAM_DRAW_BLACK       "填充黑"
    #define L10N_PARAM_DRAW_RED         "填充红"
    #define L10N_PARAM_DRAW_GREEN       "填充绿"
    #define L10N_PARAM_DRAW_BLUE        "填充蓝"
    #define L10N_PARAM_DRAW_YELLOW      "填充黄"
    #define L10N_PARAM_DRAW_VIOLET      "填充紫"
    #define L10N_PARAM_BORDER_BLACK     "黑阈值"
    #define L10N_PARAM_BORDER_RED       "红阈值"
    #define L10N_PARAM_BORDER_GREEN     "绿阈值"
    #define L10N_PARAM_BORDER_BLUE      "蓝阈值"
    #define L10N_PARAM_BORDER_YELLOW    "黄阈值"
    #define L10N_PARAM_BORDER_VIOLET    "紫阈值"
    #define L10N_ERR_GET_AEPRM          "抱歉，发生错误。\\nAfterEffects_Params error!"
    #define L10N_ERR_GET_PRM            "抱歉，发生错误。\\nLineTrace_Params error!"
#else
    #define L10N_PLUGIN_NAME            "F's LineTrace"
    #define L10N_PLUGIN_DESC            "２値化"
    #define L10N_PARAM_ENABLED_BLACK    "Black"
    #define L10N_PARAM_ENABLED_RED      "Red"
    #define L10N_PARAM_ENABLED_GREEN    "Green"
    #define L10N_PARAM_ENABLED_BLUE     "Blue"
    #define L10N_PARAM_ENABLED_YELLOW   "Yellow"
    #define L10N_PARAM_ENABLED_VIOLET   "Violet"
    #define L10N_PARAM_ENABLED_ON       "ON"
    #define L10N_PARAM_DRAW_BLACK       "DrawBlack"
    #define L10N_PARAM_DRAW_RED         "DrawRed"
    #define L10N_PARAM_DRAW_GREEN       "DrawGreen"
    #define L10N_PARAM_DRAW_BLUE        "DrawBlue"
    #define L10N_PARAM_DRAW_YELLOW      "DrawYellow"
    #define L10N_PARAM_DRAW_VIOLET      "DrawViolet"
    #define L10N_PARAM_BORDER_BLACK     "BlackBorder"
    #define L10N_PARAM_BORDER_RED       "RedBorder"
    #define L10N_PARAM_BORDER_GREEN     "GreenBorder"
    #define L10N_PARAM_BORDER_BLUE      "BlueBorder"
    #define L10N_PARAM_BORDER_YELLOW    "YellowBorder"
    #define L10N_PARAM_BORDER_VIOLET    "VioletBorder"
    #define L10N_ERR_GET_AEPRM          "すみませんエラーです。\\nAfterEffects_Params error!"
    #define L10N_ERR_GET_PRM            "すみませんエラーです。\\nLineTrace_Params error!"
#endif



