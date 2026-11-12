"""Application paths and directory management."""

import os
import sys
from pathlib import Path


def get_base_dir() -> Path:
    """Return the base directory of the application."""
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).parent
        internal_dir = exe_dir / "_internal"
        if internal_dir.exists():
            return internal_dir
        return exe_dir
    return Path(__file__).resolve().parent.parent.parent


def get_app_dir() -> Path:
    """Return the root directory containing the executable or source repository."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent.parent


BASE_DIR = get_base_dir()
APP_DIR = BASE_DIR / "app"
ASSETS_DIR = BASE_DIR / "assets"
ICONS_DIR = ASSETS_DIR / "icons"


def get_app_data_dir() -> Path:
    """Return the Windows LocalAppData directory for user-specific data."""
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        path = Path(local_app_data) / "GDriveManager"
    else:
        path = BASE_DIR / "data"
    path.mkdir(parents=True, exist_ok=True)
    return path


DATA_DIR = get_app_data_dir()
LOGS_DIR = get_app_data_dir() / "logs"


def ensure_directories():
    """Ensure runtime directories exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    ICONS_DIR.mkdir(parents=True, exist_ok=True)
