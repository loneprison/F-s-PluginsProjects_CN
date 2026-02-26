//-----------------------------------------------------------------------------------
/*
	Extract-Hi for VS2010
*/
//-----------------------------------------------------------------------------------

#pragma once
#ifndef ExtractHi_H
#define ExtractHi_H

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

#include <math.h>

#include "../FsLibrary/FsAE.h"

//ユーザーインターフェースのID
//ParamsSetup関数とRender関数のparamsパラメータのIDになる
enum {
	ID_INPUT = 0,	// default input layer

	ID_BORDER,
	ID_SOFTNESS,
	ID_TARGET,
	ID_CUSTUM_COLOR,

	ID_INVERT,

	ID_NUM_PARAMS
};

//UIの表示文字列
#define	STR_BORDER				L10N_PARAM_BORDER
#define	STR_SOFTNESS			L10N_PARAM_SOFTNESS
#define	STR_TARGET			L10N_PARAM_TARGET
#define	STR_TARGET_ITEM		L10N_PARAM_TARGET_ITEMS
#define STR_TARGET_COUNT		9
#define STR_TARGET_DFLT		1
#define	STR_CUSTUM_COLOR	L10N_PARAM_CUSTOM_COLOR
#define	STR_INVERT			L10N_PARAM_INVERT
#define	STR_INVERT_ON		L10N_PARAM_ON

//UIのパラメータ
typedef struct ParamInfo {
	PF_FpLong	hi;
	PF_FpLong	low;
	A_long		taget;
	PF_Pixel	customColor;
	PF_FpLong	r;
	PF_FpLong	g;
	PF_FpLong	b;
	PF_Boolean	invert;

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
#endif // Extract-Hi_H

