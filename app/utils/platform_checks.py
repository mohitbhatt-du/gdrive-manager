"""Platform and environment checks for Windows integration."""

import shutil
import string
import subprocess
from pathlib import Path

try:
    import win32api

    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

from app.utils.logger import get_logger

logger = get_logger("PlatformChecks")


def get_occupied_drive_letters() -> list[str]:
    """Return a list of occupied Windows drive letters (e.g., ['C:', 'D:'])."""
    occupied = []
    if HAS_WIN32:
        try:
            drives = win32api.GetLogicalDriveStrings()
            for drive in drives.split("\000"):
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


def get_available_drive_letters() -> list[str]:
    """Return a list of available Windows drive letters in preferred descending order (Z: to D:)."""
    occupied = set(get_occupied_drive_letters())
    # Prefer high letters for virtual/network mounts: G:, H:, I:, J:, etc., or Z down to D
    candidates = [f"{ch}:" for ch in "GHIJKLMNOPQRSTUVWXYZ"]
    available = [d for d in candidates if d not in occupied]
    # Also append remaining letters if needed
    remaining = [f"{ch}:" for ch in "FED" if f"{ch}:" not in occupied and f"{ch}:" not in available]
    return available + remaining


def get_rclone_executable_path() -> str | None:
    """Return resolved rclone executable path across bundled, AppData, system PATH, and standard Windows directories."""
    import os
    import sys

    from app.utils.paths import BASE_DIR, get_app_data_dir

    candidates: list[Path] = []

    # 1. sys._MEIPASS (PyInstaller onefile extraction)
    if hasattr(sys, "_MEIPASS"):
        candidates.append(Path(sys._MEIPASS) / "bin" / "rclone" / "rclone.exe")

    # 2. PyInstaller onedir internal directory
    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).parent
        candidates.append(exe_dir / "_internal" / "bin" / "rclone" / "rclone.exe")
        candidates.append(exe_dir / "bin" / "rclone" / "rclone.exe")

    # 3. BASE_DIR bundled path
    candidates.append(BASE_DIR / "bin" / "rclone" / "rclone.exe")

    # 4. LocalAppData user installation / downloaded binary
    candidates.append(get_app_data_dir() / "bin" / "rclone" / "rclone.exe")

    # 5. Check each explicit path
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return str(candidate)

    # 6. System PATH via shutil.which
    path_hit = shutil.which("rclone")
    if path_hit:
        return path_hit

    # 7. Standard Windows installation directories
    pf = os.environ.get("ProgramFiles", "C:\\Program Files")
    pf86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
    local_app = os.environ.get("LOCALAPPDATA", "")

    fallback_paths = [
        Path(pf) / "rclone" / "rclone.exe",
        Path(pf86) / "rclone" / "rclone.exe",
        Path(local_app) / "Programs" / "rclone" / "rclone.exe" if local_app else None,
        Path("C:/rclone/rclone.exe"),
    ]

    for p in fallback_paths:
        if p and p.exists() and p.is_file():
            return str(p)

    return None


def is_rclone_installed() -> bool:
    """Check if rclone executable is found either bundled or on PATH."""
    return get_rclone_executable_path() is not None


def get_rclone_version() -> str | None:
    """Return rclone version string if installed."""
    exe = get_rclone_executable_path()
    if not exe:
        return None
    try:
        res = subprocess.run([exe, "version"], capture_output=True, text=True, check=True, timeout=5)
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
        res = subprocess.run(["sc", "query", "winfsp-launcher"], capture_output=True, text=True, timeout=3)
        if "RUNNING" in res.stdout or "STOPPED" in res.stdout:
            return True
    except Exception:
        pass

    return False
