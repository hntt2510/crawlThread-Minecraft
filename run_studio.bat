@echo off
title Threads Comment Video Studio
cd /d "%~dp0"
powershell.exe -ExecutionPolicy Bypass -File "run_studio.ps1"
pause
