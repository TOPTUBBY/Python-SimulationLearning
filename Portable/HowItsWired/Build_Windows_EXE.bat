@echo off
setlocal
cd /d "%~dp0"
where go >nul 2>&1
if errorlevel 1 (
 echo Go 1.23+ required only for the build computer: https://go.dev/dl/
 if not defined SIM_BUILD_NO_PAUSE pause
 exit /b 1
)
set "GOOS=windows"
set "GOARCH=amd64"
set "CGO_ENABLED=0"
if not exist "..\EXE" mkdir "..\EXE"
go build -trimpath -ldflags "-s -w -H windowsgui" -o "..\EXE\SimulationLearning-HowItsWired-8131.exe" .
if errorlevel 1 (if not defined SIM_BUILD_NO_PAUSE pause & exit /b 1)
echo Built Portable EXE successfully.
if not defined SIM_BUILD_NO_PAUSE pause
