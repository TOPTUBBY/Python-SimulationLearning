@echo off
setlocal EnableExtensions
cd /d "%~dp0"
echo ======================================================
echo SimulationLearning - Portable Builder - 11 websites
 echo Ten legacy EXEs use PyInstaller, HowItsWired uses Go.
echo ======================================================
echo.
where py >nul 2>&1
if not errorlevel 1 (
  set "PY=py -3"
) else (
  where python >nul 2>&1
  if errorlevel 1 (
    echo [ERROR] Python missing on the BUILD PC.
    pause
    exit /b 1
  )
  set "PY=python"
)
%PY% -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
  %PY% -m pip install "pyinstaller>=6,<7"
  if errorlevel 1 (pause & exit /b 1)
)
%PY% build_portable.py --all --mode bootstrap
if errorlevel 1 (
 echo [ERROR] The first 10 EXE builds failed.
 pause
 exit /b 1
)
where go >nul 2>&1
if errorlevel 1 (
 echo [ERROR] Go 1.23+ is needed on the BUILD PC for HowItsWired.
 echo Download from https://go.dev/dl/
 pause
 exit /b 1
)
set "SIM_BUILD_NO_PAUSE=1"
call "%~dp0HowItsWired\Build_Windows_EXE.bat"
if errorlevel 1 (
 echo [ERROR] HowItsWired EXE build failed.
 pause
 exit /b 1
)
echo [OK] All 11 EXEs built in Portable\EXE
pause
endlocal
