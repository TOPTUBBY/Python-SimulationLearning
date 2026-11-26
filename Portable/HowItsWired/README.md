# How It's Wired — Native Windows Portable EXE (Port 8131)

This release adds a **single Windows 64-bit EXE** alongside the existing Python Launcher-Server distribution.

- Executable: `../EXE/SimulationLearning-HowItsWired-8131.exe`
- Web page: `http://127.0.0.1:8131/lead-load`
- Original source: https://how-its-wired.vercel.app/lead-load
- Cache/logs: `%LOCALAPPDATA%\SimulationLearning\HowItsWired\`
- Thai UI: TH / Original; optional online translation is off by default.
- The original site assets are **not embedded**. They are downloaded on first launch to each user's own PC.

## For regular users

Double-click the EXE. It starts the local HTTP server without Python, then opens the page in the default browser. If a cache has not been created, the browser shows a progress page while assets are downloaded. Keep the small Windows control message open while using the site; **click OK to stop the server**. If you relaunch while it is still running, it simply opens the current local site.

## For developers

Built using native Go instead of PyInstaller so the **actual Windows x64 executable can be cross-compiled** and included in the release package without altering the existing Python/PyInstaller apps.

Windows builder: run `Build_Windows_EXE.bat` with Go 1.23+ installed. Cross-platform command from this directory:

```bash
GOOS=windows GOARCH=amd64 CGO_ENABLED=0 go build -trimpath \
  -ldflags='-s -w -H windowsgui' \
  -o ../EXE/SimulationLearning-HowItsWired-8131.exe .
```

Windows CI startup check (no real website needed):

```powershell
.\SimulationLearning-HowItsWired-8131.exe --self-test-output "$env:TEMP\howitswired-smoke.json"
Get-Content "$env:TEMP\howitswired-smoke.json"
```

The self-test checks executable identity and embedded language resources; it **does not** validate 3D interactions or the live upstream mirror. The first-use download and Windows UI remain to be tested by the user.

## License and offline limits

This EXE embeds our own HTTP server/localization assets, not the third-party website JavaScript or models. An internet connection is required for the initial download; resources referenced dynamically and online translation may require internet later. The original website content belongs to its respective owner.
