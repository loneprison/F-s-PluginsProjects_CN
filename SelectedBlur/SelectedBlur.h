//-----------------------------------------------------------------------------------
/*
	F's Plugins for VS2010/VS2012

*/
//-----------------------------------------------------------------------------------

#pragma once
#ifndef SelectedBlur_H
#define SelectedBlur_H

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

//-----------------------------------------------------------------------------------
#define	L10N_PARAM_BLUR	"blur"
#define	L10N_PARAM_RANGE	"range"
#define	L10N_PARAM_ENABLE	"有効"
#define	L10N_PARAM_ON	"ON"

#define	L10N_PARAM_TARGET0	"target0"
#define	L10N_PARAM_TARGET1	"target1"
#define	L10N_PARAM_TARGET2	"target2"
#define	L10N_PARAM_TARGET3	"target3"
#define	L10N_PARAM_TARGET4	"target4"
#define	L10N_PARAM_TARGET5	"target5"
#define	L10N_PARAM_TARGET6	"target6"
#define	L10N_PARAM_TARGET7	"target7"


#define COLOR_COUNT 8

//-----------------------------------------------------------------------------------
//ユーザーインターフェースのID
//ParamsSetup関数とRender関数のparamsパラメータのIDになる
enum {
	ID_INPUT = 0,	// default input layer 
	
	//以下参考用
	ID_BLUR_VALUE,
	ID_TARGET_RANGE,
	
	ID_TARGET_ENABLED0,
	ID_TARGET_COL0,

	ID_TARGET_ENABLED1,
	ID_TARGET_COL1,

	ID_TARGET_ENABLED2,
	ID_TARGET_COL2,

	ID_TARGET_ENABLED3,
	ID_TARGET_COL3,

	ID_TARGET_ENABLED4,
	ID_TARGET_COL4,

	ID_TARGET_ENABLED5,
	ID_TARGET_COL5,

	ID_TARGET_ENABLED6,
	ID_TARGET_COL6,

	ID_TARGET_ENABLED7,
	ID_TARGET_COL7,

	ID_NUM_PARAMS
	};

//-----------------------------------------------------------------------------------

typedef struct BlurInfo{
	A_long			blur_value;
	A_u_char		col_range;
	A_u_char		reserve1;
	A_u_char		reserve2;
	A_u_char		reserve3;
	A_long			col_count;
	PF_Pixel		target_col[COLOR_COUNT];
	PF_Boolean		isTargetCopy;
	A_long			reserve4;
} BlurInfo, *BlurInfoP, **BlurInfoH;

//-----------------------------------------------------------------------------------
typedef struct blurPrm
{
	PF_InData		*in_data;
	PF_PixelPtr		data;
	A_long			width;
	A_long			widthTrue;
	A_long			height;
	A_long			scanlineWidth;
	PF_Handle		scanlineH;
	A_long			gf[1024];//301
	A_long			blur_value;
}blurPrm;

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
//-------------------------------------------------------------------------------------------------
PF_Err BlurSub8(blurPrm *prm);
PF_Err BlurSub16(blurPrm *prm);
PF_Err BlurSub32(blurPrm *prm);
//-------------------------------------------------------------------------------------------------

#endif // SelectedBlur_H

