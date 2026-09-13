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
#define	L10N_PARAM_SEED		"seed"
#define	L10N_PARAM_SEED_POS		"seedPos"
#define	L10N_PARAM_SEED_MOVE	"seedMove"
#define	L10N_PARAM_OFFSET		"offset"
#define	L10N_PARAM_WIPE		"wipe(%)"

#define	L10N_PARAM_POINT_COUNT	"pointCount"
#define	L10N_PARAM_POINT0			"point0"
#define	L10N_PARAM_POINT1			"point1"
#define	L10N_PARAM_POINT2			"point2"
#define	L10N_PARAM_POINT3			"point3"
#define	L10N_PARAM_POINT4			"point4"
#define	L10N_PARAM_POINT5			"point5"
#define	L10N_PARAM_POINT6			"point6"

#define	L10N_PARAM_FIRST_RAND_X	"first_randX"
#define	L10N_PARAM_FIRST_RAND_Y	"first_randY"
#define	L10N_PARAM_MID_RAND_X		"mid_randX"
#define	L10N_PARAM_MID_RAND_Y		"mid_randY"
#define	L10N_PARAM_LAST_RAND_X		"last_randX"
#define	L10N_PARAM_LAST_RAND_Y		"last_randY"

#define	L10N_PARAM_LINE_SIZE	"lineSize"
#define	L10N_PARAM_LINE_MOVE	"lineMove"
#define	L10N_PARAM_FOLD_COUNT	"foldCount"
#define	L10N_PARAM_DRAW_COUNT	"drawCount"
#define	L10N_PARAM_SUB_COUNT	"subCount"




#define	L10N_PARAM_COLOR		"color"
#define	L10N_PARAM_BLEND		"blend"
#define	L10N_PARAM_ON			"on"



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

