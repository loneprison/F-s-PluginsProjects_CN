#pragma once

/*
 * Localization switch for Spark.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's Spark"
    #define L10N_PLUGIN_DESC            "绘制动画风格闪电"
    #define L10N_PARAM_SEED             "全局随机种子"
    #define L10N_PARAM_SEED_POS         "位置随机种子"
    #define L10N_PARAM_SEED_MOVE        "形态随机种子"
    #define L10N_PARAM_WIPE             "擦除(%)"
    #define L10N_PARAM_OFFSET           "偏移"
    #define L10N_PARAM_START            "起点"
    #define L10N_PARAM_LAST             "终点"
    #define L10N_PARAM_START_RAND_X     "起点随机 X"
    #define L10N_PARAM_START_RAND_Y     "起点随机 Y"
    #define L10N_PARAM_LAST_RAND_X      "终点随机 X"
    #define L10N_PARAM_LAST_RAND_Y      "终点随机 Y"
    #define L10N_PARAM_LAST_RAND_ROT    "终点随机旋转"
    #define L10N_PARAM_LAST_ROT_SEED    "旋转随机种子"
    #define L10N_PARAM_LINE_SIZE        "线条大小"
    #define L10N_PARAM_LINE_MOVE        "湍流强度"
    #define L10N_PARAM_FOLD_COUNT       "湍流复杂度"
    #define L10N_PARAM_DRAW_COUNT       "绘制数量"
    #define L10N_PARAM_SUB_COUNT        "分叉支数"
    #define L10N_PARAM_COLOR            "颜色"
    #define L10N_PARAM_BLEND            "在原始图像上合成"
    #define L10N_PARAM_ON               "开"
#else
    #define L10N_PLUGIN_NAME            "F's Spark"
    #define L10N_PLUGIN_DESC            "アニメっぽい稲妻の描画"
    #define L10N_PARAM_SEED             "seed"
    #define L10N_PARAM_SEED_POS         "seedPos"
    #define L10N_PARAM_SEED_MOVE        "seedMove"
    #define L10N_PARAM_WIPE             "wipe(%)"
    #define L10N_PARAM_OFFSET           "offset"
    #define L10N_PARAM_START            "start"
    #define L10N_PARAM_LAST             "last"
    #define L10N_PARAM_START_RAND_X     "startRandX"
    #define L10N_PARAM_START_RAND_Y     "startRandY"
    #define L10N_PARAM_LAST_RAND_X      "lastRandX"
    #define L10N_PARAM_LAST_RAND_Y      "lastRandY"
    #define L10N_PARAM_LAST_RAND_ROT    "LastRandRot"
    #define L10N_PARAM_LAST_ROT_SEED    "LastRotSeed"
    #define L10N_PARAM_LINE_SIZE        "lineSize"
    #define L10N_PARAM_LINE_MOVE        "lineMove"
    #define L10N_PARAM_FOLD_COUNT       "foldCount"
    #define L10N_PARAM_DRAW_COUNT       "drawCount"
    #define L10N_PARAM_SUB_COUNT        "subCount"
    #define L10N_PARAM_COLOR            "color"
    #define L10N_PARAM_BLEND            "blend"
    #define L10N_PARAM_ON               "on"
#endif



