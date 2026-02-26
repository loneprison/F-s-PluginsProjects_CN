#pragma once

/*
 * Localization switch for SparkRing.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
    #define L10N_PLUGIN_NAME            "F's SparkRing"
    #define L10N_PLUGIN_DESC            "绘制动画风格闪电"
    #define L10N_PARAM_SEED             "全局随机种子"
    #define L10N_PARAM_SEED_POS         "位置随机种子"
    #define L10N_PARAM_SEED_MOVE        "形态随机种子"
    #define L10N_PARAM_OFFSET           "偏移"
    #define L10N_PARAM_CENTER           "中心"
    #define L10N_PARAM_RADIUS           "半径"
    #define L10N_PARAM_ASPECT           "长宽比"
    #define L10N_PARAM_POINT_COUNT      "点数量"
    #define L10N_PARAM_POINT_ROT        "点旋转"
    #define L10N_PARAM_POINT_RAND       "点随机"
    #define L10N_PARAM_ROT              "旋转"
    #define L10N_PARAM_LINE_SIZE        "线条大小"
    #define L10N_PARAM_LINE_MOVE        "湍流强度"
    #define L10N_PARAM_FOLD_COUNT       "湍流复杂度"
    #define L10N_PARAM_SUB_COUNT        "分叉支数"
    #define L10N_PARAM_DRAW_COUNT       "绘制数量"
    #define L10N_PARAM_COLOR            "颜色"
    #define L10N_PARAM_BLEND            "在原始图像上合成"
    #define L10N_PARAM_ON               "开"
#else
    #define L10N_PLUGIN_NAME            "F's SparkRing"
    #define L10N_PLUGIN_DESC            "アニメっぽい稲妻の描画"
    #define L10N_PARAM_SEED             "seed"
    #define L10N_PARAM_SEED_POS         "seedPos"
    #define L10N_PARAM_SEED_MOVE        "seedMove"
    #define L10N_PARAM_OFFSET           "offset"
    #define L10N_PARAM_CENTER           "center"
    #define L10N_PARAM_RADIUS           "radius"
    #define L10N_PARAM_ASPECT           "aspect"
    #define L10N_PARAM_POINT_COUNT      "point_count"
    #define L10N_PARAM_POINT_ROT        "point_rot"
    #define L10N_PARAM_POINT_RAND       "point_rand"
    #define L10N_PARAM_ROT              "rot"
    #define L10N_PARAM_LINE_SIZE        "lineSize"
    #define L10N_PARAM_LINE_MOVE        "lineMove"
    #define L10N_PARAM_FOLD_COUNT       "foldCount"
    #define L10N_PARAM_SUB_COUNT        "subCount"
    #define L10N_PARAM_DRAW_COUNT       "drawCount"
    #define L10N_PARAM_COLOR            "color"
    #define L10N_PARAM_BLEND            "blend"
    #define L10N_PARAM_ON               "on"
#endif



