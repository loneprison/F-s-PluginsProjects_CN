#pragma once

/*
 * Localization switch for MainLineRepaint_old.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME                    "F's MainLineRepaint"
    #define L10N_PLUGIN_DESC                    "去除二值图像的主线"
    #define L10N_PLUGIN_MADEBY                  "bry-ful"
    #define L10N_PARAM_MAIN_COLOR               "主线颜色"
    #define L10N_ERR_GETFSAEPARAMS              "错误: 图像缓冲区尺寸错误。"
    #define L10N_ERR_GETPARAMS                  "错误: 参数错误。"
#else
    #define L10N_PLUGIN_NAME                    "F's MainLineRepaint"
    #define L10N_PLUGIN_DESC                    "セル画の主線を無くします"
    #define L10N_PLUGIN_MADEBY                  "bry-ful"
    #define L10N_PARAM_MAIN_COLOR               "主線の色"
    #define L10N_ERR_GETFSAEPARAMS              "画像バッファーサイズエラーです。御免なさい。"
    #define L10N_ERR_GETPARAMS                  "パラメータエラーです。御免なさい。"
#endif

