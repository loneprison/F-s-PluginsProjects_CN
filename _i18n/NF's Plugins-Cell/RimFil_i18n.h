#pragma once

/*
 * Localization switch for RimFil.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's RimFill"
    #define L10N_PLUGIN_DESC            "对素材边缘扩展填充"
    #define L10N_PARAM_WIDTH            "宽度"
    #define L10N_PARAM_FILL_METHOD      "填充方式"
    #define L10N_PARAM_FILL_ITEMS       "指定颜色|相邻颜色"
    #define L10N_PARAM_CUSTOM_COLOR     "指定颜色"
    #define L10N_PARAM_WHITE_TRANS      "在白色像素上填充"
    #define L10N_PARAM_ON                  "开"
#else
    #define L10N_PLUGIN_NAME            "F's RimFill"
    #define L10N_PLUGIN_DESC            "RimFill"
    #define L10N_PARAM_WIDTH            "width"
    #define L10N_PARAM_FILL_METHOD      "FillMethod"
    #define L10N_PARAM_FILL_ITEMS       "CustomColor|AdjacentColor"
    #define L10N_PARAM_CUSTOM_COLOR     "CustomColor"
    #define L10N_PARAM_WHITE_TRANS      "Treat White as Transparent"
    #define L10N_PARAM_ON                  "on"
#endif



