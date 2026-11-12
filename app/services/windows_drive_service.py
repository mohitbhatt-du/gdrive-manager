"""Low-level Windows filesystem and drive letter service."""

import os
import subprocess
from typing import Optional, Dict
from app.utils.logger import get_logger

try:
    import win32api
    import win32file
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

logger = get_logger("WindowsDriveService")

class WindowsDriveService:
    """Provides native Windows drive letter queries, Explorer invocation, and volume inspection."""

    @staticmethod
    def is_drive_ready(drive_letter: str) -> bool:
        """Check if Windows drive letter is ready and accessible."""
        letter = drive_letter.rstrip("\\")
        drive_path = f"{letter}\\"
        return os.path.exists(drive_path)

    @staticmethod
    def get_volume_info(drive_letter: str) -> Optional[Dict[str, str]]:
        """Query native Windows volume information (label, filesystem)."""
        letter = drive_letter.rstrip("\\")
        drive_path = f"{letter}\\"
        if not HAS_WIN32:
            return None

        try:
            info = win32api.GetVolumeInformation(drive_path)
            return {
                "volume_name": info[0],
                "serial_number": str(info[1]),
                "fs_name": info[4]  # e.g., 'WinFsp.rclone' or 'NTFS'
            }
        except Exception as e:
            logger.debug(f"Could not query volume information for {drive_path}: {e}")
            return None

    @staticmethod
    def open_in_explorer(drive_letter: str) -> bool:
        """Open Windows File Explorer at the assigned drive letter root."""
        letter = drive_letter.rstrip("\\")
        drive_path = f"{letter}\\"
        try:
            subprocess.Popen(["explorer.exe", drive_path])
            return True
        except Exception as e:
            logger.error(f"Failed to launch Explorer for {drive_path}: {e}")
            return False
