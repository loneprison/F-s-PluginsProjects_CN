//-----------------------------------------------------------------------------------
/*
	OpticalDiffusion for VS2010
*/
//-----------------------------------------------------------------------------------

#pragma once
#ifndef OpticalDiffusion_H
#define OpticalDiffusion_H

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
	#ifndef refconType
		#define refconType void*
	#endif
#else
	#include "PF_Suite_Helper.h"
	#ifndef refconType
		#define refconType A_long
	#endif
#endif

#ifdef AE_OS_WIN
	#include <Windows.h>
#endif

#include "../FsLibrary/FsAE.h"
#include "../FsLibrary/FsHLS.h"
//#include "FsAE.h"

//ユーザーインターフェースのID
//ParamsSetup関数とRender関数のparamsパラメータのIDになる
enum {
	ID_INPUT = 0,	// default input layer

	ID_EXTRACT_ENABLED,
	
	ID_EXTRACT_TOPIC,
	ID_EXTRACT_BLACK_POINT,
	ID_EXTRACT_WHITE_POINT,
	ID_EXTRACT_BLACK_SOFTNESS,
	ID_EXTRACT_WHITE_SOFTNESS,
	ID_EXTRACT_INVERT,
	ID_EXTRACT_TOPIC_END,

	ID_EXTRACT_COLOR_TOPIC,
	ID_EXTRACT_COL_COUNT,
	ID_EXTRACT_COLOR_RANGE,
	ID_EXTRACT_COL1,
	ID_EXTRACT_COL2,
	ID_EXTRACT_COL3,
	ID_EXTRACT_COL4,
	ID_EXTRACT_COL5,
	ID_EXTRACT_COL6,
	ID_EXTRACT_COL7,
	ID_EXTRACT_COL8,
	ID_EXTRACT_COLOR_TOPIC_END,

	ID_MINIMAX_1ST,
	ID_MINIMAX_2ND,
	ID_BLUR,
	ID_BLEND_MODE,
	ID_BLEND_OPACITY,
	ID_NOISE_VALUE,

	ID_NUM_PARAMS
};

//UIの表示文字列
#define	STR_EXTRACT_ENABLED			L10N_PARAM_EXTRACT_ENABLED
#define	STR_EXTRACT_TOPIC			L10N_PARAM_EXTRACT_TOPIC
#define	STR_EXTRACT_BLACK_POINT		L10N_PARAM_BLACK_POINT
#define	STR_EXTRACT_WHITE_POINT		L10N_PARAM_WHITE_POINT
#define	STR_EXTRACT_BLACK_SOFTNESS	L10N_PARAM_BLACK_SOFTNESS
#define	STR_EXTRACT_WHITE_SOFTNESS	L10N_PARAM_WHITE_SOFTNESS
#define	STR_EXTRACT_INVERT			L10N_PARAM_INVERT

#define	STR_EXTRACT_COLOR_TOPIC		L10N_PARAM_EXTRACT_COLOR_TOPIC
#define	STR_EXTRACT_COLOR_COUNT		L10N_PARAM_USE_COUNT
#define	STR_EXTRACT_COLOR_RANGE		L10N_PARAM_RANGE
#define STR_EXTRACT_COL1			L10N_PARAM_COLOR1
#define STR_EXTRACT_COL2			L10N_PARAM_COLOR2
#define STR_EXTRACT_COL3			L10N_PARAM_COLOR3
#define STR_EXTRACT_COL4			L10N_PARAM_COLOR4
#define STR_EXTRACT_COL5			L10N_PARAM_COLOR5
#define STR_EXTRACT_COL6			L10N_PARAM_COLOR6
#define STR_EXTRACT_COL7			L10N_PARAM_COLOR7
#define STR_EXTRACT_COL8			L10N_PARAM_COLOR8

#define	STR_MINIMAX_1ST				L10N_PARAM_MINIMAX_1ST
#define	STR_MINIMAX_2ND				L10N_PARAM_MINIMAX_2ND
#define	STR_BLUR					L10N_PARAM_BLUR

#define	STR_BLEND_MODE				L10N_PARAM_BLEND_MODE
#define	STR_BLEND_ITEMS				L10N_PARAM_BLEND_ITEMS
#define	STR_BLEND_COUNT				6
#define	STR_BLEND_DFLT				2
#define	STR_BLEND_OPACITY			L10N_PARAM_BLEND_OPACITY

#define	STR_NOISE_VALUE				L10N_PARAM_NOISE

namespace BLEND_MODE
{
	enum 
	{
		none = 1,
		Normal,
		Lighten,
		Darken,
		Screen,
		Multiply
	};
}

//UIのパラメータ
typedef struct ParamInfo {
	PF_Boolean	extractEnabled;
	A_long		blackPoint;
	A_long		whitePoint;
	A_long		blackSoftness;
	A_long		whiteSoftness;

	PF_Boolean	invert;

	PF_Fixed	extract_color_Range;
	A_long		extract_color_Count;
	HLSA		extract_colors[8];

	A_long		minimax1;
	A_long		minimax2;
	PF_FpLong	blur;
	A_long		blendMode;
	PF_FpShort	blendOpacity;
	
	PF_FpShort	noiseValue;

} ParamInfo, *ParamInfoP, **ParamInfoH;

//-------------------------------------------------------

PF_Err DF8(CFsAE *ae , ParamInfo *infoP);
PF_Err DF16(CFsAE *ae , ParamInfo *infoP);
PF_Err DF32(CFsAE *ae , ParamInfo *infoP);
///-----------------------------------------------------------------------------------
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
#endif // OpticalDiffusion_H

