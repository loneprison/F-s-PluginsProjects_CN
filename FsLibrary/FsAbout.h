#pragma once
#ifndef FS_ABOUT_H
#define FS_ABOUT_H

#define FS_ABOUT_DIALOG	"var  FsAbout = function()\r\n\
{\r\n\
	var strName = \"%s\";\r\n\
	var strVersion = \"ver %d.%d [%s]\";\r\n\
	var strDis = \"%s\";\r\n\
	var strMyName = \"https://github.com/bryful : bryful@gmail.com \";\r\n\
    var nanae = \"Nanae Furuhashi - My beloved daughter. May she rest in peace.\";\r\n\
	var winObj = new Window(\"dialog\", \"NF's Plugins\", [ 0,  0,  480, 180] );\r\n\
\
	var edFsName = winObj.add(\"edittext\", [  30,   10,   30+ 440,   10+  20], strName, { readonly:true, borderless:true });\r\n\
	var edFsVersion = winObj.add(\"edittext\", [  30,   40,   30+ 440,   40+ 20], strVersion, { readonly:true, borderless:true });\r\n\
	var edFsDis = winObj.add(\"edittext\", [  30,   70,   30+ 440,   70+  20], strDis, { readonly:true, borderless:true });\r\n\
	var edMyName = winObj.add(\"edittext\", [  30,  100,   30+ 440,  100+  20], strMyName, { readonly:true, borderless:true });\r\n\
    var stNana = winObj.add(\"statictext\", [  30,  130,   30+ 440,  130+  20], nanae, { readonly:true, borderless:true });\r\n\
	var btnOK = winObj.add(\"button\", [ 360,  140,  360+ 100,  140+  24], \"OK\" , { name:\"ok\" });\r\n\
	this.show = function()\r\n\
	{\r\n\
		winObj.center();\r\n\
		return winObj.show();\r\n\
	}\r\n\
}\r\n\
var dlg = new FsAbout;\r\n\
dlg.show();\r\n"

#endif
