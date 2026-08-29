/*
	各種定数を設定

	PiPLリソースに使う為にマクロ展開は最低限

*/
#pragma once
#ifndef Filter_Target_H
#define Filter_Target_H

#include "../FsLibrary_next/FsVersion.h"



#define L10N_PLUGIN_DESC		"Filter Effect Filter"
#define FS_DESCRIPTION		L10N_PLUGIN_DESC
#define	FS_NAME				"F's Filter"
#define FS_MATCH_NAME		FS_NAME
//-----------------------------------------------------------------------------------
//プラグインが表示されるメニュー名
	//#define FS_CATEGORY "F's Plugins-Channel"
	//#define FS_CATEGORY "F's Plugins-Draw"
	//#define FS_CATEGORY "NF's Plugins-Filter"
	//#define FS_CATEGORY "F's Plugins-Cell"
	//#define FS_CATEGORY "F's Plugins-Colorize"
	//#define FS_CATEGORY "F's Plugins-Script"
	//#define FS_CATEGORY "F's Plugins-{Legacy}"
#define FS_CATEGORY "NF's Plugins-{Legacy}"


//#define SUPPORT_SMARTFX			//これを有効にするとSmartFX+Float_Colorに対応する



//value:4 [PF_OutFlag_NON_PARAM_VARY] 全フレームで描画する

//value:64 [PF_OutFlag_USE_OUTPUT_EXTENT] 表示画面全部
//value:16777216 [PF_OutFlag_I_HAVE_EXTERNAL_DEPENDENCIES]

//value:33554432[PF_OutFlag_DEEP_COLOR_AWARE] 16bit

//#define FS_OUT_FLAGS	50332164	//こっちにすると全フレーム描画する
#define FS_OUT_FLAGS	50332192	//通常はこちら



#if defined(SUPPORT_SMARTFX)
//value:8 [PF_OutFlag2_PARAM_GROUP_START_COLLAPSED_FLAG] グループ
//value:1024 [PF_OutFlag2_SUPPORTS_SMART_RENDER] スマートレンダー
//value:4096 [PF_OutFlag2_FLOAT_COLOR_AWARE] 32bit
#define FS_OUT_FLAGS2	5128

#else
//value : 8[PF_OutFlag2_PARAM_GROUP_START_COLLAPSED_FLAG]
#define FS_OUT_FLAGS2	8
#endif

#endif // Filter_Target_H


