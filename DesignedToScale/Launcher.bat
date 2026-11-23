@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title SimulationLearning - Designed to Scale - Launcher.bat - Port 8126
set "PYEXE="
where py >nul 2>&1
if not errorlevel 1 (
    py -3 -c "import sys; assert sys.version_info >= (3,8)" >nul 2>&1
    if not errorlevel 1 set "PYEXE=py -3"
)
if not defined PYEXE (
    where python >nul 2>&1
    if not errorlevel 1 (
        python -c "import sys; assert sys.version_info >= (3,8)" >nul 2>&1
        if not errorlevel 1 set "PYEXE=python"
    )
)
if not defined PYEXE (
    echo [ERROR] Python 3.8+ was not found. Install from python.org
    pause
    exit /b 1
)
%PYEXE% "%~dp0server.py"
if errorlevel 1 (
    echo.
    echo [ERROR] Command failed. Read the message above.
    pause
)
endlocal
