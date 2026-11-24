@echo off
setlocal EnableExtensions
cd /d "%~dp0"
where py >nul 2>&1
if not errorlevel 1 (
  py -3 -m unittest discover -s tests -v
) else (
  python -m unittest discover -s tests -v
)
if errorlevel 1 (
  echo [ERROR] Test failed.
  pause
  exit /b 1
)
echo.
echo [PASS] Offline tests completed.
pause
