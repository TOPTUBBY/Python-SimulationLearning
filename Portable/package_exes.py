"""Validate and pack ten Windows EXEs into a release ZIP."""
from __future__ import annotations
import argparse
import hashlib
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

PROJECTS = {"ESP32":8121, "Arduino":8122, "RoverKit":8123, "Multimeter":8124,
            "Protocol":8125, "DesignedToScale":8126, "RoboticsLab":8127,
            "ByteSizedAlgorithms":8128, "MoonLife":8129, "ESP32Labs":8130}

def package(directory, output):
    directory, output = Path(directory), Path(output)
    files = [directory / ("SimulationLearning-%s-%d.exe" % (site, port))
             for site, port in PROJECTS.items()]
    for file in files:
        if not file.is_file() or file.stat().st_size < 1024:
            raise FileNotFoundError(str(file))
        with file.open("rb") as f:
            if f.read(2) != b"MZ":
                raise ValueError("Not a Windows executable: " + str(file))
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", ZIP_DEFLATED, compresslevel=6, allowZip64=True) as dest:
        sums = []
        for file in files:
            with file.open("rb") as source:
                sha = hashlib.sha256()
                for block in iter(lambda: source.read(1048576), b""):
                    sha.update(block)
            sums.append(sha.hexdigest() + "  " + file.name + "\n")
            dest.write(file, file.name)
        dest.writestr("SHA256SUMS.txt", "".join(sums))
        dest.writestr("README.txt", "SimulationLearning Portable 10 EXEs. First launch requires internet. No Python installation needed.\n")
    with ZipFile(output) as result:
        if result.testzip() is not None:
            raise IOError("Invalid release ZIP")
    return files

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    a = parser.parse_args()
    print("Packaged", len(package(a.directory, a.output)), "Windows EXEs")
