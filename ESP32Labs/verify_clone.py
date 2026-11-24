"""ESP32 Labs entrypoint. Shared implementation: ../tools/esp_labs_runtime.py"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from esp_labs_runtime import main

if __name__ == "__main__":
    raise SystemExit(main("check", Path(__file__).resolve().parent))
