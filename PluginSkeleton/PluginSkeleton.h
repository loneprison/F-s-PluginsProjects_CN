//-----------------------------------------------------------------------------------
/*
	PluginSkeleton for VS2010
*/
//-----------------------------------------------------------------------------------

#pragma once
#ifndef PluginSkeleton_H
#define PluginSkeleton_H

#include "../FsLibrary/Fs.h"

#include "Fs_Target.h"


#include "../FsLibrary/FsAE.h"
#include "../FsLibrary/CParamsSetup.h"

//ユーザーインターフェースのID
//ParamsSetup関数とRender関数のparamsパラメータのIDになる
enum {
	ID_INPUT = 0,	// default input layer

	ID_R,
	ID_G,
	ID_B,

	ID_NOISE,
	ID_NOISE_FRAME,
	ID_NOISE_OFFSET,


	ID_HIDDEN_ON,

	ID_TOPIC,
	ID_ADD_SLIDER,
	ID_FIXED_SLIDER,
	ID_FLOAT_SLIDER,
	ID_COLOR,
	ID_CHECKBOX,
	ID_ANGLE,
	ID_POPUP,
	ID_POINT,
	ID_TOPIC_END,
	ID_BUTTON,

	ID_NUM_PARAMS
};

//UIの表示文字列
#define	L10N_PARAM_R				"R"
#define	L10N_PARAM_G				"G"
#define	L10N_PARAM_B				"B"
#define	L10N_PARAM_NOISE			"noise"
#define	L10N_PARAM_NOISE_FRAME	"frame randerm"
#define	L10N_PARAM_ON	"on"
#define	L10N_PARAM_NOISE_OFFSET	"noise offset"


#define	L10N_PARAM_HIDDEN_UI		"Hidden UI"
#define	L10N_PARAM_HIDDEN_TEXT		"oba-Q!"

#define	L10N_PARAM_SAMPLE_TOPIC			"Sample Topics"
#define	L10N_PARAM_ADD_SLIDER		"Add_Slider"
#define	L10N_PARAM_FIXED_SLIDER	"Fixed_Slider"
#define	L10N_PARAM_FLOAT_SLIDER	"Float_Slider"
#define	L10N_PARAM_COLOR			"Color"
#define	L10N_PARAM_CHECKBOX		"Checkbox"
#define	STR_CHECKBOX2		"on"
#define	L10N_PARAM_ANGLE			"Angle"
#define	L10N_PARAM_POPUP			"Popup"
#define	L10N_PARAM_POPUP_ITEMS		"One|Two|Tree"
#define	STR_POPUP_COUNT		3
#define	STR_POPUP_DFLT		1
#define	L10N_PARAM_POINT			"Point"

#define	L10N_PARAM_BUTTON			"button"
#define	L10N_PARAM_PUSH			"push"

//UIのパラメータ
typedef struct ParamInfo {
	PF_FpLong	r;
	PF_FpLong	g;
	PF_FpLong	b;
	
	PF_FpLong	noise;
	PF_Boolean	noise_frame;
	A_long		noise_offset;

	A_long			add;
	PF_Fixed		fxd;
	PF_FpLong		flt;
	PF_Pixel		col;
	PF_Boolean		cbx;
	PF_Fixed		agl;
	A_long			pop;
	PF_FixedPoint	pnt;
} ParamInfo, *ParamInfoP, **ParamInfoH;

//-------------------------------------------------------


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
#endif // PluginSkeleton_H

