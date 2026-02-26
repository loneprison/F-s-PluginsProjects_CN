//-----------------------------------------------------------------------------------
/*
	F's Plugins for VS2010/VS2012
*/
//-----------------------------------------------------------------------------------


#pragma once
#ifndef PixelSelector_H
#define PixelSelector_H

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

//-----------------------------------------------------------------------------
//ParamsSetup用の定数
#define PS_PRM_COUNT	24
enum {
	paramsOffset_topic = 0,
	paramsOffset_enabled,
	paramsOffset_s_color,
	paramsOffset_topic_end,
	paramsOffset_num
};
enum{
	PixelSelector_INPUT	= 0,
	PixelSelector_TOPIC,
	PixelSelector_REV,
	PixelSelector_FILL,
	PixelSelector_FILL_COLOR,
	PixelSelector_FILL_OPACITY,
	PixelSelector_TOPIC_END,
	PixelSelector_NUM,

};
#define PARAMS_IDX(I,J) (PixelSelector_NUM + (I) *paramsOffset_num + (J) )
#define PixelSelector_LV (PixelSelector_NUM + PS_PRM_COUNT * paramsOffset_num)
#define PixelSelector_POP (PixelSelector_NUM + PS_PRM_COUNT * paramsOffset_num+1)
#define PixelSelector_NUM_PARAMS (PixelSelector_NUM + PS_PRM_COUNT * paramsOffset_num+2)
#define ID_NUM_PARAMS PixelSelector_NUM_PARAMS
//-----------------------------------------------------------------------------
//パラメータUI用の文字列
#define UI_TOPIC	L10N_PARAM_TOPIC
#define UI_ON		L10N_PARAM_ON
#define UI_REV		L10N_PARAM_REVERSE
#define UI_FILL		L10N_PARAM_FILL
#define UI_FILL_COLOR	L10N_PARAM_FILL_COLOR
#define UI_FILL_OPA		L10N_PARAM_FILL_OPACITY

#define UI_ENABLED	L10N_PARAM_ENABLED
#define UI_SRC_COLOR	L10N_PARAM_TARGET_COLOR

#define UI_LV			L10N_PARAM_LEVEL

#define UI_POP1			L10N_PARAM_DISP
#define UI_POP2			L10N_PARAM_DISP_ITEMS

#define ERR_GET_AEPRM	L10N_ERR_GET_AEPRM
#define ERR_GET_PRM		L10N_ERR_GET_PRM
//-----------------------------------------------------------------------------

typedef struct
{
	PF_Pixel		src[PS_PRM_COUNT];
	A_long			count;
	PF_Boolean		rev;
	PF_Boolean		fill;
	PF_Pixel		col;
	PF_Pixel16		col16;
	PF_PixelFloat	col32;
	A_long		dispCount;
	A_u_char	lv;
} ParamInfo;

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

#endif // PixelSelector_H
