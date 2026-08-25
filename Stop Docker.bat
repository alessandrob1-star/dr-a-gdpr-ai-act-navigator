@echo off
setlocal
cd /d "%~dp0"
docker compose -f module_company_profile\docker-compose.yml down
if errorlevel 1 pause
