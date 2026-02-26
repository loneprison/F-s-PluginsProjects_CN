#pragma once

/*
 * Localization switch for SparkStorm.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's SparkStorm"
    #define L10N_PLUGIN_DESC            "绘制动画风格闪电，风暴版"
    #define L10N_PARAM_SEED             "全局随机种子"
    #define L10N_PARAM_SEED_POS         "位置随机种子"
    #define L10N_PARAM_SEED_MOVE        "形态随机种子"
    #define L10N_PARAM_SEED_DRAW        "绘制随机种子"
    #define L10N_PARAM_OFFSET           "偏移"
    #define L10N_PARAM_WIPE             "擦除 (%)"
    #define L10N_PARAM_START0           "起点0"
    #define L10N_PARAM_START1           "起点1"
    #define L10N_PARAM_LAST0            "终点0"
    #define L10N_PARAM_LAST1            "终点1"
    #define L10N_PARAM_FIRST_RAND_X     "起点随机 X"
    #define L10N_PARAM_FIRST_RAND_Y     "起点随机 Y"
    #define L10N_PARAM_LAST_RAND_X      "终点随机 X"
    #define L10N_PARAM_LAST_RAND_Y      "终点随机 Y"
    #define L10N_PARAM_LINE_SIZE        "线条大小"
    #define L10N_PARAM_LINE_MOVE        "湍流强度"
    #define L10N_PARAM_FOLD_COUNT       "湍流复杂度"
    #define L10N_PARAM_DRAW_COUNT       "绘制数量"
    #define L10N_PARAM_SUB_COUNT        "分叉支数"
    #define L10N_PARAM_COLOR            "颜色"
    #define L10N_PARAM_BLEND            "在原始图像上合成"
    #define L10N_PARAM_ON               "开"
#else
    #define L10N_PLUGIN_NAME            "F's SparkStorm"
    #define L10N_PLUGIN_DESC            "アニメっぽい稲妻の描画、嵐"
    #define L10N_PARAM_SEED             "seed"
    #define L10N_PARAM_SEED_POS         "seedPos"
    #define L10N_PARAM_SEED_MOVE        "seedMove"
    #define L10N_PARAM_SEED_DRAW        "seedDraw"
    #define L10N_PARAM_OFFSET           "offset"
    #define L10N_PARAM_WIPE             "wipe(%)"
    #define L10N_PARAM_START0           "start0"
    #define L10N_PARAM_START1           "start1"
    #define L10N_PARAM_LAST0            "last0"
    #define L10N_PARAM_LAST1            "last1"
    #define L10N_PARAM_FIRST_RAND_X     "first_randX"
    #define L10N_PARAM_FIRST_RAND_Y     "first_randY"
    #define L10N_PARAM_LAST_RAND_X      "last_randX"
    #define L10N_PARAM_LAST_RAND_Y      "last_randY"
    #define L10N_PARAM_LINE_SIZE        "lineSize"
    #define L10N_PARAM_LINE_MOVE        "lineMove"
    #define L10N_PARAM_FOLD_COUNT       "foldCount"
    #define L10N_PARAM_DRAW_COUNT       "drawCount"
    #define L10N_PARAM_SUB_COUNT        "subCount"
    #define L10N_PARAM_COLOR            "color"
    #define L10N_PARAM_BLEND            "blend"
    #define L10N_PARAM_ON               "on"
#endif



