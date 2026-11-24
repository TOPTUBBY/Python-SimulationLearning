@echo off
setlocal
cd /d "%~dp0"
echo ===================================================
echo SimulationLearning - Portable EXE Builder (10 sites)
echo ===================================================
echo.
echo Requirement: Windows + Python + internet on build PC.
echo Output: dist\portable\SimulationLearning-*-*.exe
echo No Python is required on recipient PCs.
echo Websites download on FIRST RUN on recipient PC.
echo.
where py >nul 2>&1
if not errorlevel 1 (
  set "PY=py -3"
) else (
  where python >nul 2>&1
  if errorlevel 1 (
    echo [ERROR] Python is required on this BUILD PC only.
    pause
    exit /b 1
  )
  set "PY=python"
)
%PY% -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
  echo Installing PyInstaller on BUILD PC only...
  %PY% -m pip install "pyinstaller>=6,<7"
  if errorlevel 1 (
    echo [ERROR] Could not install PyInstaller.
    pause
    exit /b 1
  )
)
%PY% tools\build_portable.py --all --mode bootstrap
set "CODE=%errorlevel%"
echo.
if not "%CODE%"=="0" (
  echo [WARN] Some EXEs could not be built. Review output and retry.
) else (
  echo [OK] Check dist\portable for 10 standalone EXE files.
)
pause
exit /b %CODE%
