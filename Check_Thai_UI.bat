@echo off
setlocal
cd /d "%~dp0"
title SimulationLearning - Thai UI Checks
set "PYEXE="
where py >nul 2>&1
if not errorlevel 1 set "PYEXE=py -3"
if not defined PYEXE (
  where python >nul 2>&1
  if not errorlevel 1 set "PYEXE=python"
)
if not defined PYEXE (
  echo [ERROR] Python 3.8+ is required.
  pause
  exit /b 1
)
echo Running Thai UI tests for ports 8121-8128 ...
%PYEXE% -m unittest discover -s tests -p test_thai_ui.py -v
if errorlevel 1 (
  echo [FAIL] Thai UI tests failed.
  pause
  exit /b 1
)
echo [PASS] Thai UI checks completed.
pause
endlocal
