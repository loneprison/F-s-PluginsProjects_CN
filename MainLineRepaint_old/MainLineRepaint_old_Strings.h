/* MainLineRepaint_Strings.h */

#pragma once

#define L10N_PLUGIN_DESC "セル画の主線を無くします"
#define L10N_PARAM_MAIN_COLOR "主線の色"
// Historical only: no active code path passes this text to PF_OutData::return_msg.
#define L10N_ERR_GETFSAEPARAMS "画像バッファーサイズエラーです。御免なさい。"
#define L10N_ERR_GETPARAMS "パラメータエラーです。御免なさい。"

typedef enum {
	StrID_NONE, 
	StrID_Name,
	StrID_Description,
	StrID_MADEBY,
	StrID_MY_Main_Color,


	StrID_ERR_getFsAEParams,
	StrID_ERR_getParams,
	StrID_NUMTYPES
} StrIDType;

