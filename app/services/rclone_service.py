"""Rclone cloud storage engine service managing binaries, configuration, and remotes."""

import json
import os
import shutil
import subprocess
import urllib.request
import zipfile
from pathlib import Path

from app.utils.logger import get_logger
from app.utils.paths import get_app_data_dir
from app.utils.platform_checks import get_rclone_executable_path

logger = get_logger("RcloneService")


class RcloneService:
    """Manages rclone executable discovery, config files, and remote operations."""

    def __init__(self, custom_binary_path: str | None = None, custom_config_path: str | None = None):
        self.custom_binary = custom_binary_path
        self.custom_config = custom_config_path
        self._rclone_exe: str | None = None
        self._config_path: Path | None = None
        self._is_available: bool | None = None

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
    def rclone_exe(self) -> str | None:
        """Resolve rclone executable path across custom, bundled, AppData, and system PATH."""
        if self._rclone_exe and Path(self._rclone_exe).exists():
            return self._rclone_exe

        # 1. Custom configured binary
        if self.custom_binary and Path(self.custom_binary).exists():
            self._rclone_exe = self.custom_binary
            return self._rclone_exe

        # 2. Check platform discovery (bundled _internal, BASE_DIR, AppData, PATH)
        discovered = get_rclone_executable_path()
        if discovered:
            self._rclone_exe = discovered
            return self._rclone_exe

        return None

    @rclone_exe.setter
    def rclone_exe(self, value: str | None):
        self._rclone_exe = value
        self._is_available = None

    @rclone_exe.deleter
    def rclone_exe(self):
        self._rclone_exe = None
        self._is_available = None

    def is_available(self) -> bool:
        """Check whether rclone executable is found and executable."""
        if self._is_available is True:
            return True

        exe = self.rclone_exe
        if not exe or not Path(exe).is_file():
            self._is_available = False
            return False

        try:
            flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            res = subprocess.run(
                [exe, "version"],
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                creationflags=flags,
                timeout=10,
            )
            self._is_available = res.returncode == 0
            return self._is_available
        except Exception as e:
            logger.warning(f"rclone is_available check failed: {e}")
            self._is_available = False
            return False

    def get_version(self) -> str | None:
        """Return first line of rclone version output."""
        exe = self.rclone_exe
        if not exe or not Path(exe).is_file():
            return None
        try:
            flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            res = subprocess.run(
                [exe, "version"],
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                creationflags=flags,
                timeout=10,
            )
            if res.returncode == 0:
                self._is_available = True
                lines = res.stdout.strip().splitlines()
                return lines[0] if lines else "rclone"
        except Exception as e:
            logger.warning(f"Failed to query rclone version: {e}")
        return None

    def execute_cmd(self, args: list[str], timeout: int = 30) -> tuple[int, str, str]:
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
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        return res.returncode, res.stdout, res.stderr

    def list_remotes(self) -> list[str]:
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

    def get_account_storage_quota(self, remote_name: str) -> dict[str, int]:
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

    def download_bundled_rclone(self, dest_dir: Path | None = None, progress_callback=None) -> bool:
        """Download official rclone Windows x64 standalone zip and extract to safe location.

        If dest_dir is not specified, defaults to get_app_data_dir() / 'bin' / 'rclone' to ensure
        clean user-level write permissions even when running inside Program Files.
        """
        url = "https://downloads.rclone.org/rclone-current-windows-amd64.zip"
        if dest_dir is None:
            dest_dir = get_app_data_dir() / "bin" / "rclone"
        dest_dir.mkdir(parents=True, exist_ok=True)
        zip_path = dest_dir / "rclone.zip"

        try:
            logger.info(f"Downloading rclone from {url} to {dest_dir}...")
            req = urllib.request.Request(
                url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) GDriveManager"}
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
                self._is_available = True
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

    def list_directory(
        self, remote_name: str, remote_path: str = "", shared_with_me: bool = False
    ) -> list[dict]:
        """List files and folders in remote path using 'rclone lsjson'.

        Supports browsing remote directories without mounting virtual drives,
        including Google Drive 'Shared with me' files.
        """
        if remote_name.startswith("sample") or remote_name == "mock_remote":
            return self._get_sample_directory(remote_path, shared_with_me)

        clean_path = remote_path.strip("/\\").replace("\\", "/")
        target = f"{remote_name}:{clean_path}" if clean_path else f"{remote_name}:"

        args = ["lsjson", target, "--max-depth", "1"]
        if shared_with_me:
            args.append("--drive-shared-with-me")

        try:
            code, stdout, stderr = self.execute_cmd(args, timeout=30)
            if code == 0 and stdout:
                raw_items = json.loads(stdout)
                if isinstance(raw_items, list):
                    items: list[dict] = [i for i in raw_items if isinstance(i, dict)]
                    # Sort: directories first (alphabetical), then files (alphabetical)
                    items.sort(key=lambda x: (not x.get("IsDir", False), str(x.get("Name", "")).lower()))
                    return items
            logger.warning(f"rclone lsjson failed for {target} (code {code}): {stderr}")
            return []
        except Exception as e:
            logger.error(f"Failed to list directory for {remote_name}: {e}")
            return []

    def _get_sample_directory(self, remote_path: str = "", shared_with_me: bool = False) -> list[dict]:
        """Return rich mock files and directories for preview or sample mode."""
        clean_path = remote_path.strip("/\\").replace("\\", "/")
        if shared_with_me:
            return [
                {
                    "Path": "Shared Team Project",
                    "Name": "Shared Team Project",
                    "Size": -1,
                    "MimeType": "inode/directory",
                    "ModTime": "2026-11-10T14:20:00Z",
                    "IsDir": True,
                    "ID": "shared_f1",
                },
                {
                    "Path": "Q4 Quarterly Presentation.pptx",
                    "Name": "Q4 Quarterly Presentation.pptx",
                    "Size": 14680064,
                    "MimeType": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    "ModTime": "2026-11-11T09:15:00Z",
                    "IsDir": False,
                    "ID": "shared_f2",
                },
                {
                    "Path": "Architecture Design Review.pdf",
                    "Name": "Architecture Design Review.pdf",
                    "Size": 3840212,
                    "MimeType": "application/pdf",
                    "ModTime": "2026-11-12T10:00:00Z",
                    "IsDir": False,
                    "ID": "shared_f3",
                },
                {
                    "Path": "Client Contract Agreement.docx",
                    "Name": "Client Contract Agreement.docx",
                    "Size": 524288,
                    "MimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    "ModTime": "2026-11-09T18:30:00Z",
                    "IsDir": False,
                    "ID": "shared_f4",
                },
            ]
        if not clean_path:
            return [
                {
                    "Path": "Documents",
                    "Name": "Documents",
                    "Size": -1,
                    "MimeType": "inode/directory",
                    "ModTime": "2026-11-10T10:00:00Z",
                    "IsDir": True,
                    "ID": "mock_d1",
                },
                {
                    "Path": "Projects",
                    "Name": "Projects",
                    "Size": -1,
                    "MimeType": "inode/directory",
                    "ModTime": "2026-11-08T16:45:00Z",
                    "IsDir": True,
                    "ID": "mock_d2",
                },
                {
                    "Path": "Photos & Media",
                    "Name": "Photos & Media",
                    "Size": -1,
                    "MimeType": "inode/directory",
                    "ModTime": "2026-11-05T12:30:00Z",
                    "IsDir": True,
                    "ID": "mock_d3",
                },
                {
                    "Path": "Financial Forecast 2026.xlsx",
                    "Name": "Financial Forecast 2026.xlsx",
                    "Size": 2457600,
                    "MimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    "ModTime": "2026-11-12T08:00:00Z",
                    "IsDir": False,
                    "ID": "mock_f1",
                },
                {
                    "Path": "Annual Report.pdf",
                    "Name": "Annual Report.pdf",
                    "Size": 5242880,
                    "MimeType": "application/pdf",
                    "ModTime": "2026-11-11T15:20:00Z",
                    "IsDir": False,
                    "ID": "mock_f2",
                },
                {
                    "Path": "Backup Archive.zip",
                    "Name": "Backup Archive.zip",
                    "Size": 104857600,
                    "MimeType": "application/zip",
                    "ModTime": "2026-11-01T22:10:00Z",
                    "IsDir": False,
                    "ID": "mock_f3",
                },
            ]
        elif clean_path == "Documents":
            return [
                {
                    "Path": "Documents/Work Notes.txt",
                    "Name": "Work Notes.txt",
                    "Size": 45056,
                    "MimeType": "text/plain",
                    "ModTime": "2026-11-10T11:00:00Z",
                    "IsDir": False,
                    "ID": "mock_doc1",
                },
                {
                    "Path": "Documents/Research Summary.pdf",
                    "Name": "Research Summary.pdf",
                    "Size": 1843200,
                    "MimeType": "application/pdf",
                    "ModTime": "2026-11-09T14:20:00Z",
                    "IsDir": False,
                    "ID": "mock_doc2",
                },
            ]
        elif clean_path == "Projects":
            return [
                {
                    "Path": "Projects/SourceCode.tar.gz",
                    "Name": "SourceCode.tar.gz",
                    "Size": 45000000,
                    "MimeType": "application/gzip",
                    "ModTime": "2026-11-07T12:00:00Z",
                    "IsDir": False,
                    "ID": "mock_proj1",
                },
                {
                    "Path": "Projects/Specification.pdf",
                    "Name": "Specification.pdf",
                    "Size": 1200000,
                    "MimeType": "application/pdf",
                    "ModTime": "2026-11-08T09:30:00Z",
                    "IsDir": False,
                    "ID": "mock_proj2",
                },
            ]
        return []

    def download_file(self, remote_name: str, remote_path: str, local_dest: str) -> bool:
        """Download remote cloud file to local destination path."""
        if remote_name.startswith("sample") or remote_name == "mock_remote":
            try:
                dest = Path(local_dest)
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(f"Sample download of {remote_path} from {remote_name}", encoding="utf-8")
                return True
            except Exception as e:
                logger.error(f"Sample file download failed: {e}")
                return False

        clean_path = remote_path.strip("/\\").replace("\\", "/")
        src = f"{remote_name}:{clean_path}"
        try:
            code, stdout, stderr = self.execute_cmd(["copyto", src, local_dest], timeout=120)
            if code == 0:
                logger.info(f"Downloaded {src} to {local_dest} successfully")
                return True
            logger.warning(f"rclone copyto failed (code {code}): {stderr}")
            return False
        except Exception as e:
            logger.error(f"Exception during file download: {e}")
            return False
