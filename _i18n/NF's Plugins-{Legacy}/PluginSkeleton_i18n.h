#pragma once

/*
 * Localization switch for PluginSkeleton.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's PluginSkeleton"
    #define L10N_PLUGIN_DESC            "测试用插件骨架"
    #define L10N_PARAM_R                "R"
    #define L10N_PARAM_G                "G"
    #define L10N_PARAM_B                "B"
    #define L10N_PARAM_NOISE            "杂色"
    #define L10N_PARAM_NOISE_FRAME      "随机种子"
    #define L10N_PARAM_ON               "开"
    #define L10N_PARAM_NOISE_OFFSET     "杂色相位"
    #define L10N_PARAM_HIDDEN_UI        "隐藏界面"
    #define L10N_PARAM_HIDDEN_TEXT      "oba-Q!"
    #define L10N_PARAM_SAMPLE_TOPIC     "示例主题"
    #define L10N_PARAM_ADD_SLIDER       "整数滑块"
    #define L10N_PARAM_FIXED_SLIDER     "定点小数滑块"
    #define L10N_PARAM_FLOAT_SLIDER     "浮点滑块"
    #define L10N_PARAM_COLOR            "颜色"
    #define L10N_PARAM_CHECKBOX         "复选框"
    #define L10N_PARAM_ANGLE            "角度"
    #define L10N_PARAM_POPUP            "下拉菜单"
    #define L10N_PARAM_POPUP_ITEMS      "一|二|三"
    #define L10N_PARAM_POINT            "点"
    #define L10N_PARAM_BUTTON           "按钮"
    #define L10N_PARAM_PUSH             "按下"
#else
    #define L10N_PLUGIN_NAME            "F's PluginSkeleton"
    #define L10N_PLUGIN_DESC            "プラグインのスケルトン"
    #define L10N_PARAM_R                "R"
    #define L10N_PARAM_G                "G"
    #define L10N_PARAM_B                "B"
    #define L10N_PARAM_NOISE            "noise"
    #define L10N_PARAM_NOISE_FRAME      "frame randerm"
    #define L10N_PARAM_ON               "on"
    #define L10N_PARAM_NOISE_OFFSET     "noise offset"
    #define L10N_PARAM_HIDDEN_UI        "Hidden UI"
    #define L10N_PARAM_HIDDEN_TEXT      "oba-Q!"
    #define L10N_PARAM_SAMPLE_TOPIC     "Sample Topics"
    #define L10N_PARAM_ADD_SLIDER       "Add_Slider"
    #define L10N_PARAM_FIXED_SLIDER     "Fixed_Slider"
    #define L10N_PARAM_FLOAT_SLIDER     "Float_Slider"
    #define L10N_PARAM_COLOR            "Color"
    #define L10N_PARAM_CHECKBOX         "Checkbox"
    #define L10N_PARAM_ANGLE            "Angle"
    #define L10N_PARAM_POPUP            "Popup"
    #define L10N_PARAM_POPUP_ITEMS      "One|Two|Tree"
    #define L10N_PARAM_POINT            "Point"
    #define L10N_PARAM_BUTTON           "button"
    #define L10N_PARAM_PUSH             "push"
#endif



