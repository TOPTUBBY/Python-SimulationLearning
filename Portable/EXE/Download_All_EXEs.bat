@echo off
setlocal EnableExtensions
cd /d "%~dp0"
echo Downloading SimulationLearning v1.7.0 Portable EXEs (11 sites)...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; $u='https://github.com/TOPTUBBY/Python-SimulationLearning/releases/download/v1.7.0/SimulationLearning_Portable_11_EXEs.zip'; $z=Join-Path $env:TEMP 'SimulationLearning_Portable_11_EXEs.zip'; Invoke-WebRequest -Uri $u -OutFile $z -UseBasicParsing; Expand-Archive -Path $z -DestinationPath (Get-Location).Path -Force; Remove-Item -LiteralPath $z; Write-Host '[OK] Eleven EXEs extracted into Portable/EXE'"
if errorlevel 1 (
  echo [ERROR] Could not download. Check your internet connection or the GitHub Release page.
) else (
  echo [DONE] Portable EXEs are ready in this folder.
)
pause
