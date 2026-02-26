//-----------------------------------------------------------------------------------
/*
	ShitsuKanBlur for VS2010
*/
//-----------------------------------------------------------------------------------

#pragma once
#ifndef ShitsuKanBlur_H
#define ShitsuKanBlur_H

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

	//ターゲットカラー
	ID_COLOR_TOPICS0,

	ID_CBX_COLOR0,
	ID_COL_COLOR0,
	ID_CBX_COLOR1,
	ID_COL_COLOR1,
	ID_CBX_COLOR2,
	ID_COL_COLOR2,
	ID_CBX_COLOR3,
	ID_COL_COLOR3,
	ID_CBX_COLOR4,
	ID_COL_COLOR4,
	ID_CBX_COLOR5,
	ID_COL_COLOR5,
	ID_CBX_COLOR6,
	ID_COL_COLOR6,
	ID_CBX_COLOR7,
	ID_COL_COLOR7,

	ID_COLOR_TOPICS_END0,

	ID_COLOR_TOPICS1,

	ID_CBX_COLOR_EX0,
	ID_COL_COLOR_EX0,
	ID_CBX_COLOR_EX1,
	ID_COL_COLOR_EX1,
	ID_CBX_COLOR_EX2,
	ID_COL_COLOR_EX2,
	ID_CBX_COLOR_EX3,
	ID_COL_COLOR_EX3,
	ID_CBX_COLOR_EX4,
	ID_COL_COLOR_EX4,
	ID_CBX_COLOR_EX5,
	ID_COL_COLOR_EX5,
	ID_CBX_COLOR_EX6,
	ID_COL_COLOR_EX6,
	ID_CBX_COLOR_EX7,
	ID_COL_COLOR_EX7,

	
	ID_COLOR_TOPICS_END1,

	ID_ANGLE,

	ID_HI_TOPICS,
	ID_FLT_HI_LENGTH,
	ID_ADD_HI_BLUR,
	ID_FLT_HILIGHT_LV,
	ID_FLT_HILIGHT_R,
	ID_FLT_HILIGHT_G,
	ID_FLT_HILIGHT_B,
	ID_HI_TOPICS_END,

	ID_SW_TOPICS,
	ID_FLT_SW_LENGTH,
	ID_ADD_SW_BLUR,
	ID_FLT_SHADOW_LV,
	ID_FLT_SHADOW_R,
	ID_FLT_SHADOW_G,
	ID_FLT_SHADOW_B,
	ID_SW_TOPICS_END,

	ID_FLT_NOISE,
	ID_CBX_EDGE,

	ID_PUP_DRAW,
	ID_COL_MASKCOLOR,
	ID_CBX_WHITE,

	ID_NUM_PARAMS
};
#define LENGTH_MIN 3
//UIの表示文字列
#define STR_CBX_ON              L10N_PARAM_ON

#define STR_CBX_COLOR0          L10N_PARAM_ENABLED0
#define STR_CBX_COLOR1          L10N_PARAM_ENABLED1
#define STR_CBX_COLOR2          L10N_PARAM_ENABLED2
#define STR_CBX_COLOR3          L10N_PARAM_ENABLED3
#define STR_CBX_COLOR4          L10N_PARAM_ENABLED4
#define STR_CBX_COLOR5          L10N_PARAM_ENABLED5
#define STR_CBX_COLOR6          L10N_PARAM_ENABLED6
#define STR_CBX_COLOR7          L10N_PARAM_ENABLED7

#define STR_COL_COLOR0          L10N_PARAM_COLOR0
#define STR_COL_COLOR1          L10N_PARAM_COLOR1
#define STR_COL_COLOR2          L10N_PARAM_COLOR2
#define STR_COL_COLOR3          L10N_PARAM_COLOR3
#define STR_COL_COLOR4          L10N_PARAM_COLOR4
#define STR_COL_COLOR5          L10N_PARAM_COLOR5
#define STR_COL_COLOR6          L10N_PARAM_COLOR6
#define STR_COL_COLOR7          L10N_PARAM_COLOR7

#define STR_COL_TOPICS0         L10N_PARAM_TARGET_COLORS
#define STR_COL_TOPICS1         L10N_PARAM_TARGET_EX_COLORS
#define STR_HI_TOPICS           L10N_PARAM_HILIGHT_TOPIC
#define STR_SW_TOPICS           L10N_PARAM_SHADOW_TOPIC

#define STR_CBX_COLOR_EX0       L10N_PARAM_ENABLED_EX0
#define STR_CBX_COLOR_EX1       L10N_PARAM_ENABLED_EX1
#define STR_CBX_COLOR_EX2       L10N_PARAM_ENABLED_EX2
#define STR_CBX_COLOR_EX3       L10N_PARAM_ENABLED_EX3
#define STR_CBX_COLOR_EX4       L10N_PARAM_ENABLED_EX4
#define STR_CBX_COLOR_EX5       L10N_PARAM_ENABLED_EX5
#define STR_CBX_COLOR_EX6       L10N_PARAM_ENABLED_EX6
#define STR_CBX_COLOR_EX7       L10N_PARAM_ENABLED_EX7

#define STR_COL_COLOR_EX0       L10N_PARAM_EX_COLOR0
#define STR_COL_COLOR_EX1       L10N_PARAM_EX_COLOR1
#define STR_COL_COLOR_EX2       L10N_PARAM_EX_COLOR2
#define STR_COL_COLOR_EX3       L10N_PARAM_EX_COLOR3
#define STR_COL_COLOR_EX4       L10N_PARAM_EX_COLOR4
#define STR_COL_COLOR_EX5       L10N_PARAM_EX_COLOR5
#define STR_COL_COLOR_EX6       L10N_PARAM_EX_COLOR6
#define STR_COL_COLOR_EX7       L10N_PARAM_EX_COLOR7

#define STR_ANGLE               L10N_PARAM_DIRECTION
#define STR_FLT_HI_LENGTH       L10N_PARAM_HILIGHT_LENGTH
#define STR_FLT_HI_BLUR         L10N_PARAM_HILIGHT_BLUR
#define STR_FLT_SW_LENGTH       L10N_PARAM_SHADOW_LENGTH
#define STR_FLT_SW_BLUR         L10N_PARAM_SHADOW_BLUR
#define STR_CBX_EDGE1           L10N_PARAM_OUT_OF_SCREEN
#define STR_CBX_EDGE2           L10N_PARAM_EDGE_REPEAT

#define STR_FLT_HILIGHT_LV      L10N_PARAM_HILIGHT_LV
#define STR_FLT_HILIGHT_R       L10N_PARAM_HILIGHT_RED
#define STR_FLT_HILIGHT_G       L10N_PARAM_HILIGHT_GREEN
#define STR_FLT_HILIGHT_B       L10N_PARAM_HILIGHT_BLUE

#define STR_FLT_SHADOW_LV       L10N_PARAM_SHADOW_LV
#define STR_FLT_SHADOW_R        L10N_PARAM_SHADOW_RED
#define STR_FLT_SHADOW_G        L10N_PARAM_SHADOW_GREEN
#define STR_FLT_SHADOW_B        L10N_PARAM_SHADOW_BLUE

#define STR_NOISE               L10N_PARAM_NOISE
#define STR_CBX_DRAW            L10N_PARAM_BLEND_WITH_ORIGINAL

#define STR_PUP_DRAW            L10N_PARAM_BLEND
#define STR_PUP_ITEMS           L10N_PARAM_BLEND_ITEMS
#define	STR_PUP_COUNT			4
#define	STR_PUP_DFLT			1

#define STR_COL_MASKCOLOR       L10N_PARAM_MASK_COLOR
#define STR_CBX_WHITE           L10N_PARAM_WHITE_KEY



#define SKN32_ON 1
#define SKN32_H  0.5



//UIのパラメータ
typedef struct ParamInfo {

	A_long		Color_Max;
	PF_Pixel	Color[8];
	A_long		EXColor_Max;
	PF_Pixel	EXColor[8];
	A_long		TagetCount;

	PF_Pixel	MaskColor;

	PF_Fixed	angle;
	PF_Fixed	hi_length;
	A_long		hi_blur;
	PF_Fixed	sw_length;
	A_long		sw_blur;
	

	PF_FpLong	hi_lv;
	PF_FpLong	hi_r;
	PF_FpLong	hi_g;
	PF_FpLong	hi_b;

	PF_FpLong	sw_lv;
	PF_FpLong	sw_r;
	PF_FpLong	sw_g;
	PF_FpLong	sw_b;

	PF_Boolean	edge;
	PF_FpLong	noise;
	A_long		draw;
	PF_Boolean	white;



} ParamInfo, *ParamInfoP, **ParamInfoH;

#define BLUR_MAX 600

typedef struct ParamInfo8 {
	ParamInfo	info;


	A_long		hi_x_offset;
	A_long		hi_y_offset;

	A_long		sw_x_offset;
	A_long		sw_y_offset;


	A_long		TargetCount;

	PF_InData	*in_data;

	A_long width;
	A_long width2;

	A_long widthTrue;
	A_long height;
	A_long height2;

	PF_Pixel8	*data;

	PF_Handle		scanlineH;
	A_long			scanlineSize;
	A_long			blurSize;
				
	A_u_char	*scanline;
	A_u_char	*scanlineM;
	A_long		*blurTable;

	PF_Boolean		IsTagetHi;

} ParamInfo8, *ParamInfo8P, **ParamInfo8H;

typedef struct ParamInfo16 {
	ParamInfo	info;


	A_long		hi_x_offset;
	A_long		hi_y_offset;

	A_long		sw_x_offset;
	A_long		sw_y_offset;

	PF_Pixel16	MaskColor16;

	A_long		TargetCount;

	PF_InData	*in_data;

	A_long width;
	A_long width2;

	A_long widthTrue;
	A_long height;
	A_long height2;

	PF_Pixel16	*data;

	PF_Handle		scanlineH;
	A_long			scanlineSize;
	A_long			blurSize;

	A_u_short	*scanline;
	A_u_short	*scanlineM;
	A_long		*blurTable;

	PF_Boolean		IsTagetHi;

} ParamInfo16, *ParamInfo16P, **ParamInfo16H;

typedef struct ParamInfo32 {
	ParamInfo	info;


	A_long		hi_x_offset;
	A_long		hi_y_offset;

	A_long		sw_x_offset;
	A_long		sw_y_offset;

	PF_PixelFloat	MaskColor32;

	A_long		TargetCount;

	PF_InData	*in_data;

	A_long width;
	A_long width2;

	A_long widthTrue;
	A_long height;
	A_long height2;

	PF_PixelFloat	*data;

	PF_Handle		scanlineH;
	A_long			scanlineSize;
	A_long			blurSize;

	PF_FpShort	*scanline;
	PF_FpShort	*scanlineM;
	A_long		*blurTable;

	PF_Boolean		IsTagetHi;

} ParamInfo32, *ParamInfo32P, **ParamInfo32H;
//-------------------------------------------------------
PF_Err SitsuKanSub8(CFsAE *ae, ParamInfo *infoP);
PF_Err SitsuKanSub16(CFsAE *ae, ParamInfo *infoP);
PF_Err SitsuKanSub32(CFsAE *ae, ParamInfo *infoP);
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
#endif // ShitsuKanBlur_H

