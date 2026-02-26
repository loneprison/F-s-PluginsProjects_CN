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
#define	STR_R				L10N_PARAM_R
#define	STR_G				L10N_PARAM_G
#define	STR_B				L10N_PARAM_B
#define	STR_NOISE			L10N_PARAM_NOISE
#define	STR_NOISE_FRAME1	L10N_PARAM_NOISE_FRAME
#define	STR_NOISE_FRAME2	L10N_PARAM_ON
#define	STR_NOISE_OFFSET	L10N_PARAM_NOISE_OFFSET


#define	STR_HIDDEN_ON1		L10N_PARAM_HIDDEN_UI
#define	STR_HIDDEN_ON2		L10N_PARAM_HIDDEN_TEXT

#define	STR_TOPIC			L10N_PARAM_SAMPLE_TOPIC
#define	STR_ADD_SLIDER		L10N_PARAM_ADD_SLIDER
#define	STR_FIXED_SLIDER	L10N_PARAM_FIXED_SLIDER
#define	STR_FLOAT_SLIDER	L10N_PARAM_FLOAT_SLIDER
#define	STR_COLOR			L10N_PARAM_COLOR
#define	STR_CHECKBOX1		L10N_PARAM_CHECKBOX
#define	STR_CHECKBOX2		L10N_PARAM_ON
#define	STR_ANGLE			L10N_PARAM_ANGLE
#define	STR_POPUP			L10N_PARAM_POPUP
#define	STR_POPUP_ITEMS		L10N_PARAM_POPUP_ITEMS
#define	STR_POPUP_COUNT		3
#define	STR_POPUP_DFLT		1
#define	STR_POINT			L10N_PARAM_POINT

#define	STR_BUTTON1			L10N_PARAM_BUTTON
#define	STR_BUTTON2			L10N_PARAM_PUSH

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

