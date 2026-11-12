"""Synchronization Manager coordinating one-way copy, sync, and two-way bisync jobs."""

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from app.models.account import Account
from app.models.transfer_job import TransferJob
from app.services.rclone_service import RcloneService
from app.core.transfer_manager import TransferManager
from app.utils.logger import get_logger

logger = get_logger("SyncManager")

class SyncManager:
    """Manages offline downloads, uploads, and bidirectional synchronization with safety checks."""

    def __init__(self, rclone_service: RcloneService, transfer_manager: TransferManager):
        self.rclone_service = rclone_service
        self.transfer_manager = transfer_manager
        # Track active synchronization targets to prevent overlapping jobs
        self._active_targets: Dict[str, str] = {}  # target_key -> job_id

    def _get_target_key(self, account_id: str, destination_path: str) -> str:
        """Create unique key identifying account and destination directory."""
        clean_path = str(Path(destination_path).resolve()).lower()
        return f"{account_id}::{clean_path}"

    def build_sync_command(
        self,
        operation: str,
        account: Account,
        local_path: str,
        dry_run: bool = False,
        remote_subpath: str = ""
    ) -> Tuple[List[str], str]:
        """Construct rclone command argument list and human-readable operation title."""
        exe = self.rclone_service.rclone_exe
        if not exe:
            raise FileNotFoundError("rclone executable not found. Please install rclone.")

        remote_target = f"{account.remote_name}:{remote_subpath.lstrip('/')}"
        clean_local = str(Path(local_path).resolve())

        base_flags = [
            exe,
            "--config", str(self.rclone_service.config_path),
        ]

        telemetry_flags = [
            "--stats", "1s",
            "--stats-log-level", "NOTICE",
            "--use-json-log",
        ]

        if dry_run:
            telemetry_flags.append("--dry-run")

        # Map UI operations to rclone subcommands
        if "Cloud -> Local (Download/Copy" in operation:
            # Safe copy from cloud to local
            op_title = "Cloud -> Local (Download)"
            cmd = base_flags + ["copy", remote_target, clean_local] + telemetry_flags

        elif "Cloud -> Local (Mirror/Sync" in operation:
            # Mirror sync from cloud to local (deletes missing local files)
            op_title = "Cloud -> Local (Mirror Sync)"
            cmd = base_flags + ["sync", remote_target, clean_local] + telemetry_flags

        elif "Local -> Cloud (Upload/Copy" in operation:
            # Safe copy from local to cloud
            op_title = "Local -> Cloud (Upload)"
            cmd = base_flags + ["copy", clean_local, remote_target] + telemetry_flags

        elif "Local -> Cloud (Mirror/Sync" in operation:
            # Mirror sync from local to cloud (deletes missing cloud files)
            op_title = "Local -> Cloud (Mirror Sync)"
            cmd = base_flags + ["sync", clean_local, remote_target] + telemetry_flags

        elif "Two-Way Bi-Sync" in operation:
            # Bidirectional bisync
            op_title = "Two-Way Bi-Sync"
            cmd = base_flags + ["bisync", remote_target, clean_local, "--resync"] + telemetry_flags

        else:
            # Default to safe copy
            op_title = "Cloud -> Local (Copy)"
            cmd = base_flags + ["copy", remote_target, clean_local] + telemetry_flags

        return cmd, op_title

    def start_sync(
        self,
        account: Account,
        local_path: str,
        operation: str,
        dry_run: bool = False,
        remote_subpath: str = ""
    ) -> Tuple[bool, str, Optional[TransferJob]]:
        """Validate safety rules, create transfer job, and dispatch to TransferManager."""
        # 1. Validate destination path
        if not local_path.strip():
            return False, "Destination directory cannot be empty.", None

        dest_dir = Path(local_path)
        try:
            dest_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            return False, f"Cannot create destination directory '{local_path}': {e}", None

        # 2. Prevent overlapping synchronization jobs for the same account and destination
        target_key = self._get_target_key(account.id, local_path)
        if target_key in self._active_targets:
            existing_job_id = self._active_targets[target_key]
            return False, f"A synchronization job ({existing_job_id}) is already active for this account and destination.", None

        # 3. Build command
        try:
            cmd, op_title = self.build_sync_command(operation, account, local_path, dry_run, remote_subpath)
        except Exception as e:
            return False, f"Failed to build sync command: {e}", None

        # 4. Create TransferJob
        job_id = f"sync-{int(os.getpid())}-{len(self.transfer_manager.jobs) + 1}"
        item_label = f"{account.display_name} ({Path(local_path).name})"
        if dry_run:
            item_label += " [DRY RUN]"

        job = TransferJob(
            id=job_id,
            account_name=account.display_name,
            item_name=item_label,
            operation_type=op_title,
            total_bytes=0,
            transferred_bytes=0,
            speed_bytes_per_sec=0.0,
            eta_seconds=None,
            status="Queued",
            is_sample=False
        )

        self._active_targets[target_key] = job_id

        # Register cleanup when job completes or fails
        def _on_finish(j: TransferJob):
            if j.id == job_id and j.status in ("Completed", "Failed", "Cancelled"):
                self._active_targets.pop(target_key, None)

        self.transfer_manager.register_callback(_on_finish)

        # 5. Submit to TransferManager
        self.transfer_manager.add_job(job, cmd)
        logger.info(f"Submitted sync job {job_id} for {account.display_name} -> {local_path}")

        return True, f"Started {op_title} successfully.", job
