//-----------------------------------------------------------------------------------
/*
	Thin for VS2010
*/
//-----------------------------------------------------------------------------------

#pragma once
#ifndef Thin_H
#define Thin_H

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
#include "../FsLibrary/FsDebug.h"

//ユーザーインターフェースのID
//ParamsSetup関数とRender関数のparamsパラメータのIDになる
enum {
	ID_INPUT = 0,	// default input layer

	ID_Y,

	ID_COLOR1_ON,
	ID_COLOR1,
	ID_COLOR2_ON,
	ID_COLOR2,
	ID_COLOR3_ON,
	ID_COLOR3,
	ID_COLOR4_ON,
	ID_COLOR4,
	ID_LEVEL,

	ID_WHITE,
	ID_ALPHAZERO,
	ID_EDGE,

	ID_NUM_PARAMS
};

//UIの表示文字列
#define	L10N_PARAM_THIN_VALUE			"ThinValue"
#define	L10N_PARAM_ON				"on"
#define	L10N_PARAM_ENABLED_COLOR1		"EnabledColor1"
#define	L10N_PARAM_ENABLED_COLOR2		"EnabledColor2"
#define	L10N_PARAM_ENABLED_COLOR3		"EnabledColor3"
#define	L10N_PARAM_ENABLED_COLOR4		"EnabledColor4"

#define	L10N_PARAM_COLOR1			"Color1"
#define	L10N_PARAM_COLOR2			"Color2"
#define	L10N_PARAM_COLOR3			"Color3"
#define	L10N_PARAM_COLOR4			"Color4"

#define	L10N_PARAM_NO_WHITE			"NoWhite"
#define	L10N_PARAM_NO_ALPHA_ZERO		"NoAlphaZero"
#define	L10N_PARAM_EDGE_FILTER		"EdgeFilter"

#define	L10N_PARAM_LEVEL			"level"

#define COLOR_MAX	4
//UIのパラメータ
typedef struct ParamInfo {
	A_long		value;
	A_long		colorMax;
	PF_Pixel	color[COLOR_MAX];
	
	PF_Boolean	white;
	PF_Boolean	alphaZero;
	PF_Boolean	edge;

	PF_FpLong	level;
} ParamInfo, *ParamInfoP, **ParamInfoH;

//-------------------------------------------------------
typedef struct thinInfo8 {
	A_long		w;
	A_long		wt;
	A_long		wt2;
	A_long		h;
	A_long		offset;
	PF_Handle	scanlineH;
	PF_Pixel	*scanline;
	PF_Pixel	*data;

	PF_Boolean	white;
	PF_Boolean	alphaZero;
	PF_Boolean	edge;

	A_long		colorMax;
	PF_Pixel	color[COLOR_MAX];
	A_long	level;
	A_long		nowX;
	A_long		nowY;

} thinInfo8;
typedef struct thinBak8 {
	PF_Boolean	drawFlag;
	PF_Pixel	color;
	A_long		dir;
} thinBak8;

typedef struct thinInfo16 {
	A_long		w;
	A_long		wt;
	A_long		wt2;
	A_long		h;
	A_long		offset;
	PF_Handle	scanlineH;
	PF_Pixel16	*scanline;
	PF_Pixel16	*data;

	PF_Boolean	white;
	PF_Boolean	alphaZero;
	PF_Boolean	edge;

	A_long		colorMax;
	PF_Pixel16	color[COLOR_MAX];
	PF_Pixel	color8[COLOR_MAX];
	A_long		level;
	A_long		nowX;
	A_long		nowY;

} thinInfo16;

typedef struct thinBak16 {
	PF_Boolean	drawFlag;
	PF_Pixel16	color;
	A_long		dir;
} thinBak16;

typedef struct thinInfo32 {
	A_long		w;
	A_long		wt;
	A_long		wt2;
	A_long		h;
	A_long		offset;
	PF_Handle	scanlineH;
	PF_PixelFloat	*scanline;
	PF_PixelFloat	*data;

	PF_Boolean	white;
	PF_Boolean	alphaZero;
	PF_Boolean	edge;

	A_long		colorMax;
	PF_PixelFloat	color[COLOR_MAX];
	PF_Pixel		color8[COLOR_MAX];
	A_long		level;
	A_long		nowX;
	A_long		nowY;

} thinInfo32;
typedef struct thinBak32 {
	PF_Boolean	drawFlag;
	PF_PixelFloat	color;
	A_long		dir;
} thinBak32;

//--------------------------------------------------------------------xFF--------------
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


PF_Err thinExec8(CFsAE *ae , ParamInfo *infoP);
PF_Err thinExec16(CFsAE *ae , ParamInfo *infoP);
PF_Err thinExec32(CFsAE *ae , ParamInfo *infoP);
#endif // Thin_H

