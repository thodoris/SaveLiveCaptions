@echo off
rem Install / update the SaveLiveCaptions hotkey service. See scripts\install.ps1 for options.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\install.ps1" %*
set EXITCODE=%ERRORLEVEL%
rem Keep the window open when started by double-click (no arguments)
if "%~1"=="" pause
exit /b %EXITCODE%
