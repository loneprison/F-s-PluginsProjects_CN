#pragma once
#ifndef CellLineEraser_H
#define CellLineEraser_H

#include "Fs_Target.h"

#include "AEConfig.h"
#include "entry.h"

#include "AE_Effect.h"
#include "AE_EffectCB.h"
#include "AE_EffectCBSuites.h"
#include "AE_Macros.h"
#include "AEGP_SuiteHandler.h"
#include "String_Utils.h"
#include "Param_Utils.h"
#include "Smart_Utils.h"
#include <atomic>
#include <type_traits>
#include <utility>
#include <utility>
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
enum {
	ID_INPUT = 0,
	ID_Color_COUNT,
	ID_Color1, ID_Color2, ID_Color3, ID_Color4, ID_Color5,
	ID_Color6, ID_Color7, ID_Color8, ID_Color9, ID_Color10,
	ID_KEEP_PIXELS,
	ID_FillUnknownColors,
	ID_Fill_Color,
	ID_MakeWhiteTransparent,
	ID_NUM_PARAMS
};

//UIの表示文字列
#define	L10N_PARAM_TARGET_COUNT					"TargetColorCount"
#define	L10N_PARAM_COLOR1				"color1"
#define	L10N_PARAM_COLOR2				"color2"
#define	L10N_PARAM_COLOR3				"color3"
#define	L10N_PARAM_COLOR4				"color4"
#define	L10N_PARAM_COLOR5				"color5"
#define	L10N_PARAM_COLOR6				"color6"
#define	L10N_PARAM_COLOR7				"color7"
#define	L10N_PARAM_COLOR8				"color8"
#define	L10N_PARAM_COLOR9				"color9"
#define	L10N_PARAM_COLOR10				"color10"
#define	L10N_PARAM_KEEP_PIXELS			"KeepPixels"
#define	L10N_PARAM_FILL_UNKNOWN	"Fill unremoved pixels"
#define	L10N_PARAM_FILL_COLOR			"FillColor"
#define	L10N_PARAM_WHITE_TRANS	"Make White Transparent"
#define	L10N_PARAM_ON					"on"




// 共通構造体
typedef struct {
	A_long              target_count;
	PF_Pixel8           targets[10];      // 比較基準（常に8bit）
	PF_EffectWorld* src_world;        // 反復処理用参照
	std::atomic<long>* pixels_changed;   // 収束判定用
	PF_Boolean          KeepPixel;
	PF_Boolean          FillUnknownColors;
	PF_Pixel8           GiveUpColor8;
	PF_Pixel16          GiveUpColor16;
	PF_PixelFloat       GiveUpColor32;
	PF_Boolean          MakeWhiteTransparent;
} FillInfo;

/* 関数宣言 */
PF_Err CellLineEraserSub(CFsAE* ae, FillInfo* infoP);

extern "C" {
	DllExport PF_Err EntryPointFunc(
		PF_Cmd cmd,
		PF_InData* in_data,
		PF_OutData* out_data,
		PF_ParamDef* params[],
		PF_LayerDef* output,
		void* extra);
}

#endif // CellLineEraser_H
