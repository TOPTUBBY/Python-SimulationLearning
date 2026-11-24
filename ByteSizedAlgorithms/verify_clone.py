"""Project entrypoint. Implementation lives in ../tools/clone_runtime.py."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from thai_runtime import main

if __name__ == "__main__":
    raise SystemExit(main("check", Path(__file__).resolve().parent))
