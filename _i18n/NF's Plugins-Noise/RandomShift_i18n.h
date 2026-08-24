#pragma once

/*
 * Localization switch for RandomShift.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's RandomShift"
    #define L10N_PLUGIN_DESC            "随机错位随机矩形"
    #define L10N_PARAM_AMOUNT           "数量"
    #define L10N_PARAM_SHIFT_MAX        "最大水平偏移"
    #define L10N_PARAM_SHIFT_MIN        "最小水平偏移"
    #define L10N_PARAM_LEN_MAX          "块最大宽度"
    #define L10N_PARAM_LEN_MIN          "块最小宽度"
    #define L10N_PARAM_HEIGHT_MAX       "块最大高度"
    #define L10N_PARAM_HEIGHT_MIN       "块最小高度"
    #define L10N_PARAM_VER_SHIFT        "垂直偏移"
#else
    #define L10N_PLUGIN_NAME            "F's RandomShift"
    #define L10N_PLUGIN_DESC            "ランダムな矩形をランダムにずらします"
    #define L10N_PARAM_AMOUNT           "量"
    #define L10N_PARAM_SHIFT_MAX        "ずらし幅の最大値(px)"
    #define L10N_PARAM_SHIFT_MIN        "ずらし幅の最小値(px)"
    #define L10N_PARAM_LEN_MAX          "横幅の最大値(px)"
    #define L10N_PARAM_LEN_MIN          "横幅の最小値(px)"
    #define L10N_PARAM_HEIGHT_MAX       "縦幅の最大値(px)"
    #define L10N_PARAM_HEIGHT_MIN       "縦幅の最小値(px)"
    #define L10N_PARAM_VER_SHIFT        "上下のずらし幅(px)"
#endif



