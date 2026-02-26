//-----------------------------------------------------------------------------------
/*
	ExpsPos for VS2010
*/
//-----------------------------------------------------------------------------------

#pragma once
#ifndef ExpsPos_H
#define ExpsPos_H

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
	ID_POS0,
	ID_POS1,
	ID_POS2,
	ID_POS3,
	ID_POS4,
	ID_POS5,
	ID_POS6,
	ID_POS7,
	ID_POS8,
	ID_POS9,

	ID_NUM_PARAMS
};

//UIの表示文字列
#define	STR_ON				L10N_PARAM_ON
#define	STR_ON2				L10N_PARAM_ON_VALUE
#define	STR_POS0			L10N_PARAM_POS0
#define	STR_POS1			L10N_PARAM_POS1
#define	STR_POS2			L10N_PARAM_POS2
#define	STR_POS3			L10N_PARAM_POS3
#define	STR_POS4			L10N_PARAM_POS4
#define	STR_POS5			L10N_PARAM_POS5
#define	STR_POS6			L10N_PARAM_POS6
#define	STR_POS7			L10N_PARAM_POS7
#define	STR_POS8			L10N_PARAM_POS8
#define	STR_POS9			L10N_PARAM_POS9


//UIのパラメータ
typedef struct ParamInfo {
	PF_Boolean		on;
	PF_FixedPoint	pos[10];
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
#endif // ExpsPos_H

