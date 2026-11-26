"""Bundle 11 portable executables (10 PyInstaller + one native Go) for a Release.

The bootstrap EXEs contain no original third-party website assets.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

PROJECTS = {
    "ESP32": 8121, "Arduino": 8122, "RoverKit": 8123, "Multimeter": 8124,
    "Protocol": 8125, "DesignedToScale": 8126, "RoboticsLab": 8127,
    "ByteSizedAlgorithms": 8128, "MoonLife": 8129, "ESP32Labs": 8130,
    "HowItsWired": 8131,
}


def package(directory: Path, output: Path) -> list[Path]:
    files = [directory / f"SimulationLearning-{project}-{port}.exe"
             for project, port in PROJECTS.items()]
    for p in files:
        if not p.is_file() or p.stat().st_size < 1024:
            raise FileNotFoundError(f"Missing compiled EXE: {p}")
        with p.open("rb") as stream:
            if stream.read(2) != b"MZ":
                raise ValueError(f"Invalid Windows executable: {p}")
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    with ZipFile(output, "w", ZIP_DEFLATED, compresslevel=6, allowZip64=True) as zipfile:
        for p in files:
            digest = hashlib.sha256(p.read_bytes()).hexdigest()
            lines.append(f"{digest}  {p.name}\n")
            zipfile.write(p, p.name)
        zipfile.writestr("SHA256SUMS.txt", "".join(lines))
        zipfile.writestr("README.txt", "SimulationLearning Portable 11 EXEs.\nDouble-click the selected EXE. Internet is needed on first launch.\nAssets are cached locally under %%LOCALAPPDATA%%\\SimulationLearning.\n")
    with ZipFile(output) as archive:
        broken = archive.testzip()
        if broken:
            raise IOError(f"ZIP integrity check failed: {broken}")
    return files


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    files = package(args.directory, args.output)
    print(f"Packed {len(files)} Windows EXEs: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
