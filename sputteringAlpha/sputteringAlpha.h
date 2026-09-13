//-----------------------------------------------------------------------------------
/*
	PluginSkeleton for VS2010
*/
//-----------------------------------------------------------------------------------
#pragma once
#ifndef sputteringAlpha_H
#define sputteringAlpha_H


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

#include "../FsLibrary/FsSputtering.h"


//-----------------------------------------------------------------------------
//ParamsSetup用の定数
enum {
	ID_INPUT = 0,

	ID_SEED,		//乱数の基準
	ID_Y,		//量
	ID_EDGE_VALUE,		//量
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
#define L10N_PARAM_SEED			"seed"
#define L10N_PARAM_VALUE		"value(%)"
#define L10N_PARAM_EDGE_VALUE	"edge_value(%)"
#define L10N_PARAM_OPACITY_RAND		"opacity_rand"

#define L10N_PARAM_POINT_VALUE	"PointValue"
#define L10N_PARAM_POINT_LENGTH	"PointLength"
#define UI_POINT_LEN_SYSNC1	"Point_length_sysnc"
#define UI_POINT_LEN_SYSNC2	"ON"

#define L10N_PARAM_SIZE		"size"
#define L10N_PARAM_SIZE_ITEMS		"極小|小|中|大|特大"
#define UI_SIZE_COUNT	5
#define UI_SIZE_DFLT	2

#define L10N_PARAM_COLOR1		"Color1"
#define L10N_PARAM_EXTRA_COLORS	"ExtraColors"
#define L10N_PARAM_COLOR_MAX	"ColorMax"
#define UI_COLOR_MAX_V	4
#define L10N_PARAM_COLOR2		"Color2"
#define L10N_PARAM_COLOR3		"Color3"
#define L10N_PARAM_COLOR4		"Color4"
#define L10N_PARAM_BLEND_WITH_ORIGINAL			"Blend with original"
#define L10N_PARAM_ON			"ON"



//-----------------------------------------------------------------------------
#define SPD_RAND_MAX	200
#define SPD_VSMALL_VALUE	255


#define EDGE_BORDER8 (PF_MAX_CHAN8 * 8 /10)
#define EDGE_BORDER16 (PF_MAX_CHAN16 * 8 /10)
#define EDGE_BORDER32 (0.8)

#define TARGET_EDGE		(PF_MAX_CHAN8)
#define TARGET_SOLID	(PF_HALF_CHAN8)

typedef struct
{
	A_long		seed;
	PF_Fixed	value;
	PF_Fixed	edge_value;
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

#endif // sputteringAlpha_H
