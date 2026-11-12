"""Rclone cloud storage engine service managing binaries, configuration, and remotes."""

import json
import os
import shutil
import subprocess
import zipfile
import urllib.request
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple

from app.utils.paths import BASE_DIR, get_app_data_dir
from app.utils.logger import get_logger

logger = get_logger("RcloneService")

class RcloneService:
    """Manages rclone executable discovery, config files, and remote operations."""

    def __init__(self, custom_binary_path: Optional[str] = None, custom_config_path: Optional[str] = None):
        self.custom_binary = custom_binary_path
        self.custom_config = custom_config_path
        self._rclone_exe: Optional[str] = None
        self._config_path: Optional[Path] = None

    @property
    def config_path(self) -> Path:
        """Return path to isolated application rclone.conf."""
        if self._config_path:
            return self._config_path
        if self.custom_config:
            self._config_path = Path(self.custom_config)
        else:
            self._config_path = get_app_data_dir() / "rclone.conf"
        self._config_path.parent.mkdir(parents=True, exist_ok=True)
        return self._config_path

    @property
    def rclone_exe(self) -> Optional[str]:
        """Resolve rclone executable path across custom, bundled, and system PATH."""
        if self._rclone_exe and Path(self._rclone_exe).exists():
            return self._rclone_exe

        # 1. Custom configured binary
        if self.custom_binary and Path(self.custom_binary).exists():
            self._rclone_exe = self.custom_binary
            return self._rclone_exe

        # 2. Bundled in bin/rclone/rclone.exe
        bundled = BASE_DIR / "bin" / "rclone" / "rclone.exe"
        if bundled.exists():
            self._rclone_exe = str(bundled)
            return self._rclone_exe

        # 3. System PATH
        system_rclone = shutil.which("rclone")
        if system_rclone:
            self._rclone_exe = system_rclone
            return self._rclone_exe

        return self._rclone_exe

    @rclone_exe.setter
    def rclone_exe(self, value: Optional[str]):
        self._rclone_exe = value

    @rclone_exe.deleter
    def rclone_exe(self):
        self._rclone_exe = None

    def is_available(self) -> bool:
        """Check whether rclone executable is found and executable."""
        exe = self.rclone_exe
        if not exe:
            return False
        try:
            res = subprocess.run([exe, "version"], capture_output=True, text=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def get_version(self) -> Optional[str]:
        """Return first line of rclone version output."""
        exe = self.rclone_exe
        if not exe:
            return None
        try:
            res = subprocess.run([exe, "version"], capture_output=True, text=True, timeout=5)
            if res.returncode == 0:
                return res.stdout.strip().splitlines()[0]
        except Exception as e:
            logger.warning(f"Failed to query rclone version: {e}")
        return None

    def execute_cmd(self, args: List[str], timeout: int = 30) -> Tuple[int, str, str]:
        """Execute rclone subprocess safely using argument list."""
        exe = self.rclone_exe
        if not exe:
            raise FileNotFoundError("rclone executable not found. Please install rclone.")

        cmd = [exe, "--config", str(self.config_path)] + args
        logger.debug(f"Running rclone command: {' '.join(cmd)}")

        res = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        )
        return res.returncode, res.stdout, res.stderr

    def list_remotes(self) -> List[str]:
        """List configured remotes in rclone.conf."""
        if not self.config_path.exists():
            return []
        try:
            code, stdout, stderr = self.execute_cmd(["listremotes"])
            if code == 0:
                remotes = [r.strip().rstrip(":") for r in stdout.strip().splitlines() if r.strip()]
                return remotes
            logger.warning(f"rclone listremotes returned code {code}: {stderr}")
            return []
        except Exception as e:
            logger.error(f"Error listing rclone remotes: {e}")
            return []

    def get_account_storage_quota(self, remote_name: str) -> Dict[str, int]:
        """Query real cloud storage quota via 'rclone about <remote>: --json'."""
        target = f"{remote_name}:"
        try:
            code, stdout, stderr = self.execute_cmd(["about", target, "--json"], timeout=15)
            if code == 0 and stdout:
                data = json.loads(stdout)
                return {
                    "total": data.get("total", 0),
                    "used": data.get("used", 0),
                    "trashed": data.get("trashed", 0),
                    "free": data.get("free", 0),
                }
            logger.warning(f"Could not retrieve quota for {target}: {stderr}")
        except Exception as e:
            logger.error(f"Error querying quota for {remote_name}: {e}")
        return {"total": 0, "used": 0, "trashed": 0, "free": 0}

    def delete_remote(self, remote_name: str) -> bool:
        """Remove remote configuration from rclone.conf."""
        try:
            code, stdout, stderr = self.execute_cmd(["config", "delete", remote_name])
            return code == 0
        except Exception as e:
            logger.error(f"Failed to delete remote {remote_name}: {e}")
            return False

    def download_bundled_rclone(self, progress_callback=None) -> bool:
        """Download official rclone Windows x64 standalone zip and extract to bin/rclone/."""
        url = "https://downloads.rclone.org/rclone-current-windows-amd64.zip"
        dest_dir = BASE_DIR / "bin" / "rclone"
        dest_dir.mkdir(parents=True, exist_ok=True)
        zip_path = dest_dir / "rclone.zip"

        try:
            logger.info(f"Downloading rclone from {url}...")
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) GDriveManager"}
            )
            with urllib.request.urlopen(req) as resp, open(zip_path, "wb") as out_f:
                shutil.copyfileobj(resp, out_f)

            logger.info("Extracting rclone...")
            with zipfile.ZipFile(zip_path, "r") as z:
                # Find rclone.exe inside subfolder
                for name in z.namelist():
                    if name.endswith("rclone.exe"):
                        with z.open(name) as src, open(dest_dir / "rclone.exe", "wb") as dst:
                            shutil.copyfileobj(src, dst)
                        break

            if zip_path.exists():
                zip_path.unlink()

            exe = dest_dir / "rclone.exe"
            if exe.exists():
                self._rclone_exe = str(exe)
                logger.info(f"rclone successfully installed to {exe}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to download rclone: {e}")
            if zip_path.exists():
                try:
                    zip_path.unlink()
                except Exception:
                    pass
            return False
