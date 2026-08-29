//-----------------------------------------------------------------------------------
/*
	F's Plugins for VS2010/VS2012
*/
//-----------------------------------------------------------------------------------
#pragma once
#ifndef ChannelNoise_H
#define ChannelNoise_H

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

	
#define	L10N_PARAM_RED_NOISE		"Red Noise(%)"
#define	L10N_PARAM_RED_OPACITY			"Red Opacity(%)"
#define	L10N_PARAM_GREEN_NOISE		"Green Noise(%)"
#define	L10N_PARAM_GREEN_OPACITY		"Green Opacity(%)"
#define	L10N_PARAM_BLUE_NOISE		"Blue Noise(%)"
#define	L10N_PARAM_BLUE_OPACITY		"Blue Opacity(%)"
	

//ユーザーインターフェースのID
//ParamsSetup関数とRender関数のparamsパラメータのIDになる
enum {
	ID_INPUT = 0,	// default input layer 
	
	ID_RED_NOISE,	//
	ID_RED_OPT,	//
	ID_GREEN_NOISE,	//
	ID_GREEN_OPT,	//
	ID_BLUE_NOISE,	//
	ID_BLUE_OPT,	//

	ID_NUM_PARAMS
	};
	
typedef struct ParamInfo{
	A_long				red_add;
	A_long				green_add;
	A_long				blue_add;
	PF_FpShort			red_value;
	PF_FpShort			green_value;
	PF_FpShort			blue_value;
	PF_FpShort			red_opt;
	PF_FpShort			green_opt;
	PF_FpShort			blue_opt;
} ParamInfo,*ParamInfoP,**ParamInfoH;

//-------------------------------------------------------
extern "C" {
DllExport	
PF_Err 
EntryPointFunc (
	PF_Cmd			cmd,
	PF_InData		*in_data,
	PF_OutData		*out_data,
	PF_ParamDef		*params[],
	PF_LayerDef		*output,
	void			*extraP);
}

#endif // ChannelNoise_H

