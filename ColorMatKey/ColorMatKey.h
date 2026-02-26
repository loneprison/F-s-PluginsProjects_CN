//-----------------------------------------------------------------------------------
/*
	ColorMatKey for VS2010
*/
//-----------------------------------------------------------------------------------

#pragma once
#ifndef ColorMatKey_H
#define ColorMatKey_H


#include <math.h>

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
#include "../FsLibrary/FsHLS.h"

//ユーザーインターフェースのID
//ParamsSetup関数とRender関数のparamsパラメータのIDになる
enum {
	ID_INPUT = 0,	// default input layer

	ID_REV,


	ID_TARGET_ENABLE0,
	ID_TARGET_COLOR0,
	ID_TAGET_BORDER0,
	ID_TAGET_SOFT0,

	ID_TARGET_ENABLE1,
	ID_TARGET_COLOR1,
	ID_TAGET_BORDER1,
	ID_TAGET_SOFT1,

	ID_TARGET_ENABLE2,
	ID_TARGET_COLOR2,
	ID_TAGET_BORDER2,
	ID_TAGET_SOFT2,

	ID_TARGET_ENABLE3,
	ID_TARGET_COLOR3,
	ID_TAGET_BORDER3,
	ID_TAGET_SOFT3,

	ID_NUM_PARAMS
};

//UIの表示文字列
#define	STR_ALPHA_REV			L10N_PARAM_INVERT_ALPHA

#define	STR_ON					L10N_PARAM_ON
#define	STR_TARGET_ENABLED0		L10N_PARAM_ENABLED0
#define	STR_TARGET_COLOR0		L10N_PARAM_COLOR0
#define	STR_TAGET_BORDER0		L10N_PARAM_BORDER0
#define	STR_TAGET_SOFT0			L10N_PARAM_SOFTNESS0

#define	STR_TARGET_ENABLED1		L10N_PARAM_ENABLED1
#define	STR_TARGET_COLOR1		L10N_PARAM_COLOR1
#define	STR_TAGET_BORDER1		L10N_PARAM_BORDER1
#define	STR_TAGET_SOFT1			L10N_PARAM_SOFTNESS1

#define	STR_TARGET_ENABLED2		L10N_PARAM_ENABLED2
#define	STR_TARGET_COLOR2		L10N_PARAM_COLOR2
#define	STR_TAGET_BORDER2		L10N_PARAM_BORDER2
#define	STR_TAGET_SOFT2			L10N_PARAM_SOFTNESS2

#define	STR_TARGET_ENABLED3		L10N_PARAM_ENABLED3
#define	STR_TARGET_COLOR3		L10N_PARAM_COLOR3
#define	STR_TAGET_BORDER3		L10N_PARAM_BORDER3
#define	STR_TAGET_SOFT3			L10N_PARAM_SOFTNESS3


//UIのパラメータ
typedef struct CInfo {
	PF_Boolean	target_enabled;
	PF_FpLong	target_border;
	PF_FpLong	target_softness;
	PF_FpLong	target_start;
	LABA		target_lab;


} CInfo, *CInfoP, **CInfoH;


typedef struct ParamInfo {
	CInfo		ci[4];
	PF_Boolean	rev;
	PF_InData	*in_data;


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
#endif // ColorMatKey_H

