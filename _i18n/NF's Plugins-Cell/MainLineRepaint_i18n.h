#pragma once

/*
 * Localization switch for MainLineRepaint.
 *
 * Default: Japanese (original text).
 * Define FS_LOCALIZE_ZH_CN in project preprocessor definitions to build zh-CN UI text.
 */

#if defined(FS_LOCALIZE_ZH_CN)
	#define L10N_PLUGIN_NAME			"F's MainLineRepaint"
	#define L10N_PLUGIN_DESC			"去除二值图像主线"

	#define L10N_PARAM_MAIN_COLOR		"主线颜色"
	#define L10N_PARAM_LEVEL			"阈值"
#else
	#define L10N_PLUGIN_NAME			"F's MainLineRepaint"
	#define L10N_PLUGIN_DESC			"セル画の主線を無くします"

	#define L10N_PARAM_MAIN_COLOR		"主線の色"
	#define L10N_PARAM_LEVEL			"許容値(%)"
#endif



