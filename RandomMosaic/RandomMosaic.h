//-----------------------------------------------------------------------------------
/*
	PluginSkeleton for VS2010
*/
//-----------------------------------------------------------------------------------
#pragma once

#ifndef RandomMosaic_H
#define RandomMosaic_H


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

typedef struct ParamInfo{
	A_long		value;
	A_long		sizeMax;
	A_long		sizeMin;
	A_long		aspect;
	A_long		randomColor;
} ParamInfo;

enum {
	ID_INPUT = 0,	// default input layer 
	ID_Y,		// ノイズ量
	ID_SIZEMAX,		// モザイクの大きさ(最大値)
	ID_SIZEMIN,		// モザイクの大きさ(最小値)
	ID_ASPECT,		// モザイクの左右
	ID_RANDCOLOR,	// 色のばらつき
	ID_NUM_PARAMS
};

#define STR_Y		L10N_PARAM_AMOUNT
#define STR_SIZEMAX		L10N_PARAM_SIZE_MAX
#define STR_SIZEMIN		L10N_PARAM_SIZE_MIN
#define STR_ASPECT		L10N_PARAM_ASPECT_RANDOM
#define STR_RANDOMCOLOR	L10N_PARAM_BRIGHT_RANDOM



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

#endif // RandomMosaic
