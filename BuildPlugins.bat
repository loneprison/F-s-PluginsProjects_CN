@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0_tools\BuildPlugins.ps1" %*
set "exitCode=%ERRORLEVEL%"
endlocal & exit /b %exitCode%
