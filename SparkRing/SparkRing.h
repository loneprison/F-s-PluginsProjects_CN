//-----------------------------------------------------------------------------------
/*
	SparkRing for VS2010
*/
//-----------------------------------------------------------------------------------

#pragma once
#ifndef SparkRing_H
#define SparkRing_H

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
	ID_CENTER,
	ID_BLUR,
	ID_ASPECT,
	ID_POINT_COUNT,
	ID_POIN_ROT,
	ID_POINT_RAND,
	ID_ROT,
	ID_LINE_SIZE,
	ID_LINE_MOVE,
	ID_FOLD_COUNT,
	ID_SUB_COUNT,
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

#define STR_CENTER          L10N_PARAM_CENTER
#define STR_BLUR            L10N_PARAM_RADIUS
#define STR_ASPECT          L10N_PARAM_ASPECT

#define STR_POINT_COUNT     L10N_PARAM_POINT_COUNT
#define STR_POINT_ROT       L10N_PARAM_POINT_ROT
#define STR_POINT_ROND      L10N_PARAM_POINT_RAND

#define STR_ROT             L10N_PARAM_ROT

#define STR_LINE_SIZE       L10N_PARAM_LINE_SIZE
#define STR_LINE_MOVE       L10N_PARAM_LINE_MOVE
#define STR_FOLDCOUNT       L10N_PARAM_FOLD_COUNT
#define STR_SUBCOUNT        L10N_PARAM_SUB_COUNT
#define STR_DRAWCOUNT       L10N_PARAM_DRAW_COUNT

#define STR_COLOR           L10N_PARAM_COLOR
#define STR_BLEND           L10N_PARAM_BLEND
#define STR_ON              L10N_PARAM_ON


#define POINT_COUNT_MAX	36
//-----------------------------------------------------------------------------------
typedef struct ParamInfo {
	A_long		frame;
	A_long		seed;
	A_long		seedPos;
	A_long		seedMove;
	PF_FpLong	offset;

	A_LPoint	center;
	A_long		blur;
	PF_FpLong	aspect;
	A_long		point_count;
	PF_FpLong	point_rot;
	A_long		point_round;
	PF_FpLong	rot;

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

#endif // SparkRing_H

