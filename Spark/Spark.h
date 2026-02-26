//-----------------------------------------------------------------------------------
/*
	Spark for VS2010
*/
//-----------------------------------------------------------------------------------

#pragma once
#ifndef Spark_H
#define Spark_H

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
	ID_STARTRANDX,
	ID_STARTRANDY,

	ID_LAST,
	ID_LASTRANDX,
	ID_LASTRANDY,

	ID_LASTRANDR,
	ID_LASTRANDSEED,

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
#define STR_SEED        L10N_PARAM_SEED
#define STR_SEEDPOS     L10N_PARAM_SEED_POS
#define STR_SEEDMOVE    L10N_PARAM_SEED_MOVE
#define STR_WIPE        L10N_PARAM_WIPE

#define STR_OFFSET      L10N_PARAM_OFFSET
#define STR_START       L10N_PARAM_START
#define STR_LAST        L10N_PARAM_LAST

#define STR_STARTRANDX  L10N_PARAM_START_RAND_X
#define STR_STARTRANDY  L10N_PARAM_START_RAND_Y

#define STR_LASTRANDX   L10N_PARAM_LAST_RAND_X
#define STR_LASTRANDY   L10N_PARAM_LAST_RAND_Y

#define STR_LASTRANDR   L10N_PARAM_LAST_RAND_ROT
#define STR_LASTROTSEED L10N_PARAM_LAST_ROT_SEED

#define STR_LINESIZE    L10N_PARAM_LINE_SIZE
#define STR_LINEMOVE    L10N_PARAM_LINE_MOVE
#define STR_FOLDCOUNT   L10N_PARAM_FOLD_COUNT
#define STR_DRAWCOUNT   L10N_PARAM_DRAW_COUNT
#define STR_SUBCOUNT    L10N_PARAM_SUB_COUNT

#define STR_COLOR       L10N_PARAM_COLOR
#define STR_BLEND       L10N_PARAM_BLEND
#define STR_ON          L10N_PARAM_ON



//-----------------------------------------------------------------------------------
typedef struct ParamInfo {
	PointInfo	start;
	A_long		startRandX;
	A_long		startRandY;

	PointInfo	last;
	A_long		lastRandX;
	A_long		lastRandY;

	PF_FpLong	lastRandR;
	A_long		lastRandSeed;

	PF_FpLong	lineSize;
	A_long		lineMove;
	A_long		foldCount;
	A_long		drawCount;
	A_long		subCount;

	PF_FpLong	offset;
	A_long		seed;
	A_long		seedPos;
	A_long		seedMove;
	A_long		frame;

	PF_FpLong	wipe;


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

#endif // Spark_H

