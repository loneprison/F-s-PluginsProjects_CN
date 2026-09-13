//-----------------------------------------------------------------------------------
/*
	NamiGarasu for VS2010
*/
//-----------------------------------------------------------------------------------

#pragma once
#ifndef NamiGarasu_H
#define NamiGarasu_H

#include "Fs_Target.h"

#include "AEConfig.h"
#include "entry.h"

//#include "PrSDKAESupport.h"
#include "AE_Effect.h"
#include "AE_EffectCB.h"
#include "AE_EffectCBSuites.h"
#include "AE_Macros.h"
#include "AEGP_SuiteHandler.h"
#include "String_Utils.h"
#include "Param_Utils.h"
#include "Smart_Utils.h"

#if defined(PF_AE100_PLUG_IN_VERSION)
	#include "AEFX_SuiteHelper.h"
	#define refconType void*
#else
	#include "PF_Suite_Helper.h"
	#define refconType A_long
#endif

#ifdef AE_OS_WIN
	#include <Windows.h>
#endif

#include "../FsLibrary/FsAE.h"

//ユーザーインターフェースのID
//ParamsSetup関数とRender関数のparamsパラメータのIDになる
enum {
	ID_INPUT = 0,	// default input layer
	
	ID_VALE,

	ID_ROT,
	ID_SPEED,

	ID_LEVEL,
	ID_NOISE,

	ID_TOPIC_A,
	ID_A_SIZE,
	ID_A_VALUE,
	ID_A_STRONG,
	ID_A_SPEED,
	ID_A_SEED,
	ID_TOPIC_A_END,

	ID_TOPIC_B,
	ID_B_SIZE,
	ID_B_VALUE,
	ID_B_STRONG,
	ID_B_SPEED,
	ID_B_SEED,
	ID_TOPIC_B_END,

	ID_TOPIC_C,
	ID_C_SIZE,
	ID_C_VALUE,
	ID_C_STRONG,
	ID_C_SPEED,
	ID_C_SEED,
	ID_TOPIC_C_END,

	ID_DISPMAP,
	ID_LENGTH_X,
	ID_LENGTH_Y,

	ID_NUM_PARAMS
};

//UIの表示文字列
#define	L10N_PARAM_WAVE_VALUE			"WaveValue"
#define	L10N_PARAM_X_LENGTH		"X_Length"
#define	L10N_PARAM_Y_LENGTH		"Y_Length"
#define	L10N_PARAM_ROT				"Rot"
#define	L10N_PARAM_SPEED			"Speed"
#define	L10N_PARAM_ADD_MAP			"AddMap"
#define	L10N_PARAM_NOISE			"Noise"

#define	L10N_PARAM_LAYER_A				"LayerA"
#define	L10N_PARAM_A_SIZE			"A_size"
#define	L10N_PARAM_A_VALUE			"A_value"
#define	L10N_PARAM_A_STRONG		"A_Strong"
#define	L10N_PARAM_A_SPEED			"A_Speed"
#define	L10N_PARAM_A_SEED			"A_Seed"

#define	L10N_PARAM_LAYER_B				"LayerB"
#define	L10N_PARAM_B_SIZE			"B_size"
#define	L10N_PARAM_B_VALUE			"B_value"
#define	L10N_PARAM_B_STRONG		"B_Strong"
#define	L10N_PARAM_B_SPEED			"B_Speed"
#define	L10N_PARAM_B_SEED			"B_Seed"

#define	L10N_PARAM_LAYER_C				"LayerC"
#define	L10N_PARAM_C_SIZE			"C_size"
#define	L10N_PARAM_C_VALUE			"C_value"
#define	L10N_PARAM_C_STRONG		"C_Strong"
#define	L10N_PARAM_C_SPEED			"C_Speed"
#define	L10N_PARAM_C_SEED			"C_Seed"

#define	L10N_PARAM_DISP_MAP			"DispMap"
#define	L10N_PARAM_ON				"on"

#define	STR_POINT			"point"

//UIのパラメータ
typedef struct ScrInfo {
	PF_PixelPtr data;
	A_long	width;
	A_long	widthTrue;
	A_long	height;
}ScrInfo;

typedef struct MapInfo {
	A_long		size;
	A_long		value;
	PF_FpLong	strong;
	PF_FpLong	speed;
	A_long		seed;
	PF_Fixed	shift_x;
	PF_Fixed	shift_y;
}MapInfo;

typedef struct ParamInfo {
	PF_Fixed	lengthX;
	PF_Fixed	lengthY;
	PF_Fixed	rot;
	PF_Fixed	speed;
	double		level;
	double		noise;

	MapInfo		map[3];

	PF_Boolean	disp_map;
	//PF_FixedPoint	point;

} ParamInfo, *ParamInfoP, **ParamInfoH;


#define PF_HALF_CHAN32 0.5

typedef struct DrawInfo{
	ScrInfo scr;
	A_long	x;
	A_long	y;
	A_long	sizeIdx;
	A_long	isW;
	double	strong;
	A_long	scale;
} DrawInfo;

void drawSq8(DrawInfo *infoP);
void drawSq16(DrawInfo *infoP);
void drawSq32(DrawInfo *infoP);

typedef struct ShiftInfo{
	ScrInfo scr;
	PF_Fixed	shift_x;
	PF_Fixed	shift_y;
	double		level;
} ShiftInfo;

PF_Err 
shiftRed8 (
	refconType	refcon, 
	A_long		xL, 
	A_long		yL, 
	PF_Pixel	*inP, 
	PF_Pixel	*outP);
PF_Err 
shiftRed16 (
	refconType	refcon, 
	A_long		xL, 
	A_long		yL, 
	PF_Pixel16	*inP, 
	PF_Pixel16	*outP);

PF_Err 
shiftRed32 (
	refconType	refcon, 
	A_long		xL, 
	A_long		yL, 
	PF_PixelFloat	*inP, 
	PF_PixelFloat	*outP);

PF_Err 
imageMap8 (
	refconType	refcon, 
	A_long		xL, 
	A_long		yL, 
	PF_Pixel	*inP, 
	PF_Pixel	*outP);
PF_Err 
imageMap16 (
	refconType	refcon, 
	A_long		xL, 
	A_long		yL, 
	PF_Pixel16	*inP, 
	PF_Pixel16	*outP);
PF_Err 
imageMap32 (
	refconType	refcon, 
	A_long		xL, 
	A_long		yL, 
	PF_PixelFloat	*inP, 
	PF_PixelFloat	*outP);

//-------------------------------------------------------
void AlphaBlur8(CFsGraph *g);
void AlphaBlur16(CFsGraph *g);
void AlphaBlur32(CFsGraph *g);


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
#endif // NamiGarasu_H

