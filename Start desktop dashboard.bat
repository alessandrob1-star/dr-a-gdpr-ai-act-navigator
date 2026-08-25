@echo off
setlocal
set "ROOT=%~dp0"
set "PYTHON_EXE=%ROOT%.venv\Scripts\python.exe"
if "%ASSISTANT_NAME%"=="" set "ASSISTANT_NAME=Dr. A"
if "%LOCAL_MODEL_NAME%"=="" set "LOCAL_MODEL_NAME=%QWEN_MODEL%"
if "%LOCAL_MODEL_NAME%"=="" set "LOCAL_MODEL_NAME=qwen2.5:14b-instruct"
if "%LOCAL_MODEL_ENDPOINT%"=="" set "LOCAL_MODEL_ENDPOINT=%QWEN_ENDPOINT%"
if "%LOCAL_MODEL_ENDPOINT%"=="" set "LOCAL_MODEL_ENDPOINT=http://localhost:11434/v1/chat/completions"

set "PY="
if exist "%PYTHON_EXE%" set "PY=%PYTHON_EXE%"
if not defined PY (
  where python >nul 2>nul
  if not errorlevel 1 set "PY=python"
)
if not defined PY (
  where py >nul 2>nul
  if not errorlevel 1 set "PY=py"
)
if not defined PY (
  echo Python is not available. Install Python 3.12 or create .venv first.
  pause
  exit /b 1
)

cd /d "%ROOT%"
"%PY%" -c "import PySide6, docx, reportlab" >nul 2>nul
if errorlevel 1 (
  echo Installing desktop UI dependencies...
  "%PY%" -m pip install -r "%ROOT%module_company_profile\requirements.txt"
  if errorlevel 1 (
    echo Unable to install desktop UI dependencies.
    pause
    exit /b 1
  )
)

"%PY%" "%ROOT%module_company_profile\desktop_app.py"
