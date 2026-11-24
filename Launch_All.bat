@echo off
setlocal
cd /d "%~dp0"
echo Starting all ten local sites...
start "ESP32" cmd /c ""%~dp0ESP32\Launcher.bat""
start "Arduino" cmd /c ""%~dp0Arduino\Launcher.bat""
start "RoverKit" cmd /c ""%~dp0RoverKit\Launcher.bat""
start "Multimeter" cmd /c ""%~dp0Multimeter\Launcher.bat""
start "Protocol" cmd /c ""%~dp0Protocol\Launcher.bat""
start "DesignedToScale" cmd /c ""%~dp0DesignedToScale\Launcher.bat""
start "RoboticsLab" cmd /c ""%~dp0RoboticsLab\Launcher.bat""
start "ByteSizedAlgorithms" cmd /c ""%~dp0ByteSizedAlgorithms\Launcher.bat""
start "MoonLife" cmd /c ""%~dp0MoonLife\Launcher.bat""
start "ESP32Labs" cmd /c ""%~dp0ESP32Labs\Launcher.bat""
echo Each server has its own CMD window.
endlocal
