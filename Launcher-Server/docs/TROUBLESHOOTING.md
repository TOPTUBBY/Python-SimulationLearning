# Troubleshooting

## CMD opens then closes

Install Python 3.8 or newer and enable its PATH entry. In Windows CMD run `py -3 --version` or `python --version`. Double-click `Launcher.bat` again; errors pause for inspection.

## Browser is blank/black

Run the site's `Check_Clone.bat`; if it reports missing JS/CSS or manifest, connect to the internet and run `Update_Clone.bat`, then restart Launcher. Try hard refresh Ctrl+Shift+R, or an InPrivate window to eliminate old service-worker/browser cache. The server sends `Cache-Control: no-store` on every local file.

## First-run download fails

The original Vercel site must be reachable from that PC. Corporate proxy/TLS inspection, VPN, firewall, upstream site changes, or externally hosted content can interfere. The mirror retains a previously working cache if an update fails; check warnings printed in the console. Source assets must not be redistributed without permission.

## Port already in use

Each default port is fixed to one site (ESP32 8121, Arduino 8122, RoverKit 8123, Multimeter 8124, Protocol 8125, DesignedToScale 8126). Close old CMD windows; check `netstat -ano | findstr :8121` and map PID in Task Manager if needed. A different app using the port will not be overridden.

## Offline lessons not complete

Some assets load only when you visit a specific lesson, and some features call network APIs. Connect to the internet, visit the desired lessons so missing resources can be cached on demand, then retest offline. This toolkit cannot guarantee complete offline coverage or exact functionality for every upstream version.

## Changes to original websites

Run `Update_Clone.bat`; it downloads to a staging folder and swaps it only if entrypoint checks pass. Do not manually copy its `site/` into Git.
