//-----------------------------------------------------------------------------------
/*
	F's Plugins for VS2010/VS2012
*/
//-----------------------------------------------------------------------------------
#pragma once
#ifndef SelectColor_H
#define SelectColor_H

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
//#include "FsAE.h"


enum {
	ID_INPUT = 0,		// default input layer 

	ID_TARGET0,
	ID_SRCCOL0,

	ID_TARGET1,
	ID_SRCCOL1,

	ID_TARGET2,
	ID_SRCCOL2,

	ID_TARGET3,
	ID_SRCCOL3,

	ID_TARGET4,
	ID_SRCCOL4,

	ID_TARGET5,
	ID_SRCCOL5,

	ID_TARGET6,
	ID_SRCCOL6,

	ID_TARGET7,
	ID_SRCCOL7,

	ID_REV,
	ID_LEVEL,
	ID_NUM_PARAMS
};

#define SelectColorCount 8

#define TARGET_POS(i) ( ID_TARGET0 + (i)*2 )
#define SRCCOL_POS(i) ( ID_TARGET0 + (i)*2 +1)

#define STR_TARGET0          L10N_PARAM_TARGET0
#define STR_TARGET1          L10N_PARAM_TARGET1
#define STR_TARGET2          L10N_PARAM_TARGET2
#define STR_TARGET3          L10N_PARAM_TARGET3
#define STR_TARGET4          L10N_PARAM_TARGET4
#define STR_TARGET5          L10N_PARAM_TARGET5
#define STR_TARGET6          L10N_PARAM_TARGET6
#define STR_TARGET7          L10N_PARAM_TARGET7
#define STR_TARGET_ON        L10N_PARAM_ENABLE

#define STR_COLOR0           L10N_PARAM_COLOR0
#define STR_COLOR1           L10N_PARAM_COLOR1
#define STR_COLOR2           L10N_PARAM_COLOR2
#define STR_COLOR3           L10N_PARAM_COLOR3
#define STR_COLOR4           L10N_PARAM_COLOR4
#define STR_COLOR5           L10N_PARAM_COLOR5
#define STR_COLOR6           L10N_PARAM_COLOR6
#define STR_COLOR7           L10N_PARAM_COLOR7

#define STR_REV              L10N_PARAM_REVERSE
#define STR_REV_ON           L10N_PARAM_REVERSE_ON
#define STR_LEVEL            L10N_PARAM_TOLERANCE

typedef struct ParamInfo{
	PF_Boolean		rev;
	A_long			lv;
	A_long			count;
	PF_Pixel8		src[SelectColorCount];
} ParamInfo,*ParamInfoP,**ParamInfoH;

//-------------------------------------------------------------------------------------------------

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



#endif // SelectColor_H
