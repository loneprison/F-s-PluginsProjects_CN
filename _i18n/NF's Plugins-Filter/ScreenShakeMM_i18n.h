#pragma once

/*
 * Localization switch for ScreenShakeMM.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's ScreenShakeMM"
    #define L10N_PLUGIN_DESC            "动画风屏幕抖动，方向指示版（单位毫米）"
    #define L10N_PARAM_AMOUNT_MM        "幅度 (毫米)"
    #define L10N_PARAM_AMOUNT_RND       "随机幅度 (%)"
    #define L10N_PARAM_DIR              "方向"
    #define L10N_PARAM_DIR_RND          "随机方向"
    #define L10N_PARAM_RANDOM_SEED      "随机种子"
    #define L10N_PARAM_EDGE_MODE        "边缘模式"
    #define L10N_PARAM_EDGE_MODE_ITEMS  "透明|延伸|平铺|镜像"
    #define L10N_PARAM_DPI              "分辨率 (dpi)"
    #define L10N_PARAM_TEST_TIME_DISP   "显示时间"
    #define L10N_PARAM_ON               "开"
#else
    #define L10N_PLUGIN_NAME            "F's ScreenShakeMM"
    #define L10N_PLUGIN_DESC            "アニメちっく画面動。方向指示バージョン単位がミリ"
    #define L10N_PARAM_AMOUNT_MM        "大きさ(mm)"
    #define L10N_PARAM_AMOUNT_RND       "大きさのばらつき(%)"
    #define L10N_PARAM_DIR              "方向(Rot)"
    #define L10N_PARAM_DIR_RND          "方向のばらつき(Rot)"
    #define L10N_PARAM_RANDOM_SEED      "Random Seed"
    #define L10N_PARAM_EDGE_MODE        "縁の処理"
    #define L10N_PARAM_EDGE_MODE_ITEMS  "透明|伸ばす|繰り返す1|繰り返す2"
    #define L10N_PARAM_DPI              "解像度(dpi)"
    #define L10N_PARAM_TEST_TIME_DISP   "Time Disp"
    #define L10N_PARAM_ON               "ON"
#endif



