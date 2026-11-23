@echo off
setlocal
cd /d "%~dp0"
call "%~dp0ESP32\Check_Clone.bat"
call "%~dp0Arduino\Check_Clone.bat"
call "%~dp0RoverKit\Check_Clone.bat"
call "%~dp0Multimeter\Check_Clone.bat"
call "%~dp0Protocol\Check_Clone.bat"
call "%~dp0DesignedToScale\Check_Clone.bat"
call "%~dp0RoboticsLab\Check_Clone.bat"
echo Finished.
endlocal
