//-----------------------------------------------------------------------------------
/*
	PixelExtend for VS2010
*/
//-----------------------------------------------------------------------------------

#pragma once
#ifndef PixelExtend_H
#define PixelExtend_H

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


enum
{
	LEN_TOP =0,
	LEN_TOP_RIGHT,
	LEN_RIGHT,
	LEN_BOTTOM_RIGHT,
	LEN_BOTTOM,
	LEN_BOTTOM_LEFT,
	LEN_LEFT,
	LEN_TOP_LEFT,
	LEN_COUNT
};
#define EXPAND_MAX 8
//ユーザーインターフェースのID
//ParamsSetup関数とRender関数のparamsパラメータのIDになる
enum {
	ID_INPUT = 0,	// default input layer


	ID_TARGET_TOPIC,
	ID_RANGE,
	ID_TARGET_COLOR0_ENABLED,
	ID_TARGET_COLOR0,
	ID_TARGET_COLOR1_ENABLED,
	ID_TARGET_COLOR1,
	ID_TARGET_COLOR2_ENABLED,
	ID_TARGET_COLOR2,
	ID_TARGET_COLOR3_ENABLED,
	ID_TARGET_COLOR3,
	ID_TARGET_COLOR4_ENABLED,
	ID_TARGET_COLOR4,
	ID_TARGET_COLOR5_ENABLED,
	ID_TARGET_COLOR5,
	ID_TARGET_COLOR6_ENABLED,
	ID_TARGET_COLOR6,
	ID_TARGET_COLOR7_ENABLED,
	ID_TARGET_COLOR7,
	ID_TARGET_TOPIC_END,

	ID_DIR_TOPIC,
	ID_TOP,
	ID_TOP_RIGHT,
	ID_RIGHT,
	ID_BOTTOM_RIGHT,
	ID_BOTTOM,
	ID_BOTTOM_LEFT,
	ID_LEFT,
	ID_TOP_LEFT,
	ID_DIR_TOPIC_END,

	ID_NONE_TOPIC,
	ID_NONE_COLOR0_ENABLED,
	ID_NONE_COLOR0,
	ID_NONE_COLOR1_ENABLED,
	ID_NONE_COLOR1,
	ID_NONE_COLOR2_ENABLED,
	ID_NONE_COLOR2,
	ID_NONE_COLOR3_ENABLED,
	ID_NONE_COLOR3,
	ID_NONE_COLOR4_ENABLED,
	ID_NONE_COLOR4,
	ID_NONE_COLOR5_ENABLED,
	ID_NONE_COLOR5,
	ID_NONE_COLOR6_ENABLED,
	ID_NONE_COLOR6,
	ID_NONE_COLOR8_ENABLED,
	ID_NONE_COLOR8,
	ID_NONE_TOPIC_END,


	ID_TARGET_ONLY,

	ID_NUM_PARAMS
};

//UIの表示文字列
#define L10N_PARAM_TARGET_TOPIC			"Target"
#define L10N_PARAM_RANGE					"Range"
#define L10N_PARAM_ON						"on"
#define L10N_PARAM_TARGET_COLOR_EN		"TargetColorEnabled"
#define L10N_PARAM_TARGET_COLOR			"TargetColor"
#define L10N_PARAM_EXTEND_TOPIC			"Extend"
#define L10N_PARAM_TOP						"Top"
#define L10N_PARAM_TOP_RIGHT				"Top_Right"
#define L10N_PARAM_RIGHT					"Right"
#define L10N_PARAM_BOTTOM_RIGHT			"Bottom_Right"
#define L10N_PARAM_BOTTOM					"Bottom"
#define L10N_PARAM_BOTTOM_LEFT				"Bottom_Left"
#define L10N_PARAM_LEFT						"Left"
#define L10N_PARAM_TOP_LEFT				"Top_Left"
#define L10N_PARAM_NODRAW_TOPIC			"NoDraw"
#define L10N_PARAM_NODRAW_COLOR_EN		"NoneColorEnabled"
#define L10N_PARAM_NODRAW_COLOR			"NoneColor"
#define L10N_PARAM_TARGET_ONLY				"TargetOnly"

//UIのパラメータ
typedef struct ParamInfo {
	A_long		colTableCount;
	PF_Pixel	colTable[EXPAND_MAX];
	PF_Pixel16	colTable16[EXPAND_MAX];
	PF_PixelFloat	colTable32[EXPAND_MAX];
	A_long		lenTable[LEN_COUNT];

	A_u_char	range8;
	A_u_short	range16;
	PF_FpShort	range32;

	A_long		ncolTableCount;
	PF_Pixel	ncolTable[EXPAND_MAX];
	PF_Pixel16	ncolTable16[EXPAND_MAX];
	PF_PixelFloat	ncolTable32[EXPAND_MAX];


	A_long		lineWidth;
	A_long		widthTrue;
	A_long		height;
	PF_Boolean	IsTargetOnly;
} ParamInfo, *ParamInfoP, **ParamInfoH;
//-------------------------------------------------------


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
#endif // PixelExtend_H

