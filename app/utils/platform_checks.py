"""Platform and environment checks for Windows integration."""

import shutil
import string
import subprocess
from pathlib import Path
from typing import List

try:
    import win32api
    import win32file
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

from app.utils.logger import get_logger

logger = get_logger("PlatformChecks")

def get_occupied_drive_letters() -> List[str]:
    """Return a list of occupied Windows drive letters (e.g., ['C:', 'D:'])."""
    occupied = []
    if HAS_WIN32:
        try:
            drives = win32api.GetLogicalDriveStrings()
            for drive in drives.split('\000'):
                if drive:
                    occupied.append(drive[:2].upper())
            return occupied
        except Exception as e:
            logger.warning(f"Failed to query drives via win32api: {e}")

    # Fallback checking path existence
    for letter in string.ascii_uppercase:
        drive_path = f"{letter}:\\"
        if Path(drive_path).exists():
            occupied.append(f"{letter}:")
    return occupied

def get_available_drive_letters() -> List[str]:
    """Return a list of available Windows drive letters in preferred descending order (Z: to D:)."""
    occupied = set(get_occupied_drive_letters())
    # Prefer high letters for virtual/network mounts: G:, H:, I:, J:, etc., or Z down to D
    candidates = [f"{ch}:" for ch in "GHIJKLMNOPQRSTUVWXYZ"]
    available = [d for d in candidates if d not in occupied]
    # Also append remaining letters if needed
    remaining = [f"{ch}:" for ch in "FED" if f"{ch}:" not in occupied and f"{ch}:" not in available]
    return available + remaining

def get_rclone_executable_path() -> str | None:
    """Return resolved rclone executable path (bundled or on system PATH)."""
    from app.utils.paths import BASE_DIR
    bundled = BASE_DIR / "bin" / "rclone" / "rclone.exe"
    if bundled.exists():
        return str(bundled)
    return shutil.which("rclone")

def is_rclone_installed() -> bool:
    """Check if rclone executable is found either bundled or on PATH."""
    return get_rclone_executable_path() is not None

def get_rclone_version() -> str | None:
    """Return rclone version string if installed."""
    exe = get_rclone_executable_path()
    if not exe:
        return None
    try:
        res = subprocess.run(
            [exe, "version"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5
        )
        first_line = res.stdout.strip().splitlines()[0]
        return first_line
    except Exception as e:
        logger.warning(f"Error checking rclone version: {e}")
        return None

def is_winfsp_installed() -> bool:
    """Check if WinFsp virtual filesystem driver is installed."""
    paths_to_check = [
        Path("C:/Program Files/WinFsp"),
        Path("C:/Program Files (x86)/WinFsp"),
    ]
    for p in paths_to_check:
        if p.exists() and (p / "bin").exists():
            return True

    # Check via sc.exe query
    try:
        res = subprocess.run(
            ["sc", "query", "winfsp-launcher"],
            capture_output=True,
            text=True,
            timeout=3
        )
        if "RUNNING" in res.stdout or "STOPPED" in res.stdout:
            return True
    except Exception:
        pass

    return False
