"""How It's Wired: Windows-safe cache slot launcher."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from how_its_wired_runtime import main

if __name__ == "__main__":
    raise SystemExit(main("mirror", Path(__file__).resolve().parent))
