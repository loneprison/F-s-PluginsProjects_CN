//-----------------------------------------------------------------------------------
/*
	graytoneToColorize for VS2010
*/
//-----------------------------------------------------------------------------------

#pragma once
#ifndef graytoneToColorize_H
#define graytoneToColorize_H

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
//#include "FsAE.h"



//ユーザーインターフェースのID
//ParamsSetup関数とRender関数のparamsパラメータのIDになる
enum {
	ID_INPUT = 0,	// default input layer
	
	ID_TARGET,

	ID_COL0,

	ID_COL1,
	
	ID_COL2,
	
	ID_COL3,
	
	ID_COL4,

	ID_COL5,

	ID_COL6,

	ID_COL7,

	ID_COL8,

	ID_REP,
	ID_OFFSET_ON,
	ID_OFFSET,
	ID_OFFSET_SPEED,


	ID_NUM_PARAMS
};

//UIの表示文字列
#define	STR_TARGET		L10N_PARAM_TARGET
#define	STR_TARGET_ITEMS		L10N_PARAM_TARGET_ITEMS
#define	STR_TARGET_COUNT		5
#define	STR_TARGET_DEFLT		1

#define	STR_COL0		L10N_PARAM_COLOR0
#define	STR_COL1		L10N_PARAM_COLOR1
#define	STR_COL2		L10N_PARAM_COLOR2
#define	STR_COL3		L10N_PARAM_COLOR3
#define	STR_COL4		L10N_PARAM_COLOR4
#define	STR_COL5		L10N_PARAM_COLOR5
#define	STR_COL6		L10N_PARAM_COLOR6
#define	STR_COL7		L10N_PARAM_COLOR7
#define	STR_COL8		L10N_PARAM_COLOR8

#define	STR_OFFSET		L10N_PARAM_OFFSET
#define	STR_OFFSET_ON	L10N_PARAM_OFFSET_ENABLED
#define STR_ON          L10N_PARAM_ON
#define	STR_OFFSET_SPEED	L10N_PARAM_OFFSET_SPEED

#define	STR_REP			L10N_PARAM_REPEAT

//UIのパラメータ
#define COL_COUNT 9
typedef struct ParamInfo {
	A_long		target;
	double	offset;
	double	offset_speed;
	double	offset_rep;
	PF_Boolean offset_enabled;
	PF_Pixel	col[COL_COUNT];
	A_long		colBorder[COL_COUNT];
	A_long	frame;

} ParamInfo, *ParamInfoP, **ParamInfoH;
typedef struct ParamInfo16 {
	A_long		target;
	double	offset;
	double	offset_speed;
	double	offset_rep;
	PF_Boolean offset_enabled;
	PF_Pixel16	col[COL_COUNT];
	A_long		colBorder[COL_COUNT];
	A_long	frame;

} ParamInfo16, *ParamInfo16P, **ParamInfo16H;
typedef struct ParamInfo32 {
	A_long		target;
	double		offset;
	double	offset_speed;
	double	offset_rep;
	PF_Boolean offset_enabled;
	PF_PixelFloat	col[COL_COUNT];
	A_long		colBorder[COL_COUNT];
	A_long	frame;

} ParamInfo32, *ParamInfo32P, **ParamInfo32H;

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
#endif // graytoneToColorize_H

