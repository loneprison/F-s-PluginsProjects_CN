//-----------------------------------------------------------------------------------
/*
	F's Plugins for VS2010/VS2012
*/
//-----------------------------------------------------------------------------------

#include "sputteringRect.h"
#include "sputteringRectText.generated.h"


//-----------------------------------------------------------------------------
static PF_Err 
ParamsSetup (
	PF_InData		*in_data,
	PF_OutData		*out_data,
	PF_ParamDef		*params[],
	PF_LayerDef		*output)
{
	PF_Err			err = PF_Err_NONE;
	PF_ParamDef		def;
	const sputteringRectText::Strings strings(in_data);
	
	//-----------------
	AEFX_CLR_STRUCT(def);
	PF_ADD_SLIDER(	AETEXT_PARAM(strings, L10N_PARAM_SEED),		//パラメータの名前
					0, 				//数値入力する場合の最小値
					32000,			//数値入力する場合の最大値
					0,				//スライダーの最小値 
					144,			//スライダーの最大値
					0,				//デフォルトの値
					ID_SEED
					);
	//-----------------
	AEFX_CLR_STRUCT(def);
	PF_ADD_SLIDER(	AETEXT_PARAM(strings, L10N_PARAM_VALUE),		//パラメータの名前
					0, 				//数値入力する場合の最小値
					32000,			//数値入力する場合の最大値
					0,				//スライダーの最小値 
					100,			//スライダーの最大値
					20,				//デフォルトの値
					ID_Y
					);
	//-----------------
	AEFX_CLR_STRUCT(def);
	PF_ADD_FIXED(	AETEXT_PARAM(strings, L10N_PARAM_OPACITY_RAND),		//パラメータの名前
					0, 				//数値入力する場合の最小値
					5,				//数値入力する場合の最大値
					0,				//スライダーの最小値 
					2,				//スライダーの最大値
					1,				//デフォルトの値
					2,				//表示される小数の桁数
					0,
					0,
					ID_OPACITY_RAND
					);
	//-----------------
	AEFX_CLR_STRUCT(def);
	PF_ADD_POINT(	AETEXT_PARAM(strings, L10N_PARAM_TOP_LEFT),
					25,	// X(横の%)
					25,	// Y(縦の%)
					FALSE,	// TRUEなら0.0から100.0の値に限定される
					ID_TOPLEFT
				);
	//-----------------
	AEFX_CLR_STRUCT(def);
	PF_ADD_POINT(	AETEXT_PARAM(strings, L10N_PARAM_BOTTOM_RIGHT),
					75,	// X(横の%)
					75,	// Y(縦の%)
					FALSE,	// TRUEなら0.0から100.0の値に限定される
					ID_BOTTOMRIGHT
				);
	//-----------------
	AEFX_CLR_STRUCT(def);
	PF_ADD_SLIDER(	AETEXT_PARAM(strings, L10N_PARAM_POINT_VALUE),		//パラメータの名前
					1, 				//数値入力する場合の最小値
					100,			//数値入力する場合の最大値
					1,				//スライダーの最小値 
					50,			//スライダーの最大値
					10,				//デフォルトの値
					ID_POINT_VALUE
					);
	//-----------------
	AEFX_CLR_STRUCT(def);
	PF_ADD_SLIDER(	AETEXT_PARAM(strings, L10N_PARAM_POINT_LENGTH),		//パラメータの名前
					5, 			//数値入力する場合の最小値
					1000,			//数値入力する場合の最大値
					5,				//スライダーの最小値 
					200,			//スライダーの最大値
					50,				//デフォルトの値
					ID_POINT_LENGTH
					);
	//-----------------
	//ポップアップ
	AEFX_CLR_STRUCT(def);	
	PF_ADD_POPUP(	AETEXT_PARAM(strings, L10N_PARAM_SIZE),
					UI_SIZE_COUNT,	//メニューの数
					UI_SIZE_DFLT,	//デフォルト
					AETEXT_POPUP(strings, L10N_PARAM_SIZE_ITEMS),
					ID_SIZE
					);

	//-----------------
	AEFX_CLR_STRUCT(def);
	PF_ADD_COLOR(	AETEXT_PARAM(strings, L10N_PARAM_COLOR1),
					PF_MAX_CHAN8,	// Red
					PF_MAX_CHAN8,	//Green
					PF_MAX_CHAN8,	//Blue
					ID_COLOR1
					);
	
	//-----------------
	//トピック表示の開始
	AEFX_CLR_STRUCT(def);	
	def.flags 	= 	PF_ParamFlag_START_COLLAPSED;	//
	PF_ADD_TOPIC(	AETEXT_TOPIC(strings, L10N_PARAM_EXTRA_COLORS),
					ID_COLOR_TOPIC
					);
	//-----------------
	AEFX_CLR_STRUCT(def);
	PF_ADD_SLIDER(	AETEXT_PARAM(strings, L10N_PARAM_COLOR_MAX),		//パラメータの名前
					1, 				//数値入力する場合の最小値
					UI_COLOR_MAX_V,			//数値入力する場合の最大値
					1,				//スライダーの最小値 
					UI_COLOR_MAX_V,			//スライダーの最大値
					20,				//デフォルトの値
					ID_COLOR_MAX
					);

	//-----------------
	AEFX_CLR_STRUCT(def);
	PF_ADD_COLOR(	AETEXT_PARAM(strings, L10N_PARAM_COLOR2),
					PF_MAX_CHAN8,	// Red
					PF_MAX_CHAN8,	//Green
					0,	//Blue
					ID_COLOR2
					);
	//-----------------
	AEFX_CLR_STRUCT(def);
	PF_ADD_COLOR(	AETEXT_PARAM(strings, L10N_PARAM_COLOR3),
					PF_MAX_CHAN8,	// Red
					0,	//Green
					PF_MAX_CHAN8,	//Blue
					ID_COLOR3
					);
	//-----------------
	AEFX_CLR_STRUCT(def);
	PF_ADD_COLOR(	AETEXT_PARAM(strings, L10N_PARAM_COLOR4),
					0,	// Red
					PF_MAX_CHAN8,	//Green
					PF_MAX_CHAN8,	//Blue
					ID_COLOR4
					);
	//-----------------
	//トピック表示の終わり
	AEFX_CLR_STRUCT(def);
	PF_END_TOPIC(ID_COLOR_TOPIC_END);
	//-----------------
	//チェックボックス
	AEFX_CLR_STRUCT(def);
	PF_ADD_CHECKBOX(AETEXT_PARAM(strings, L10N_PARAM_BLEND_WITH_ORIGINAL),
					AETEXT_LABEL(strings, L10N_PARAM_ON),
					FALSE,
					0,
					ID_ORG
					);
	//-----------------

	out_data->num_params = ID_NUM_PARAMS;

	return err;
}
//-------------------------------------------------------------------------------------------------
static PF_Err GetParams(CFsAE *ae, ParamInfo *infoP)
{
	PF_Err				err		= PF_Err_NONE;

	ERR(ae->GetADD(ID_SEED,&infoP->seed));
	ERR(ae->GetADD(ID_Y,&infoP->value));
	ERR(ae->GetFIXED(ID_OPACITY_RAND,&infoP->opa));

	PF_FixedPoint tl,br;
	ERR(ae->GetFIXEDPOINT(ID_TOPLEFT,&tl));
	ERR(ae->GetFIXEDPOINT(ID_BOTTOMRIGHT,&br));
	if (!err){
		infoP->rect.left	= tl.x >>16;
		infoP->rect.top		= tl.y >>16;
		infoP->rect.right	= br.x >>16;
		infoP->rect.bottom	= br.y >>16;
		if(infoP->rect.left>infoP->rect.right) swapLong(&infoP->rect.left,&infoP->rect.right);
		if(infoP->rect.top>infoP->rect.bottom) swapLong(&infoP->rect.top,&infoP->rect.bottom);
	}

	ERR(ae->GetADD(ID_POINT_VALUE,&infoP->point_value));
	ERR(ae->GetADD(ID_POINT_LENGTH,&infoP->point_length));
	if (!err){
		infoP->point_length = ae->downScale(infoP->point_length);
		if (infoP->point_length<2)  infoP->point_length = 2;
	}
	ERR(ae->GetPOPUP(ID_SIZE,&infoP->size));
	ERR(ae->GetADD(ID_COLOR_MAX,&infoP->color_max));

	ERR(ae->GetCOLOR(ID_COLOR1,&infoP->colors[0]));
	ERR(ae->GetCOLOR(ID_COLOR2,&infoP->colors[1]));
	ERR(ae->GetCOLOR(ID_COLOR3,&infoP->colors[2]));
	ERR(ae->GetCOLOR(ID_COLOR4,&infoP->colors[3]));

	ERR(ae->GetCHECKBOX(ID_ORG,&infoP->org));

	return err;
}
//-------------------------------------------------------------------------------------------------
static PF_Err 
	Exec (CFsAE *ae , ParamInfo *infoP)
{
	PF_Err	err = PF_Err_NONE;

	if (infoP->org == TRUE) {
		ERR( ae->CopyInToOut());
	}else{
		ERR(ae->out->clear());
	}
	if (infoP->value>0){
		CFsBuffer buf = ae->NewBuffer(SPD_RAND_MAX*sizeof(A_u_char));// + SPD_RAND_MAX
		if (buf.alive()==FALSE){
			ae->out_data->out_flags |= PF_OutFlag_DISPLAY_ERROR_MESSAGE;
			err = PF_Err_INTERNAL_STRUCT_DAMAGED;
			return err;
		}
		infoP->sputRandTable = buf.bufA_u_char();
		SetupSputData(infoP->size,infoP->sputRandTable);

		F_SRAND(infoP->seed);	
		switch(ae->pixelFormat())
		{
		case PF_PixelFormat_ARGB128:
			ERR(MainRender32(ae,infoP));
			break;
		case PF_PixelFormat_ARGB64:
			ERR(MainRender16(ae,infoP));
			break;
		case PF_PixelFormat_ARGB32:
			ERR(MainRender8(ae,infoP));
			break;
		}
		buf.Dispose();
	}
	return err;
}
//-----------------------------------------------------------------------------
 static PF_Err 
Render ( 
	PF_InData		*in_data,
	PF_OutData		*out_data,
	PF_ParamDef		*params[],
	PF_LayerDef		*output )
{
	PF_Err	err = PF_Err_NONE;
	PF_Handle		pixelTable = NULL;
	
	CFsAE ae(in_data,out_data,params,output,ID_NUM_PARAMS);
	err =ae.resultErr();
	if (!err){
		ParamInfo info;
		ERR(GetParams(&ae,&info));
		ERR(Exec(&ae,&info));
	}
	return err;
}
 //-----------------------------------------------------------------------------------
/*
	SmartFX対応の場合、まずこの関数が呼ばれてパラメータの獲得を行う
*/
#if defined(SUPPORT_SMARTFX)
static PF_Err
PreRender(
	PF_InData			*in_data,
	PF_OutData			*out_data,
	PF_PreRenderExtra	*extraP)
{
	PF_Err		err 		= PF_Err_NONE;
	CFsAE ae(in_data,out_data,extraP,sizeof(ParamInfo),ID_NUM_PARAMS);
	err = ae.resultErr();
	if (!err){

		ParamInfo *infoP = reinterpret_cast<ParamInfo*>(ae.LockPreRenderData());
		if (infoP){
			ae.SetHostPreRenderData();
			ERR(GetParams(&ae,infoP));
			ERR(ae.UnSetPreRenderData());
			ae.UnlockPreRenderData();
		}else{
			err = PF_Err_OUT_OF_MEMORY;
		}
	}
	return err;
}
#endif
//-----------------------------------------------------------------------------------
#if defined(SUPPORT_SMARTFX)
static PF_Err
SmartRender(
	PF_InData				*in_data,
	PF_OutData				*out_data,
	PF_SmartRenderExtra		*extraP)
{
	PF_Err			err		= PF_Err_NONE,
					err2 	= PF_Err_NONE;

	CFsAE ae(in_data,out_data,extraP,ID_NUM_PARAMS);
	err = ae.resultErr();
	if (!err){
		ParamInfo *infoP = reinterpret_cast<ParamInfo*>(ae.LockPreRenderData());
		if (infoP){
			ERR(Exec(&ae,infoP));
			ERR2(ae.UnsetSmartRender());
			ae.UnlockPreRenderData();
		}else{
			err = PF_Err_OUT_OF_MEMORY;
		}
	}
	return err;
}
#endif


#include "Fs_Entry.h"
