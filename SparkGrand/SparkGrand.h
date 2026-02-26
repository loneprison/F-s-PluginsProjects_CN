//-----------------------------------------------------------------------------------
/*
	SparkGrand for VS2010
*/
//-----------------------------------------------------------------------------------

#pragma once
#ifndef SparkGrand_H
#define SparkGrand_H

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

	ID_START,
	ID_LAST1,
	ID_LAST2,

	ID_DRAW_COUNT,

	ID_START_RX,
	ID_START_RY,

	ID_LAST_RX,
	ID_LAST_RY,


	ID_LINE_SIZE,
	ID_LINE_MOVE,
	ID_FOLD_COUNT,
	ID_COLOR,
	ID_BLEND,

	ID_NUM_PARAMS
};



//UIの表示文字列
#define STR_SEED        L10N_PARAM_SEED
#define STR_SEEDPOS     L10N_PARAM_SEED_POS
#define STR_SEEDMOVE    L10N_PARAM_SEED_MOVE
#define STR_OFFSET      L10N_PARAM_OFFSET
#define STR_WIPE        L10N_PARAM_WIPE

#define STR_START       L10N_PARAM_START
#define STR_LAST1       L10N_PARAM_LAST1
#define STR_LAST2       L10N_PARAM_LAST2

#define STR_START_RX    L10N_PARAM_START_RAND_X
#define STR_START_RY    L10N_PARAM_START_RAND_Y
#define STR_LAST_RX     L10N_PARAM_LAST_RAND_X
#define STR_LAST_RY     L10N_PARAM_LAST_RAND_Y

#define STR_LINE_SIZE   L10N_PARAM_LINE_SIZE
#define STR_LINE_MOVE   L10N_PARAM_LINE_MOVE
#define STR_FOLDCOUNT   L10N_PARAM_FOLD_COUNT
#define STR_SUBCOUNT    L10N_PARAM_SUB_COUNT
#define STR_DRAWCOUNT   L10N_PARAM_DRAW_COUNT

#define STR_COLOR       L10N_PARAM_COLOR
#define STR_BLEND       L10N_PARAM_BLEND
#define STR_ON          L10N_PARAM_ON


#define POINT_COUNT_MAX	36
//-----------------------------------------------------------------------------------
typedef struct ParamInfo {
	A_long		frame;
	A_long		seed;
	A_long		seedPos;
	A_long		seedMove;
	PF_FpLong	offset;
	PF_FpLong	wipe;

	PointInfo	start;
	PointInfo	last1;
	PointInfo	last2;

	A_long		startRandX;
	A_long		startRandY;
	A_long		lastRandX;
	A_long		lastRandY;


	PF_FpLong	lineSize;
	A_long		lineMove;
	A_long		foldCount;
	A_long		drawCount;


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

#endif // SparkGrand_H

