"""Standalone Distribution Build Forwarder for GDrive Manager."""

import sys
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scripts.build import main

if __name__ == "__main__":
    main()
