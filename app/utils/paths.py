"""Application paths and directory management."""

from pathlib import Path
import os
import sys

def get_base_dir() -> Path:
    """Return the base directory of the application."""
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent.parent

BASE_DIR = get_base_dir()
APP_DIR = BASE_DIR / "app"
ASSETS_DIR = BASE_DIR / "assets"
ICONS_DIR = ASSETS_DIR / "icons"
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

def get_app_data_dir() -> Path:
    """Return the Windows LocalAppData directory for user-specific data."""
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        path = Path(local_app_data) / "GDriveManager"
    else:
        path = DATA_DIR
    path.mkdir(parents=True, exist_ok=True)
    return path

def ensure_directories():
    """Ensure runtime directories exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    ICONS_DIR.mkdir(parents=True, exist_ok=True)
