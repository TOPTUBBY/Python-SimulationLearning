# Portable — ten standalone Windows programs

For regular Windows users: run [EXE/Download_All_EXEs.bat](EXE/Download_All_EXEs.bat) once to fetch the latest verified Release package into `Portable/EXE/`. Then double-click the desired EXE. **Python is not needed on the recipient PC.**

For developers: `Build_Portable_All.bat` builds all ten EXEs on Windows (Python + PyInstaller required on the builder only). Output goes to `Portable/EXE/`.

See [Portable EXE guide](docs/PORTABLE_EXE.md) and [QA checklist](docs/PORTABLE_QA_CHECKLIST.md). Bootstrap EXEs download the original website assets on first launch. They do not embed vendor files.
