@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0..\scripts\start-with-openai.ps1"
if errorlevel 1 pause
