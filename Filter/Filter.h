//-----------------------------------------------------------------------------------
/*
	Filter for VS2010
*/
//-----------------------------------------------------------------------------------

#pragma once
#ifndef Filter_H
#define Filter_H

#include "../FsLibrary_next/FsAEHeader.h"
#include "../FsLibrary_next/FsVersion.h"
#include "../FsLibrary_next/FsUtils.h"
#include "../FsLibrary_next/PixelBase.h"
#include "../FsLibrary_next/FsG.h"
#include "../FsLibrary_next/FsBlend.h"

#include "Filter_Target.h"

//CAEクラスの読み込み
#include "../FsLibrary_next/CAE.h"

#ifdef AE_OS_WIN
#define SPRINTF(STR,IDX) sprintf_s(num, "%s%d", STR, IDX)
#else
#define SPRINTF(STR,IDX) sprintf_(num, "%s%d", STR, IDX)
#endif

enum
{
	ID_TOPIC =0,
	ID_ENABLED,
	ID_EXTRACT, // none Light Dark
	ID_BORDER_HI,
	ID_SOFTNESS_HI,
	ID_BORDER_LO,
	ID_SOFTNESS_LO,
	ID_BRIGHT,

	ID_MINMAX,
	ID_MAX,
	ID_BLUR,
	ID_OPACITY,
	ID_BLEND,
	ID_TOPIC_END,
	ID_COUNT
};
enum
{
	ID_INPUT=0,
	ID_BASE_ENABLED,
	ID_BASE_OPACITY,
	ID_FILTER_OPACITY,
	ID_BASE_END

};
#define PARAMSET_COUNT 4
#define ID_NUM(n,idx) (ID_BASE_END + idx + ID_COUNT * n)
#define ID_NOISE (ID_BASE_END + ID_COUNT *PARAMSET_COUNT)
#define ID_ALPHA_ON (ID_NOISE+1)

#define ID_NUM_PARAMS (ID_NOISE+2)

//ID_NUM_PARAMS

//UIの表示文字列
#define	STR_ON				L10N_PARAM_ON
#define	STR_BASE_ENABLED	L10N_PARAM_BASE_ENABLED
#define	STR_BASE_OPACITY	L10N_PARAM_BASE_OPACITY

#define	STR_TOPIC			L10N_PARAM_TOPIC
#define	STR_ENABLED			L10N_PARAM_ENABLED
#define	STR_EXTRACT			L10N_PARAM_EXTRACT
#define	STR_EXTRACT_ITEMS	L10N_PARAM_EXTRACT_ITEMS
#define	STR_EXTRACT_COUNT	3
#define	STR_EXTRACT_DFLT	1
#define	STR_BORDER_HI		L10N_PARAM_BORDER_HI
#define	STR_SOFTNESS_HI		L10N_PARAM_SOFTNESS_HI
#define	STR_BORDER_LO		L10N_PARAM_BORDER_LO
#define	STR_SOFTNESS_LO		L10N_PARAM_SOFTNESS_LO
#define	STR_BRIGHT			L10N_PARAM_BRIGHTNESS

#define	STR_MINMAX			L10N_PARAM_MINMAX
#define	STR_MAX				L10N_PARAM_MAX
#define	STR_BLUR			L10N_PARAM_BLUR
#define	STR_OPACITY			L10N_PARAM_OPACITY
#define	STR_BLEND			L10N_PARAM_BLEND
#define	STR_BLEND_ITEMS		L10N_PARAM_BLEND_ITEMS
#define	STR_BLEND_COUNT		9
#define	STR_BLEND_DFLT		1
#define	STR_FILTER_OPACITY	L10N_PARAM_FILTER_OPACITY

#define	STR_NOISE			L10N_PARAM_NOISE
#define	STR_ALPHA_ON		L10N_PARAM_ALPHA_ON

enum EXTRACT_MODE
{
	NONE=1,
	HI,
	LO
};

//UIのパラメータ
typedef struct ParamSetInfo {
	PF_Boolean	enabled;
	A_long		extract_mode;
	PF_FpLong	border_hi;
	PF_FpLong	softness_hi;
	PF_FpLong	border_lo;
	PF_FpLong	softness_lo;
	PF_FpLong	brightness;
	A_long		minmax;
	A_long		max;
	A_long		blur;
	PF_FpLong	opacity;
	A_long		blend_mode;

}ParamSetInfo, *ParamSetInfoP, **ParamSetInfoH;

typedef struct ParamInfo {
	PF_Boolean		base_enabled;
	PF_FpLong		base_opacity;
	ParamSetInfo	paramset[PARAMSET_COUNT];
	PF_FpLong		noise;
	PF_Boolean		alpha_on;
	PF_FpLong		filter_opacity;
} ParamInfo, *ParamInfoP, **ParamInfoH;

//-------------------------------------------------------
PF_Err Exec(CAE *ae, ParamInfo *infoP);
PF_Err Exec08(CAE *ae, ParamInfo *infoP);
PF_Err Exec16(CAE *ae, ParamInfo *infoP);
PF_Err ToHarfSize16(PF_EffectWorldPtr world);
PF_Err ToDoubleSize16(PF_EffectWorldPtr world, PF_Handle bufH);

PF_Err ExtractHi16(PF_EffectWorldPtr world, PF_FpLong wp, PF_FpLong sf);
PF_Err ExtractLo16(PF_EffectWorldPtr world, PF_FpLong bp, PF_FpLong sf);

PF_Err Max16(PF_EffectWorldPtr world, A_long max, PF_Handle bufH);
PF_Err Rev16(PF_EffectWorldPtr world);
PF_Err Blur16(CAE *ae, PF_EffectWorldPtr world, A_long blur, PF_Handle bufH);
PF_Err Brightness16(PF_EffectWorldPtr world, PF_FpLong brigtness);

//-----------------------------------------------------------------------------------
extern "C" {

	DllExport
		PF_Err
		EffectMain(
			PF_Cmd			cmd,
			PF_InData		*in_data,
			PF_OutData		*out_data,
			PF_ParamDef		*params[],
			PF_LayerDef		*output,
			void			*extra);

}

#endif // Filter_H

