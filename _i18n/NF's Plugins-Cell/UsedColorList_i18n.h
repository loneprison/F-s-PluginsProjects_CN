#pragma once

/*
 * Localization switch for UsedColorList.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's UsedColorList"
    #define L10N_PLUGIN_DESC            "提取选区范围中的使用颜色,并显示为颜色列表(最多64种颜色)。"
    #define L10N_PARAM_POS_START        "起始位置"
    #define L10N_PARAM_POS_END          "结束位置"
    #define L10N_PARAM_DISP             "显示表格"
    #define L10N_PARAM_ON               "开"
    #define L10N_PARAM_GRID_WIDTH       "网格宽度"
    #define L10N_PARAM_GRID_HEIGHT      "网格高度"
    #define L10N_PARAM_EXCEPT_COLOR0    "排除颜色0"
    #define L10N_PARAM_EXCEPT_COLOR1    "排除颜色1"
    #define L10N_PARAM_EXCEPT_COLOR2    "排除颜色2"
#else
    #define L10N_PLUGIN_NAME            "F's UsedColorList"
    #define L10N_PLUGIN_DESC            "選択範囲で使用されている色を抽出し、色見本一覧として表示します(最大64色)。 "
    #define L10N_PARAM_POS_START        "PosStart"
    #define L10N_PARAM_POS_END          "PosEnd"
    #define L10N_PARAM_DISP             "Disp"
    #define L10N_PARAM_ON               "on"
    #define L10N_PARAM_GRID_WIDTH       "GridWidrh"
    #define L10N_PARAM_GRID_HEIGHT      "GridHeight"
    #define L10N_PARAM_EXCEPT_COLOR0    "ExceptColor0"
    #define L10N_PARAM_EXCEPT_COLOR1    "ExceptColor1"
    #define L10N_PARAM_EXCEPT_COLOR2    "ExceptColor2"
#endif



