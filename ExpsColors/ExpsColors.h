//-----------------------------------------------------------------------------------
/*
	ExpsColors for VS2010
*/
//-----------------------------------------------------------------------------------

#pragma once
#ifndef ExpsColors_H
#define ExpsColors_H

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

	ID_ON,
	ID_COLOR0,
	ID_COLOR1,
	ID_COLOR2,
	ID_COLOR3,
	ID_COLOR4,
	ID_COLOR5,
	ID_COLOR6,
	ID_COLOR7,
	ID_COLOR8,
	ID_COLOR9,

	ID_NUM_PARAMS
};

//UIの表示文字列
#define	L10N_PARAM_ON				"ON"
#define	L10N_PARAM_ON_VALUE				"on"
#define	STR_COLOR			"color"
#define	L10N_PARAM_COLOR0			"color0"
#define	L10N_PARAM_COLOR1			"color1"
#define	L10N_PARAM_COLOR2			"color2"
#define	L10N_PARAM_COLOR3			"color3"
#define	L10N_PARAM_COLOR4			"color4"
#define	L10N_PARAM_COLOR5			"color5"
#define	L10N_PARAM_COLOR6			"color6"
#define	L10N_PARAM_COLOR7			"color7"
#define	L10N_PARAM_COLOR8			"color8"
#define	L10N_PARAM_COLOR9			"color9"


//UIのパラメータ
typedef struct ParamInfo {
	PF_Boolean		on;
	PF_Pixel		col[10];
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
#endif // ExpsColors_H

