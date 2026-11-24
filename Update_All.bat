@echo off
setlocal
cd /d "%~dp0"
call "%~dp0ESP32\Update_Clone.bat"
call "%~dp0Arduino\Update_Clone.bat"
call "%~dp0RoverKit\Update_Clone.bat"
call "%~dp0Multimeter\Update_Clone.bat"
call "%~dp0Protocol\Update_Clone.bat"
call "%~dp0DesignedToScale\Update_Clone.bat"
call "%~dp0RoboticsLab\Update_Clone.bat"
call "%~dp0ByteSizedAlgorithms\Update_Clone.bat"
echo Finished.
endlocal
