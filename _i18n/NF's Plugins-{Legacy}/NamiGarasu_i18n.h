#pragma once

/*
 * Localization switch for NamiGarasu.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's NamiGarasu"
    #define L10N_PLUGIN_DESC            "波纹玻璃"
    #define L10N_PARAM_WAVE_VALUE       "扭曲强度"
    #define L10N_PARAM_X_LENGTH         "X_长度"
    #define L10N_PARAM_Y_LENGTH         "Y_长度"
    #define L10N_PARAM_ROT              "风向"
    #define L10N_PARAM_SPEED            "风速"
    #define L10N_PARAM_ADD_MAP          "叠加贴图"
    #define L10N_PARAM_NOISE            "复杂度"
    #define L10N_PARAM_LAYER_A          "A扭曲"
    #define L10N_PARAM_A_SIZE           "A_尺寸"
    #define L10N_PARAM_A_VALUE          "A_数值"
    #define L10N_PARAM_A_STRONG         "A_强度"
    #define L10N_PARAM_A_SPEED          "A_速度"
    #define L10N_PARAM_A_SEED           "A_种子"
    #define L10N_PARAM_LAYER_B          "B扭曲"
    #define L10N_PARAM_B_SIZE           "B_尺寸"
    #define L10N_PARAM_B_VALUE          "B_数值"
    #define L10N_PARAM_B_STRONG         "B_强度"
    #define L10N_PARAM_B_SPEED          "B_速度"
    #define L10N_PARAM_B_SEED           "B_种子"
    #define L10N_PARAM_LAYER_C          "C扭曲"
    #define L10N_PARAM_C_SIZE           "C_尺寸"
    #define L10N_PARAM_C_VALUE          "C_数值"
    #define L10N_PARAM_C_STRONG         "C_强度"
    #define L10N_PARAM_C_SPEED          "C_速度"
    #define L10N_PARAM_C_SEED           "C_种子"
    #define L10N_PARAM_DISP_MAP         "仅贴图"
    #define L10N_PARAM_ON               "开"
#else
    #define L10N_PLUGIN_NAME            "F's NamiGarasu"
    #define L10N_PLUGIN_DESC            "波ガラス"
    #define L10N_PARAM_WAVE_VALUE       "WaveValue"
    #define L10N_PARAM_X_LENGTH         "X_Length"
    #define L10N_PARAM_Y_LENGTH         "Y_Length"
    #define L10N_PARAM_ROT              "Rot"
    #define L10N_PARAM_SPEED            "Speed"
    #define L10N_PARAM_ADD_MAP          "AddMap"
    #define L10N_PARAM_NOISE            "Noise"
    #define L10N_PARAM_LAYER_A          "LayerA"
    #define L10N_PARAM_A_SIZE           "A_size"
    #define L10N_PARAM_A_VALUE          "A_value"
    #define L10N_PARAM_A_STRONG         "A_Strong"
    #define L10N_PARAM_A_SPEED          "A_Speed"
    #define L10N_PARAM_A_SEED           "A_Seed"
    #define L10N_PARAM_LAYER_B          "LayerB"
    #define L10N_PARAM_B_SIZE           "B_size"
    #define L10N_PARAM_B_VALUE          "B_value"
    #define L10N_PARAM_B_STRONG         "B_Strong"
    #define L10N_PARAM_B_SPEED          "B_Speed"
    #define L10N_PARAM_B_SEED           "B_Seed"
    #define L10N_PARAM_LAYER_C          "LayerC"
    #define L10N_PARAM_C_SIZE           "C_size"
    #define L10N_PARAM_C_VALUE          "C_value"
    #define L10N_PARAM_C_STRONG         "C_Strong"
    #define L10N_PARAM_C_SPEED          "C_Speed"
    #define L10N_PARAM_C_SEED           "C_Seed"
    #define L10N_PARAM_DISP_MAP         "DispMap"
    #define L10N_PARAM_ON               "on"
#endif



