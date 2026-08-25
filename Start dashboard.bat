@echo off
setlocal
set "ROOT=%~dp0"
set "PYTHON_EXE=%ROOT%.venv\Scripts\python.exe"
if "%ASSISTANT_NAME%"=="" set "ASSISTANT_NAME=Dr. A"
if "%DASHBOARD_PORT%"=="" set "DASHBOARD_PORT=8771"
if "%MODEL_PROVIDER%"=="" set "MODEL_PROVIDER=openai"
if /I "%MODEL_PROVIDER%"=="ollama" set "MODEL_PROVIDER=local"
if /I "%MODEL_PROVIDER%"=="qwen" set "MODEL_PROVIDER=local"
if /I "%MODEL_PROVIDER%"=="local" (
  if "%LOCAL_MODEL_NAME%"=="" set "LOCAL_MODEL_NAME=%QWEN_MODEL%"
  if "%LOCAL_MODEL_NAME%"=="" set "LOCAL_MODEL_NAME=qwen2.5:14b-instruct"
  if "%LOCAL_MODEL_ENDPOINT%"=="" set "LOCAL_MODEL_ENDPOINT=%QWEN_ENDPOINT%"
  if "%LOCAL_MODEL_ENDPOINT%"=="" set "LOCAL_MODEL_ENDPOINT=http://localhost:11434/v1/chat/completions"
) else if "%OPENAI_API_KEY%"=="" (
  echo OPENAI_API_KEY is required. Use Start with OpenAI.bat for a private prompt.
  echo To use Ollama/Qwen instead, run: set MODEL_PROVIDER=local
  pause
  exit /b 1
)

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

cd /d "%ROOT%"
powershell -NoProfile -Command "try { $h=Invoke-RestMethod -Uri 'http://localhost:%DASHBOARD_PORT%/api/health' -TimeoutSec 1; if($h.ok -ne $true){exit 1}; if($h.model_configured -ne $true){exit 2}; exit 0 } catch { exit 1 }" >nul 2>nul
set "HEALTH_STATUS=%ERRORLEVEL%"
if "%HEALTH_STATUS%"=="0" (
  start "" "http://localhost:%DASHBOARD_PORT%/"
  exit /b 0
)
if "%HEALTH_STATUS%"=="2" (
  echo The dashboard is already running without a configured model provider.
  echo Close the existing dashboard process, then run this launcher again.
  start "" "http://localhost:%DASHBOARD_PORT%/"
  exit /b 2
)

if defined PY (
  "%PY%" -c "import docx, reportlab" >nul 2>nul
  if errorlevel 1 (
    echo Installing local report export dependencies...
    "%PY%" -m pip install -r "%ROOT%module_company_profile\requirements.txt"
    if errorlevel 1 (
      echo Unable to install report export dependencies.
      pause
      exit /b 1
    )
  )
  start "" powershell -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File "%ROOT%scripts\open-dashboard-when-ready.ps1" -Port "%DASHBOARD_PORT%"
  "%PY%" "%ROOT%module_company_profile\dashboard\dashboard_server.py"
) else (
  where docker >nul 2>nul
  if errorlevel 1 (
    echo Python and Docker are not available. Install Python or start Docker Desktop.
    pause
    exit /b 1
  )
  docker info >nul 2>nul
  if errorlevel 1 (
    echo Docker Desktop is not running. Start it and try again.
    pause
    exit /b 1
  )
  start "" powershell -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File "%ROOT%scripts\open-dashboard-when-ready.ps1" -Port "%DASHBOARD_PORT%"
  docker compose -f module_company_profile\docker-compose.yml up dashboard
)
