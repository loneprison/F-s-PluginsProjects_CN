//-----------------------------------------------------------------------------------
/*
	IroToreAdjacent for VS2010
*/
//-----------------------------------------------------------------------------------

#pragma once
#ifndef IroToreAdjacent_H
#define IroToreAdjacent_H

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
#include "../FsLibrary/FsDebug.h"
#include "../FsLibrary/FsHLS.h"

//ユーザーインターフェースのID
//ParamsSetup関数とRender関数のparamsパラメータのIDになる
enum {
	ID_INPUT = 0,	// default input layer
	
	//境界線のみ
	ID_LINE_ONLY,
	
	//変更後の色
	ID_NEW_COLOR,

	//幅
	ID_Y,

	//主線部分最大最小
	ID_LINE_MINMAX,
	
	//主線部分のぼかし
	ID_LINE_BLUR,

	//主線の色
	ID_MN_COLOR1_ON,
	ID_MN_COLOR1,
	ID_MN_COLOR2_ON,
	ID_MN_COLOR2,
	
	//主線検出レベル
	ID_LEVEL,
	
	//隣接色
	ID_AD_COLOR1_ON,
	ID_AD_COLOR1,
	ID_AD_COLOR2_ON,
	ID_AD_COLOR2,
	ID_AD_COLOR3_ON,
	ID_AD_COLOR3,
	ID_AD_COLOR4_ON,
	ID_AD_COLOR4,
	ID_AD_COLOR5_ON,
	ID_AD_COLOR5,
	ID_AD_COLOR6_ON,
	ID_AD_COLOR6,

	ID_NUM_PARAMS
};

//UIの表示文字列
#define	STR_LINE_ONLY		L10N_PARAM_LINE_ONLY

#define	STR_NEW_COLOR		L10N_PARAM_NEW_COLOR

#define	STR_Y			L10N_PARAM_VALUE

#define	STR_LINE_MINMAX		L10N_PARAM_LINE_MINMAX

#define	STR_LINE_BLUR		L10N_PARAM_LINE_BLUR


#define	STR_ON				L10N_PARAM_ON
#define	STR_MN_COLOR1_ON		L10N_PARAM_MAIN1_ON
#define	STR_MN_COLOR2_ON		L10N_PARAM_MAIN2_ON

#define	STR_MN_COLOR1			L10N_PARAM_MAIN1
#define	STR_MN_COLOR2			L10N_PARAM_MAIN2

#define	STR_AD_COLOR1_ON		L10N_PARAM_ADJ1_ON
#define	STR_AD_COLOR2_ON		L10N_PARAM_ADJ2_ON
#define	STR_AD_COLOR3_ON		L10N_PARAM_ADJ3_ON
#define	STR_AD_COLOR4_ON		L10N_PARAM_ADJ4_ON
#define	STR_AD_COLOR5_ON		L10N_PARAM_ADJ5_ON
#define	STR_AD_COLOR6_ON		L10N_PARAM_ADJ6_ON

#define	STR_AD_COLOR1			L10N_PARAM_ADJ1
#define	STR_AD_COLOR2			L10N_PARAM_ADJ2
#define	STR_AD_COLOR3			L10N_PARAM_ADJ3
#define	STR_AD_COLOR4			L10N_PARAM_ADJ4
#define	STR_AD_COLOR5			L10N_PARAM_ADJ5
#define	STR_AD_COLOR6			L10N_PARAM_ADJ6

#define	STR_LEVEL			L10N_PARAM_LEVEL


#define TARGET_MAIN8	255
#define TARGET_ADJ8		128
#define TARGET_NEW8		64

#define TARGET_MAIN16	32768
#define TARGET_ADJ16	16384
#define TARGET_NEW16	8192



#define MN_COLOR_MAX	2
#define AD_COLOR_MAX	6
//UIのパラメータ
typedef struct ParamInfo {
	PF_Boolean	lineOnly;

	PF_Pixel	newColor;


	A_long		mnColorMax;
	PF_Pixel	mnColor[MN_COLOR_MAX];
	A_long		adColorMax;
	PF_Pixel	adColor[AD_COLOR_MAX];
	A_long		level;

	A_long		value;
	A_long		minmax;
	A_long		blur;

	PF_Handle	scanlineH;
	PF_Pixel	*scanline;
	PF_Pixel	*data;
	A_long		targetCount;
	A_long		w;
	A_long		wt;
	A_long		wt2;
	A_long		h;
	A_long		offset;
	A_long		nowX;
	A_long		nowY;

} ParamInfo;
typedef struct ParamInfo16 {
	PF_Boolean	lineOnly;

	PF_Pixel16	newColor;


	A_long		mnColorMax;
	PF_Pixel	mnColor[MN_COLOR_MAX];
	A_long		adColorMax;
	PF_Pixel	adColor[AD_COLOR_MAX];
	A_long		level;

	PF_Pixel16	mnColor16;

	A_long		value;
	A_long		minmax;
	A_long		blur;

	PF_Handle	scanlineH;
	PF_Pixel16	*scanline;
	PF_Pixel16	*data;
	A_long		targetCount;
	A_long		w;
	A_long		wt;
	A_long		wt2;
	A_long		h;
	A_long		offset;
	A_long		nowX;
	A_long		nowY;

} ParamInfo16;
//-------------------------------------------------------
//--------------------------------------------------------------------xFF--------------
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


PF_Err irotoreExec8(CFsAE *ae , ParamInfo *infoP);
PF_Err irotoreExec16(CFsAE *ae , ParamInfo16 *infoP);
#endif // IroToreAdjacent_H

