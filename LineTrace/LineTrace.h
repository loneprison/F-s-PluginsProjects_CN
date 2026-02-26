//-----------------------------------------------------------------------------------
/*
	PluginSkeleton for VS2010
*/
//-----------------------------------------------------------------------------------

#pragma once
#ifndef LineTrace_H
#define LineTrace_H

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

//-----------------------------------------------------------------------------
//ParamsSetup用の定数
#define PR_PRM_COUNT	24
enum {
	ID_INPUT = 0,

	enabled_black,
	border_black,
	color_black,
	
	enabled_red,
	border_red,
	color_red,
	
	enabled_green,
	border_green,
	color_green,
	
	enabled_blue,
	border_blue,
	color_blue,

	enabled_yellow,
	border_yellow,
	color_yellow,

	enabled_violet,
	border_violet,
	color_violet,
	

	ID_NUM_PARAMS
};
enum{
	mode_trace=1,
	mode_simple
};
//-----------------------------------------------------------------------------
//パラメータUI用の文字列


#define UI_ENABLED_BLACK	L10N_PARAM_ENABLED_BLACK
#define UI_ENABLED_RED		L10N_PARAM_ENABLED_RED
#define UI_ENABLED_GREEN	L10N_PARAM_ENABLED_GREEN
#define UI_ENABLED_BLUE		L10N_PARAM_ENABLED_BLUE
#define UI_ENABLED_YELLOW	L10N_PARAM_ENABLED_YELLOW
#define UI_ENABLED_VIOLET	L10N_PARAM_ENABLED_VIOLET
#define UI_ENABLED2			L10N_PARAM_ENABLED_ON

#define UI_DRAW_BLACK		L10N_PARAM_DRAW_BLACK
#define UI_DRAW_RED			L10N_PARAM_DRAW_RED
#define UI_DRAW_GREEN		L10N_PARAM_DRAW_GREEN
#define UI_DRAW_BLUE		L10N_PARAM_DRAW_BLUE
#define UI_DRAW_YELLOW		L10N_PARAM_DRAW_YELLOW
#define UI_DRAW_VIOLET		L10N_PARAM_DRAW_VIOLET


#define UI_BORDER_BLACK		L10N_PARAM_BORDER_BLACK
#define UI_BORDER_RED		L10N_PARAM_BORDER_RED
#define UI_BORDER_GREEN		L10N_PARAM_BORDER_GREEN
#define UI_BORDER_BLUE		L10N_PARAM_BORDER_BLUE
#define UI_BORDER_YELLOW	L10N_PARAM_BORDER_YELLOW
#define UI_BORDER_VIOLET	L10N_PARAM_BORDER_VIOLET



#define ERR_GET_AEPRM	L10N_ERR_GET_AEPRM
#define ERR_GET_PRM		L10N_ERR_GET_PRM
//-----------------------------------------------------------------------------
#define	RANGE_RED2	330
#define	RANGE_RED3	360
#define	RANGE_RED0	0
#define	RANGE_RED1	60

#define	TARGET_YELLOW0	RANGE_RED1
#define	TARGET_YELLOW1	70

#define	TARGET_GREEN0	TARGET_YELLOW1
#define	TARGET_GREEN1	175

#define	TARGET_BLUE0	TARGET_GREEN1
#define	TARGET_BLUE1	280

#define	TARGET_VIOLET0	TARGET_BLUE1
#define	TARGET_VIOLET1	RANGE_RED2

#define TARGET_BLACK	((1L <<16) * 3 / 10) 
#define TARGET_WHITE	((1L <<16) * 9 / 10) 
#define TARGET_GRAY		((1L <<16) * 5 / 10) 
typedef struct
{
	PF_Boolean	enabled;
	PF_Fixed	border;
	PF_Pixel	color;
} TracePrm;

enum
{
	LT_BLACK=0,
	LT_RED,
	LT_GREEN,
	LT_BLUE,
	LT_YELLOW,
	LT_VIOLET,
	LT_COUNT
};
enum
{
	HLS_H =0,
	HLS_L,
	HLS_S,
};
typedef struct
{
	PF_Boolean	enabled;
	PF_Fixed	border;
	PF_Pixel	color;
} TracePrm8;
typedef struct
{
	PF_Boolean	enabled;
	PF_Fixed	border;
	PF_Pixel16	color;
} TracePrm16;
typedef struct
{
	PF_Boolean	enabled;
	PF_Fixed	border;
	PF_PixelFloat	color;
} TracePrm32;
typedef struct
{
	TracePrm8	ParamTable[LT_COUNT];
} ParamInfo;
typedef struct
{
	TracePrm8	ParamTable[LT_COUNT];
	PF_ColorCallbacksSuite1		*cs;
	PF_ProgPtr			effect_ref;
	PF_InData			*in_data;
} ParamInfo8;
typedef struct
{
	TracePrm16	ParamTable[LT_COUNT];
	PF_ColorCallbacks16Suite1		*cs;
	PF_ProgPtr			effect_ref;
} ParamInfo16;
typedef struct
{
	TracePrm32	ParamTable[LT_COUNT];
	PF_ColorCallbacksFloatSuite1	*cs;
	PF_ProgPtr			effect_ref;
} ParamInfo32;

//-----------------------------------------------------------------------------
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
//-----------------------------------------------------------------------------

#endif // LineTrace_H

