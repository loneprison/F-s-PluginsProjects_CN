//-----------------------------------------------------------------------------------
/*
	MaxBlur for VS2010
*/
//-----------------------------------------------------------------------------------

#pragma once
#ifndef MaxBlur_H
#define MaxBlur_H

#include "../FsLibrary/Fs.h"
#include "Fs_Target.h"
#include "../FsLibrary/FsAE.h"
#include <iostream>
#include <fstream>
#include <string>
#include <cmath>
#include <algorithm>

#include "Tiny_Mult.h"
#include "Tiny_MinMax.h"
#include "Tiny_Blur.h"
#include "Tiny_AlphaHyperbolic.h"
//ユーザーインターフェースのID
//ParamsSetup関数とRender関数のparamsパラメータのIDになる
enum {
	ID_INPUT = 0,	// default input layer

	ID_MINMAX,
	ID_BLUR,
	ID_HYPERBOLIC,

	ID_NUM_PARAMS
};


//UIの表示文字列
#define	STR_BLUR			L10N_PARAM_BLUR
#define	STR_MINMAX			L10N_PARAM_MAX
#define	STR_HYPERBOLIC		L10N_PARAM_HYPERBOLIC

//UIのパラメータ
typedef struct {
	A_long				blur;
	A_long				minmax;
	PF_FpLong			hyperbolic;
} ParamInfo;


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
#endif // MaxBlur_H

