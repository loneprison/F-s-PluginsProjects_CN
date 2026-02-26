//-----------------------------------------------------------------------------------
/*
	RimFil for VS2010
*/
//-----------------------------------------------------------------------------------

#pragma once
#ifndef RimFil_H
#define RimFil_H

#include "../FsLibrary/Fs.h"
#include "Fs_Target.h"
#include "../FsLibrary/FsAE.h"
#include "../FsLibrary/tinyfiledialogs.h"
#include "../FsLibrary/json.hpp"
#include <iostream>
#include <fstream>
#include <string>
#include <cmath>
#include <algorithm>


//ユーザーインターフェースのID
//ParamsSetup関数とRender関数のparamsパラメータのIDになる
enum {
	ID_INPUT = 0,	// default input layer

	ID_WIDTH,
	ID_MODE,
	ID_CUSTOMCOLOR,
	ID_WHITE,

	ID_NUM_PARAMS
};


//UIの表示文字列
#define	STR_WIDTH			L10N_PARAM_WIDTH
#define	STR_MODE			L10N_PARAM_FILL_METHOD
#define	STR_MODE_ITEMS		L10N_PARAM_FILL_ITEMS
#define	STR_MODE_COUNT		2
#define	STR_MODE_DFLT		1
#define	STR_CUSTOMCOLOR		L10N_PARAM_CUSTOM_COLOR

#define	STR_WHITE		L10N_PARAM_WHITE_TRANS
//UIのパラメータ
typedef struct ParamInfo {
	A_long			lineWidth;
	PF_Boolean		isWhite;
	PF_Boolean		isCustomColor;
	PF_Pixel8		customColor;
	PF_Pixel16		customColor16;
	PF_PixelFloat	customColor32;
	PF_InData*		in_data;
	PF_EffectWorld* dst;

} ParamInfo, *ParamInfoP, **ParamInfoH;

PF_Err RimFill_Sub(
	CFsAE* ae,
	ParamInfo* infoP
);


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
#endif // RimFil_H

