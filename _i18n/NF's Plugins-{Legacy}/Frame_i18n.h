#pragma once

/*
 * Localization switch for Frame.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's Frame"
    #define L10N_PLUGIN_DESC            "绘制安全框"
    #define L10N_PARAM_WIDTH            "宽度"
    #define L10N_PARAM_HEIGHT           "高度"
    #define L10N_PARAM_LINE_COLOR       "参考线颜色"
    #define L10N_PARAM_SAFE_FRAME       "安全框"
    #define L10N_PARAM_CENTER_LINE      "中心线"
    #define L10N_PARAM_ON               "开"
    #define L10N_PARAM_OUT_COLOR        "框外颜色"
    #define L10N_PARAM_OUT_OPACITY      "框外不透明度"
    #define L10N_PARAM_LINE_HEIGHT      "线条宽度"
    #define L10N_PARAM_SIZE             "大小"
    #define L10N_PARAM_SIZE_ITEMS       "自定义|720x540|1024x576|1024x768|1280x720|1440x810|1920x1080"
#else
    #define L10N_PLUGIN_NAME            "F's Frame"
    #define L10N_PLUGIN_DESC            "フレームを描く"
    #define L10N_PARAM_WIDTH            "width"
    #define L10N_PARAM_HEIGHT           "height"
    #define L10N_PARAM_LINE_COLOR       "line_color"
    #define L10N_PARAM_SAFE_FRAME       "safe_frame"
    #define L10N_PARAM_CENTER_LINE      "center_line"
    #define L10N_PARAM_ON               "ON"
    #define L10N_PARAM_OUT_COLOR        "out_color"
    #define L10N_PARAM_OUT_OPACITY      "out_opacity"
    #define L10N_PARAM_LINE_HEIGHT      "line_height"
    #define L10N_PARAM_SIZE             "size"
    #define L10N_PARAM_SIZE_ITEMS       "上の数値|720x540|1024x576|1024x768|1280x720|1440x810|1920x1080"
#endif



