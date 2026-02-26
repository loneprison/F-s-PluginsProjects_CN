#pragma once

/*
 * Localization switch for YuvControl.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's YuvControl"
    #define L10N_PLUGIN_DESC            "YUV控制"
    #define L10N_PARAM_Y                "Y"
    #define L10N_PARAM_U                "U"
    #define L10N_PARAM_V                "V"
    #define L10N_PARAM_UV_AUTO          "UV 与 Y 联动"
    #define L10N_PARAM_ON               "开"
#else
    #define L10N_PLUGIN_NAME            "F's YuvControl"
    #define L10N_PLUGIN_DESC            "Yuv制御"
    #define L10N_PARAM_Y                "Y"
    #define L10N_PARAM_U                "U"
    #define L10N_PARAM_V                "V"
    #define L10N_PARAM_UV_AUTO          "UVをYと連動させる"
    #define L10N_PARAM_ON               "on"
#endif



