# Portable EXE — 11 Windows applications

**For everyday users:** go to [`EXE/`](EXE/) and run `Download_All_EXEs.bat` to download all eleven Windows applications from GitHub Releases. After downloading, simply double-click the desired EXE. No Python/terminal is required on the end-user PC.

**For developers:** run `Build_Portable_All.bat` on Windows to build eleven EXEs locally, or use `python Portable/build_portable.py --all --mode bootstrap` from the repository root. Build results are written to `Portable/EXE/`.

Details and prerequisites: [Portable EXE guide](docs/PORTABLE_EXE.md) · [QA checklist](docs/PORTABLE_QA_CHECKLIST.md).

This mode downloads original public website assets on the first run; it does not distribute vendor content in the executable. The bundled Thai translations and per-user translation cache remain supported.


## How It’s Wired native Windows EXE (8131)

`Portable/EXE/SimulationLearning-HowItsWired-8131.exe` is a single-file **native Windows x64 program**, built from the separately authored Go source in `Portable/HowItsWired/`. No Python or Go installation is required on recipient machines. On first launch it downloads the original public frontend from `https://how-its-wired.vercel.app/` into `%LOCALAPPDATA%\SimulationLearning\HowItsWired\site\` then runs a server on `127.0.0.1:8131` and opens the `/lead-load` page. A small Windows control message stays visible: **click OK to stop the server**. Unlike the ten older EXEs, this new application is Go-based for cross-compiled offline build. It supports the same Thai/Original browser overlay.

For developers, run `Portable/HowItsWired/Build_Windows_EXE.bat` with Go 1.23+, or `go build` from the `Portable/HowItsWired/` directory. Windows x64 build is included in the approved local preview ZIP; the builder is not needed to run it. **Source is integrated for v1.7.0. The compiled executable is tested for identity/resources by CI; complete live-browser behavior still requires user validation.**
