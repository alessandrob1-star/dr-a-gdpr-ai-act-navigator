@echo off
setlocal
cd /d "%~dp0"

where docker >nul 2>nul
if errorlevel 1 (
  echo Docker Desktop is not installed or is not available in PATH.
  echo Install and start Docker Desktop, then try again.
  pause
  exit /b 1
)

docker info >nul 2>nul
if errorlevel 1 (
  echo Docker Desktop is not running. Start it and try again.
  pause
  exit /b 1
)

if "%OPENAI_API_KEY%"=="" (
  echo OPENAI_API_KEY is required before Docker startup.
  pause
  exit /b 1
)
echo Preparing the demo with gpt-5.6-sol through the OpenAI API.

docker compose -f module_company_profile\docker-compose.yml up -d --build dashboard
if errorlevel 1 (
  echo Docker startup failed.
  pause
  exit /b 1
)

echo Waiting for the dashboard to become ready...
for /l %%i in (1,1,60) do (
  powershell -NoProfile -Command "try { $h=Invoke-RestMethod -Uri 'http://localhost:8771/api/health' -TimeoutSec 2; if($h.ok -eq $true){exit 0} } catch {}; exit 1" >nul 2>nul
  if not errorlevel 1 goto ready
  timeout /t 2 /nobreak >nul
)

echo The dashboard did not respond within two minutes.
docker compose -f module_company_profile\docker-compose.yml ps
pause
exit /b 1

:ready
start "" "http://localhost:8771"
echo Demo available at http://localhost:8771
exit /b 0
