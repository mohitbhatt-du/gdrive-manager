"""Windows startup registry integration."""

import sys
import winreg
from pathlib import Path

from app.utils.logger import get_logger

logger = get_logger("StartupManager")

REG_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "GDriveManager"


def get_launch_command() -> str:
    """Return command string to execute GDrive Manager on Windows startup."""
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'
    python_exe = sys.executable
    main_py = Path(__file__).resolve().parent.parent.parent / "main.py"
    return f'"{python_exe}" "{main_py}"'


def is_startup_enabled() -> bool:
    """Check if application is registered in Windows startup registry."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY, 0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, APP_NAME)
            return bool(value)
    except FileNotFoundError:
        return False
    except Exception as e:
        logger.debug(f"Could not read startup registry: {e}")
        return False


def set_startup_enabled(enabled: bool) -> bool:
    """Enable or disable GDrive Manager startup entry in Windows registry."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY, 0, winreg.KEY_SET_VALUE) as key:
            if enabled:
                cmd = get_launch_command()
                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, cmd)
                logger.info(f"Registered GDrive Manager in Windows startup: {cmd}")
            else:
                try:
                    winreg.DeleteValue(key, APP_NAME)
                    logger.info("Removed GDrive Manager from Windows startup.")
                except FileNotFoundError:
                    pass
        return True
    except Exception as e:
        logger.error(f"Failed to update startup registry: {e}")
        return False
