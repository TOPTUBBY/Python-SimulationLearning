@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>&1
if not errorlevel 1 (
  py -3 build_portable.py --all --check
) else (
  python build_portable.py --all --check
)
pause
