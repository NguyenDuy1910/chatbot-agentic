@echo off
setlocal enabledelayedexpansion

echo ======================================
echo FinX Engine - Startup Script
echo ======================================
echo.

if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="--help" goto help
if "%1"=="-h" goto help
if "%1"=="docker" goto docker
if "%1"=="api" goto api
if "%1"=="ui" goto ui
if "%1"=="stop" goto stop
if "%1"=="clean" goto clean

echo Unknown option: %1
echo.
goto help

:help
echo Usage: start.bat [option]
echo.
echo Options:
echo   docker       Start with Docker Compose (recommended)
echo   api          Start API server only
echo   ui           Start Web UI only
echo   stop         Stop Docker Compose services
echo   clean        Stop and remove all Docker containers and volumes
echo   help         Show this help message
echo.
goto end

:docker
echo Starting FinX Engine with Docker Compose...
echo.
docker-compose up -d
echo.
echo Services started!
echo.
echo Access the application:
echo   - Web UI:   http://localhost:3000
echo   - API:      http://localhost:8000
echo   - API Docs: http://localhost:8000/docs
echo.
echo Sample PostgreSQL database:
echo   - Host: localhost
echo   - Port: 5432
echo   - Database: sample_db
echo   - User: finx_user
echo   - Password: finx_password
echo.
echo To view logs: docker-compose logs -f
echo To stop: start.bat stop
goto end

:api
echo Starting API server...
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed
    goto end
)

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -q -r requirements.txt

echo.
echo Starting API server on http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.

python api\main.py
goto end

:ui
echo Starting Web UI...
echo.

where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo Node.js/npm is not installed
    goto end
)

cd web-ui

if not exist "node_modules" (
    echo Installing dependencies...
    npm install
)

echo.
echo Starting Web UI on http://localhost:3000
echo.

npm run dev
goto end

:stop
echo Stopping Docker Compose services...
docker-compose down
echo Services stopped
goto end

:clean
echo Stopping and cleaning Docker Compose services...
docker-compose down -v
echo Services stopped and volumes removed
goto end

:end
endlocal

