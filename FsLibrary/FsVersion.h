#pragma once
#ifndef FS_VAERSION_H
#define FS_VAERSION_H


//-----------------------------------------------------------------------------------
//バージョンを買えたAlphaFixPiPL.rのAE_Effect_Versionも変えること
#ifndef FS_VERSION_PROFILE
#define FS_VERSION_PROFILE 300
#endif

#if FS_VERSION_PROFILE == 300

#define	MAJOR_VERSION		3
#define	MINOR_VERSION		0
#define	BUG_VERSION			0
//#define	STAGE_VERSION		PF_Stage_DEVELOP
//#define	STAGE_VERSION		PF_Stage_ALPHA
//#define	STAGE_VERSION		PF_Stage_BETA
#define	STAGE_VERSION		PF_Stage_RELEASE
#define	BUILD_VERSION		0

//上の値を計算した結果
#define FS_VERSION	1572864

#elif FS_VERSION_PROFILE == 310

#define	MAJOR_VERSION		3
#define	MINOR_VERSION		1
#define	BUG_VERSION			0
#define	STAGE_VERSION		PF_Stage_RELEASE
#define	BUILD_VERSION		0

//3.1.0 Release
#define FS_VERSION	1607168

#else
#error Unsupported FS_VERSION_PROFILE
#endif


#endif // FS_VAERSION_H

