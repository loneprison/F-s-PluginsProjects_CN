#pragma once

/*
 * Localization switch for SparkMult.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's SparkMult"
    #define L10N_PLUGIN_DESC            "绘制动画风格闪电，5点版"
    #define L10N_PARAM_SEED             "全局随机种子"
    #define L10N_PARAM_SEED_POS         "位置随机种子"
    #define L10N_PARAM_SEED_MOVE        "形态随机种子"
    #define L10N_PARAM_OFFSET           "偏移"
    #define L10N_PARAM_WIPE             "擦除 (%)"
    #define L10N_PARAM_POINT_COUNT      "点数量"
    #define L10N_PARAM_POINT0           "点0"
    #define L10N_PARAM_POINT1           "点1"
    #define L10N_PARAM_POINT2           "点2"
    #define L10N_PARAM_POINT3           "点3"
    #define L10N_PARAM_POINT4           "点4"
    #define L10N_PARAM_POINT5           "点5"
    #define L10N_PARAM_POINT6           "点6"
    #define L10N_PARAM_FIRST_RAND_X     "起点随机 X"
    #define L10N_PARAM_FIRST_RAND_Y     "起点随机 Y"
    #define L10N_PARAM_MID_RAND_X       "中间点随机 X"
    #define L10N_PARAM_MID_RAND_Y       "中间点随机 Y"
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
    #define L10N_PLUGIN_NAME            "F's SparkMult"
    #define L10N_PLUGIN_DESC            "アニメっぽい稲妻の描画、5ポイント"
    #define L10N_PARAM_SEED             "seed"
    #define L10N_PARAM_SEED_POS         "seedPos"
    #define L10N_PARAM_SEED_MOVE        "seedMove"
    #define L10N_PARAM_OFFSET           "offset"
    #define L10N_PARAM_WIPE             "wipe(%)"
    #define L10N_PARAM_POINT_COUNT      "pointCount"
    #define L10N_PARAM_POINT0           "point0"
    #define L10N_PARAM_POINT1           "point1"
    #define L10N_PARAM_POINT2           "point2"
    #define L10N_PARAM_POINT3           "point3"
    #define L10N_PARAM_POINT4           "point4"
    #define L10N_PARAM_POINT5           "point5"
    #define L10N_PARAM_POINT6           "point6"
    #define L10N_PARAM_FIRST_RAND_X     "first_randX"
    #define L10N_PARAM_FIRST_RAND_Y     "first_randY"
    #define L10N_PARAM_MID_RAND_X       "mid_randX"
    #define L10N_PARAM_MID_RAND_Y       "mid_randY"
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



