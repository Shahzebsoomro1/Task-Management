@echo off
REM Quick Start Script for Task Management System (Windows)

echo ======================================
echo Task Management System - Quick Start
echo ======================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo [x] Docker is not installed. Please install Docker Desktop first.
    echo     Download from: https://www.docker.com/products/docker-desktop
    exit /b 1
)

for /f "tokens=*" %%i in ('docker --version') do set DOCKER_VERSION=%%i
echo [OK] Found: %DOCKER_VERSION%

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [x] Docker Compose is not installed.
    exit /b 1
)

for /f "tokens=*" %%i in ('docker-compose --version') do set COMPOSE_VERSION=%%i
echo [OK] Found: %COMPOSE_VERSION%
echo.

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo Creating .env file from .env.example...
    copy .env.example .env
    echo [OK] .env file created
) else (
    echo [OK] .env file already exists
)

echo.
echo Launching all services...
echo This may take a few minutes on first run...
echo.

docker-compose up --build

echo.
echo ======================================
echo Services are starting!
echo ======================================
echo.
echo Frontend:  http://localhost:3000
echo Backend:   http://localhost:8000
echo API Docs:  http://localhost:8000/docs
echo.
echo Create an account to get started!
echo.
pause
