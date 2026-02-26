//-----------------------------------------------------------------------------------
/*
	SparkMult for VS2010
*/
//-----------------------------------------------------------------------------------

#pragma once
#ifndef SparkMult_H
#define SparkMult_H

#include "Fs_Target.h"

#include "../FsLibrary/Fs.h"
#include "../FsLibrary/FsAE.h"


#include "..\Spark\CLineDraw.h"
#include "..\Spark\CPointInfo.h"


//ユーザーインターフェースのID
//ParamsSetup関数とRender関数のparamsパラメータのIDになる
enum {
	ID_INPUT = 0,	// default input layer

	ID_SEED,
	ID_SEEDPOS,
	ID_SEEDMOVE,
	ID_OFFSET,
	ID_WIPE,

	ID_POINT_COUNT,
	ID_0_P,
	ID_1_P,
	ID_2_P,
	ID_3_P,
	ID_4_P,
	ID_5_P,
	ID_6_P,

	ID_START_RX,
	ID_START_RY,
	ID_MID_RX,
	ID_MID_RY,
	ID_LAST_RX,
	ID_LAST_RY,

	ID_LINESIZE,
	ID_LINEMOVE,
	
	ID_SUB_COUNT,
	ID_FOLD_COUNT,

	ID_DRAW_COUNT,



	ID_COLOR,
	ID_BLEND,

	ID_NUM_PARAMS
};

//UIの表示文字列
#define STR_SEED            L10N_PARAM_SEED
#define STR_SEEDPOS         L10N_PARAM_SEED_POS
#define STR_SEEDMOVE        L10N_PARAM_SEED_MOVE
#define STR_OFFSET          L10N_PARAM_OFFSET
#define STR_WIPE            L10N_PARAM_WIPE

#define STR_POINT_COUNT     L10N_PARAM_POINT_COUNT
#define STR_0_P             L10N_PARAM_POINT0
#define STR_1_P             L10N_PARAM_POINT1
#define STR_2_P             L10N_PARAM_POINT2
#define STR_3_P             L10N_PARAM_POINT3
#define STR_4_P             L10N_PARAM_POINT4
#define STR_5_P             L10N_PARAM_POINT5
#define STR_6_P             L10N_PARAM_POINT6

#define STR_START_RX        L10N_PARAM_FIRST_RAND_X
#define STR_START_RY        L10N_PARAM_FIRST_RAND_Y
#define STR_MID_RX          L10N_PARAM_MID_RAND_X
#define STR_MID_RY          L10N_PARAM_MID_RAND_Y
#define STR_LAST_RX         L10N_PARAM_LAST_RAND_X
#define STR_LAST_RY         L10N_PARAM_LAST_RAND_Y

#define STR_LINESIZE        L10N_PARAM_LINE_SIZE
#define STR_LINEMOVE        L10N_PARAM_LINE_MOVE
#define STR_FOLDCOUNT       L10N_PARAM_FOLD_COUNT
#define STR_DRAWCOUNT       L10N_PARAM_DRAW_COUNT
#define STR_SUBCOUNT        L10N_PARAM_SUB_COUNT

#define STR_COLOR           L10N_PARAM_COLOR
#define STR_BLEND           L10N_PARAM_BLEND
#define STR_ON              L10N_PARAM_ON



//-----------------------------------------------------------------------------------
typedef struct ParamInfo {
	A_long		frame;
	A_long		seed;
	A_long		seedPos;
	A_long		seedMove;
	PF_FpLong	offset;
	PF_FpLong	wipe;

	A_long		pointCount;
	PointInfo	point[7];
	A_long		randX[7];
	A_long		randY[7];

	PF_FpLong	lineSize;
	A_long		lineMove;
	A_long		foldCount;
	A_long		drawCount;
	A_long		subCount;

	PF_Pixel	color;
	PF_Boolean	blend;

} ParamInfo, * ParamInfoP, ** ParamInfoH;
//-----------------------------------------------------------------------------------
extern "C" {

DllExport 
PF_Err 
EntryPointFunc (	
	PF_Cmd			cmd,
	PF_InData		*in_data,
	PF_OutData		*out_data,
	PF_ParamDef		*params[],
	PF_LayerDef		*output,
	void			*extra);
}

#endif // SparkMult_H

