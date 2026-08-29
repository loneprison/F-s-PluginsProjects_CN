/* MainLineRepaint_Strings.cpp */

#include "MainLineRepaint_old.h"

typedef struct {
	unsigned long	index;
	char			str[256];
} TableString;

TableString		g_strs[StrID_NUMTYPES] = {
	StrID_NONE,					"",
	StrID_Name,					"F's MainLineRepaint",
	StrID_Description,			L10N_PLUGIN_DESC,
	StrID_MADEBY,				"bry-ful",
	
	StrID_MY_Main_Color,		L10N_PARAM_MAIN_COLOR,

	StrID_ERR_getFsAEParams,	L10N_ERR_GETFSAEPARAMS,
	StrID_ERR_getParams,	L10N_ERR_GETPARAMS,
};


char *GetStringPtr(int strNum)
{
	return g_strs[strNum].str;
}
	

