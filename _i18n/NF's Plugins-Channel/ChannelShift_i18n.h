#pragma once

/*
 * Localization switch for ChannelShift.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */


#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's ChannelShift"
    #define L10N_PLUGIN_DESC            "按通道偏移图像"
    #define L10N_PARAM_RED_TOPIC        "红色"
    #define L10N_PARAM_RED_ROT          "红色角度"
    #define L10N_PARAM_RED_LENGTH       "红色偏移"
    #define L10N_PARAM_GREEN_TOPIC      "绿色"
    #define L10N_PARAM_GREEN_ROT        "绿色角度"
    #define L10N_PARAM_GREEN_LENGTH     "绿色偏移"
    #define L10N_PARAM_BLUE_TOPIC       "蓝色"
    #define L10N_PARAM_BLUE_ROT         "蓝色角度"
    #define L10N_PARAM_BLUE_LENGTH      "蓝色偏移"
    #define L10N_PARAM_ALPHA_TOPIC      "Alpha"
    #define L10N_PARAM_ALPHA_ROT        "Alpha角度"
    #define L10N_PARAM_ALPHA_LENGTH     "Alpha偏移"
    #define L10N_PARAM_EDGE             "边缘处理"
    #define L10N_PARAM_EDGE_ITEMS       "无|扩展|平铺|镜像"
#else
    #define L10N_PLUGIN_NAME            "F's ChannelShift"
    #define L10N_PLUGIN_DESC            "チャンネル別に画像をシフトします。"
    #define L10N_PARAM_RED_TOPIC        "Red"
    #define L10N_PARAM_RED_ROT          "Red_Rot"
    #define L10N_PARAM_RED_LENGTH       "Red_Length"
    #define L10N_PARAM_GREEN_TOPIC      "Green"
    #define L10N_PARAM_GREEN_ROT        "Green_Rot"
    #define L10N_PARAM_GREEN_LENGTH     "Green_Length"
    #define L10N_PARAM_BLUE_TOPIC       "Blue"
    #define L10N_PARAM_BLUE_ROT         "Blue_Rot"
    #define L10N_PARAM_BLUE_LENGTH      "Blue_Length"
    #define L10N_PARAM_ALPHA_TOPIC      "Alpha"
    #define L10N_PARAM_ALPHA_ROT        "Alpha_Rot"
    #define L10N_PARAM_ALPHA_LENGTH     "Alpha_Length"
    #define L10N_PARAM_EDGE             "Edge"
    #define L10N_PARAM_EDGE_ITEMS       "none|extend|tile|mirror"
#endif



