"""Small fixed entrypoint used to build each self-contained Windows app."""
from pathlib import Path
import sys

ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Launcher-Server" / "tools"))
from portable_launcher import main

if __name__ == "__main__":
    raise SystemExit(main(bundle_root=ROOT))
