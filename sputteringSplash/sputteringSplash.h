//-----------------------------------------------------------------------------------
/*
	PluginSkeleton for VS2010
*/
//-----------------------------------------------------------------------------------

#pragma once

#ifndef sputteringSplash_H
#define sputteringSplash_H

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
#include "../FsLibrary/FsSputtering.h"

//-----------------------------------------------------------------------------
//ParamsSetup用の定数
enum {
	ID_INPUT = 0,

	ID_SEED,		//乱数の基準
	ID_Y,		//量
	ID_DIR,		//向き
	ID_OPACITY_RAND,		//量
	
	ID_POINT_VALUE,	//一回の描画で打つ点の数
	ID_POINT_LENGTH,	//点の距離

	ID_SIZE,

	ID_COLOR1,
	ID_COLOR_TOPIC,
	ID_COLOR_MAX,
	ID_COLOR2,
	ID_COLOR3,
	ID_COLOR4,
	ID_COLOR_TOPIC_END,
	ID_ORG,

	ID_NUM_PARAMS
};
//-----------------------------------------------------------------------------
//パラメータUI用の文字列
#define UI_SEED             L10N_PARAM_SEED
#define UI_VALUE            L10N_PARAM_VALUE
#define UI_DIR1             L10N_PARAM_DIRECTION
#define UI_DIR2             L10N_PARAM_DIRECTION_ITEMS
#define UI_DIR_COUNT	8
#define UI_DIR_DFLT	1
#define UI_OPA_RND          L10N_PARAM_OPACITY_RAND

#define UI_POINT_VALUE      L10N_PARAM_POINT_VALUE
#define UI_POINT_LENGTH     L10N_PARAM_POINT_LENGTH
#define UI_POINT_LEN_SYSNC1 L10N_PARAM_POINT_LEN_SYNC
#define UI_POINT_LEN_SYSNC2 L10N_PARAM_ON

#define UI_SIZE1            L10N_PARAM_SIZE
#define UI_SIZE2            L10N_PARAM_SIZE_ITEMS
#define UI_SIZE_COUNT	5
#define UI_SIZE_DFLT	2

#define UI_COLOR1           L10N_PARAM_COLOR1
#define UI_COLOR_TOPIC      L10N_PARAM_EXTRA_COLORS
#define UI_COLOR_MAX        L10N_PARAM_COLOR_MAX
#define UI_COLOR_MAX_V	4
#define UI_COLOR2           L10N_PARAM_COLOR2
#define UI_COLOR3           L10N_PARAM_COLOR3
#define UI_COLOR4           L10N_PARAM_COLOR4
#define UI_ORG1             L10N_PARAM_BLEND_WITH_ORIGINAL
#define UI_ORG2             L10N_PARAM_ON


//-----------------------------------------------------------------------------


#define EDGE_BORDER8 (PF_MAX_CHAN8 * 9 /10)
#define EDGE_BORDER16 (PF_MAX_CHAN16 * 9 /10)
#define EDGE_BORDER32 (0.9)

#define TARGET_EDGE		(PF_MAX_CHAN8)
#define TARGET_SOLID	(PF_HALF_CHAN8)

typedef struct
{
	A_long		seed;
	PF_Fixed	value;
	A_long		dir;
	PF_Fixed	opa;

	A_long		point_value;
	A_long		point_length;
	A_long		size;
	A_long		color_max;
	PF_Pixel	colors[UI_COLOR_MAX_V];
	A_u_char	*sputRandTable;
	A_u_char	*buf;
	PF_Boolean	org;
} ParamInfo;


//-----------------------------------------------------------------------------
//関数の宣言
PF_Err MainRender8 (CFsAE *ae, ParamInfo *prm);
PF_Err MainRender16 (CFsAE *ae, ParamInfo *prm);
PF_Err MainRender32 (CFsAE *ae, ParamInfo *prm);

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

#endif // sputteringSplash_H
