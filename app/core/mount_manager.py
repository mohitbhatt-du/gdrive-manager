"""Mount Manager supervising rclone WinFsp virtual drive subprocess lifecycles."""

import atexit
import os
import subprocess
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from app.models.account import Account
from app.services.rclone_service import RcloneService
from app.utils.logger import get_logger
from app.utils.paths import get_app_data_dir
from app.utils.platform_checks import get_occupied_drive_letters, is_winfsp_installed

logger = get_logger("MountManager")


@dataclass
class MountSession:
    """Represents an active virtual filesystem mount process."""

    account_id: str
    remote_name: str
    drive_letter: str
    process: subprocess.Popen
    pid: int
    cache_dir: Path
    status: str = "Mounting"  # Mounting, Mounted, Unmounting, Error
    error_message: str = ""
    mounted_at: float = 0.0


class MountManager:
    """Manages creation, health monitoring, and safe teardown of Windows virtual drives."""

    def __init__(self, rclone_service: RcloneService):
        self.rclone_service = rclone_service
        self.active_mounts: dict[str, MountSession] = {}
        self._lock = threading.Lock()
        self._monitoring = True
        self._callbacks: list[Callable[[str, str], None]] = []

        # Background monitor thread
        self._monitor_thread = threading.Thread(
            target=self._health_check_loop, daemon=True, name="MountMonitor"
        )
        self._monitor_thread.start()

        # Clean unmount on application termination
        atexit.register(self.unmount_all)

        # Cleanup any orphaned rclone mount processes left from prior abnormal terminations
        try:
            self.kill_orphaned_rclone_mounts()
        except Exception as e:
            logger.debug(f"Initial orphan cleanup completed: {e}")

    @staticmethod
    def kill_orphaned_rclone_mounts(drive_letter: str | None = None) -> int:
        """Find and terminate background rclone processes holding a drive letter or spawned by GDriveManager."""
        killed = 0
        if os.name != "nt":
            return 0

        try:
            cmd = [
                "powershell",
                "-NoProfile",
                "-NonInteractive",
                "-Command",
                "Get-CimInstance Win32_Process -Filter \"Name = 'rclone.exe'\" | "
                "Select-Object ProcessId, CommandLine | ConvertTo-Json",
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if res.returncode == 0 and res.stdout.strip():
                import json

                try:
                    data = json.loads(res.stdout)
                except Exception:
                    data = []

                if isinstance(data, dict):
                    data = [data]

                target_letter = drive_letter.upper().rstrip("\\") if drive_letter else None

                for proc in data:
                    pid = proc.get("ProcessId")
                    cmdline = str(proc.get("CommandLine", ""))
                    if not pid:
                        continue

                    is_mount = "mount" in cmdline.lower()
                    letter_match = target_letter is None or target_letter.lower() in cmdline.lower()

                    if is_mount and letter_match:
                        logger.info(f"Terminating orphaned rclone mount process (PID: {pid})")
                        try:
                            subprocess.run(
                                ["taskkill", "/F", "/PID", str(pid)],
                                capture_output=True,
                                timeout=3,
                            )
                            killed += 1
                        except Exception as e:
                            logger.warning(f"Failed to taskkill PID {pid}: {e}")
        except Exception as e:
            logger.warning(f"Error checking for orphaned rclone processes: {e}")

        return killed

    def register_callback(self, cb: Callable[[str, str], None]):
        """Register callback for mount status updates (account_id, new_status)."""
        self._callbacks.append(cb)

    def _notify(self, account_id: str, status: str):
        for cb in self._callbacks:
            try:
                cb(account_id, status)
            except Exception as e:
                logger.error(f"Error in mount callback: {e}")

    def build_mount_command(self, account: Account, cache_dir: Path) -> list[str]:
        """Construct safe subprocess argument list for 'rclone mount'."""
        exe = self.rclone_service.rclone_exe
        if not exe:
            raise FileNotFoundError("rclone executable not found.")

        # Ensure drive letter format: 'G:' (no trailing slash for rclone mount destination)
        letter = account.drive_letter.rstrip("\\")
        target_remote = f"{account.remote_name}:"

        cmd = [
            exe,
            "mount",
            target_remote,
            letter,
            "--config",
            str(self.rclone_service.config_path),
            "--vfs-cache-mode",
            "full",
            "--vfs-cache-max-size",
            account.cache_size,
            "--vfs-cache-max-age",
            account.cache_expiry,
            "--cache-dir",
            str(cache_dir),
            "--volname",
            account.display_name,
            "--vfs-read-chunk-size",
            "128M",
            "--vfs-read-chunk-size-limit",
            "off",
            "--buffer-size",
            "32M",
        ]

        if account.read_only:
            cmd.append("--read-only")

        return cmd

    def mount_drive(self, account: Account) -> tuple[bool, str]:
        """Mount a Google Drive account to its assigned Windows drive letter."""
        with self._lock:
            # 1. Check if already mounted
            if account.id in self.active_mounts:
                return False, f"Account '{account.display_name}' is already mounted."

            # 2. Check WinFsp driver availability
            if not is_winfsp_installed():
                return (
                    False,
                    "WinFsp driver is not installed. Please install WinFsp from Settings to mount Windows drives.",
                )

            # 3. Check rclone engine availability
            if not self.rclone_service.is_available():
                return (
                    False,
                    "rclone storage engine is not available. Please install or download rclone from Settings.",
                )

            # 4. Check for drive letter collision
            letter = account.drive_letter.upper().rstrip("\\")
            occupied = get_occupied_drive_letters()
            if letter in occupied:
                # Check and kill any orphaned background rclone process that may be holding this drive letter
                killed = self.kill_orphaned_rclone_mounts(letter)
                if killed > 0:
                    time.sleep(1.0)
                    occupied = get_occupied_drive_letters()

                if letter in occupied:
                    return (
                        False,
                        f"Drive letter {letter} is already occupied by another physical or virtual drive.",
                    )

            # 5. Prepare cache directory
            cache_dir = get_app_data_dir() / "vfs_cache" / account.id
            cache_dir.mkdir(parents=True, exist_ok=True)

            # 6. Build command
            try:
                cmd = self.build_mount_command(account, cache_dir)
            except Exception as e:
                return False, f"Failed to construct mount command: {e}"

            logger.info(f"Mounting {account.display_name} to {letter} with cmd: {' '.join(cmd)}")

            # 7. Launch process
            try:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
                )
            except Exception as e:
                logger.error(f"Failed to launch rclone mount subprocess: {e}")
                return False, f"Failed to execute mount process: {e}"

            # 8. Wait briefly to verify the process didn't instantly crash
            time.sleep(1.0)
            ret_code = process.poll()
            if ret_code is not None:
                err = (
                    process.stderr.read().strip()
                    if process.stderr
                    else "Mount process terminated unexpectedly."
                )
                logger.error(f"Mount process for {account.display_name} failed with code {ret_code}: {err}")
                return False, f"Mount failed: {err}"

            # Register active session
            session = MountSession(
                account_id=account.id,
                remote_name=account.remote_name,
                drive_letter=letter,
                process=process,
                pid=process.pid,
                cache_dir=cache_dir,
                status="Mounted",
                mounted_at=time.time(),
            )
            self.active_mounts[account.id] = session

            account.is_mounted = True
            account.mount_pid = process.pid
            account.status = "Mounted"

            logger.info(f"Successfully mounted {account.display_name} ({letter}) with PID {process.pid}")
            self._notify(account.id, "Mounted")
            return True, f"Drive {letter} mounted successfully."

    def unmount_drive(self, account: Account) -> tuple[bool, str]:
        """Safely unmount an active virtual drive and release the drive letter."""
        with self._lock:
            letter = account.drive_letter.upper().rstrip("\\")
            session = self.active_mounts.get(account.id)
            if session:
                logger.info(
                    f"Unmounting {account.display_name} (PID: {session.pid}, Drive: {session.drive_letter})..."
                )
                session.status = "Unmounting"
                self._notify(account.id, "Unmounting")

                proc = session.process
                try:
                    proc.terminate()
                    try:
                        proc.wait(timeout=3.0)
                    except subprocess.TimeoutExpired:
                        logger.warning(f"Process {session.pid} did not exit in 3s; killing force.")
                        proc.kill()
                        proc.wait(timeout=2.0)
                except Exception as e:
                    logger.warning(f"Error terminating mount process {session.pid}: {e}")

                # Remove from active mounts
                del self.active_mounts[account.id]

            # Also force-terminate any orphaned background rclone process holding this drive letter
            self.kill_orphaned_rclone_mounts(letter)

            account.is_mounted = False
            account.mount_pid = None
            account.status = "Connected"

            logger.info(f"Drive {letter} unmounted successfully.")
            self._notify(account.id, "Connected")
            return True, f"Drive {letter} unmounted safely."

    def is_account_mounted(self, account_id: str) -> bool:
        """Check whether an account is actively mounted."""
        with self._lock:
            session = self.active_mounts.get(account_id)
            if session and session.process.poll() is None:
                return True
            return False

    def get_mount_session(self, account_id: str) -> MountSession | None:
        with self._lock:
            return self.active_mounts.get(account_id)

    def _health_check_loop(self):
        """Periodically check health of active mount processes."""
        while self._monitoring:
            time.sleep(2.0)
            with self._lock:
                for account_id, session in list(self.active_mounts.items()):
                    if session.process.poll() is not None:
                        # Process died unexpectedly
                        ret = session.process.poll()
                        err = ""
                        try:
                            if session.process.stderr:
                                err = session.process.stderr.read().strip()
                        except Exception:
                            pass
                        logger.warning(
                            f"Mount process for account {account_id} died unexpectedly (code {ret}): {err}"
                        )
                        session.status = "Error"
                        session.error_message = err
                        del self.active_mounts[account_id]
                        self._notify(account_id, "Error")

    def unmount_all(self):
        """Cleanly unmount all drives on application shutdown and terminate all rclone mounts."""
        with self._lock:
            if self.active_mounts:
                logger.info(f"Shutting down {len(self.active_mounts)} active mounts...")
                for _account_id, session in list(self.active_mounts.items()):
                    try:
                        session.process.terminate()
                        session.process.wait(timeout=2.0)
                    except Exception:
                        try:
                            session.process.kill()
                        except Exception:
                            pass
                self.active_mounts.clear()

            # Also guarantee all background rclone mounts are terminated
            self.kill_orphaned_rclone_mounts()
            try:
                logger.info("All virtual drives unmounted cleanly.")
            except Exception:
                pass
