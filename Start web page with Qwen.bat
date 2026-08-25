@echo off
setlocal
set "MODEL_PROVIDER=local"
if "%LOCAL_MODEL_NAME%"=="" set "LOCAL_MODEL_NAME=%QWEN_MODEL%"
if "%LOCAL_MODEL_NAME%"=="" set "LOCAL_MODEL_NAME=qwen2.5:14b-instruct"
if "%LOCAL_MODEL_ENDPOINT%"=="" set "LOCAL_MODEL_ENDPOINT=%QWEN_ENDPOINT%"
if "%LOCAL_MODEL_ENDPOINT%"=="" set "LOCAL_MODEL_ENDPOINT=http://localhost:11434/v1/chat/completions"
call "%~dp0Start dashboard.bat"
