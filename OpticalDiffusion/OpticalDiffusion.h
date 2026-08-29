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
#define	L10N_PARAM_EXTRACT_ENABLED			"Extract Enabled"
#define	L10N_PARAM_EXTRACT_TOPIC			"Extract lightness"
#define	L10N_PARAM_BLACK_POINT		"Black Point"
#define	L10N_PARAM_WHITE_POINT		"White Point"
#define	L10N_PARAM_BLACK_SOFTNESS	"Black Softness"
#define	L10N_PARAM_WHITE_SOFTNESS	"White Softness"
#define	L10N_PARAM_INVERT			"Invert"

#define	L10N_PARAM_EXTRACT_COLOR_TOPIC		"Extract TargetColor"
#define	L10N_PARAM_USE_COUNT		"Use Count"
#define	L10N_PARAM_RANGE		"Range"
#define L10N_PARAM_COLOR1			"Color1"
#define L10N_PARAM_COLOR2			"Color2"
#define L10N_PARAM_COLOR3			"Color3"
#define L10N_PARAM_COLOR4			"Color4"
#define L10N_PARAM_COLOR5			"Color5"
#define L10N_PARAM_COLOR6			"Color6"
#define L10N_PARAM_COLOR7			"Color7"
#define L10N_PARAM_COLOR8			"Color8"

#define	L10N_PARAM_MINIMAX_1ST				"Minimax 1st"
#define	L10N_PARAM_MINIMAX_2ND				"Minimax 2nd"
#define	L10N_PARAM_BLUR					"Blur"

#define	L10N_PARAM_BLEND_MODE				"Blend mode"
#define	L10N_PARAM_BLEND_ITEMS				"None|Normal|Lighten|Darkne|Screen|Multiply"
#define	STR_BLEND_COUNT				6
#define	STR_BLEND_DFLT				2
#define	L10N_PARAM_BLEND_OPACITY			"Blend Opacity"

#define	L10N_PARAM_NOISE				"Noise"

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

