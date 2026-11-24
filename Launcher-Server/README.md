# Launcher-Server — ten Python websites

Contains the original launcher/server edition with the same ten sources, ports and Thai localization. Requires **Python 3.8+ on Windows**. Double-click any `<Site>/Launcher.bat`, or use `Launch_All.bat` for all ten.

`Update_All.bat` refreshes downloaded website assets; `Check_All.bat` validates local caches; `Check_Thai_UI.bat` tests the Thai localization interface. The project folders share `tools/` and `localization/` and should not be separated.

Ports: ESP32 8121 · Arduino 8122 · RoverKit 8123 · Multimeter 8124 · Protocol 8125 · DesignedToScale 8126 · RoboticsLab 8127 · ByteSizedAlgorithms 8128 · MoonLife 8129 · ESP32Labs 8130.

Run tests from repository root: `python -m unittest discover -s Launcher-Server/tests -v`.
