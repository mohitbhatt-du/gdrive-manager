"""Unit tests for SyncManager command construction, safety rules, and concurrency checks."""

import sys
from pathlib import Path
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.models.account import Account
from app.services.rclone_service import RcloneService
from app.core.transfer_manager import TransferManager
from app.core.sync_manager import SyncManager

@pytest.fixture
def sync_mgr(tmp_path):
    svc = RcloneService()
    svc.rclone_exe = "dummy_rclone.exe"
    tm = TransferManager()
    return SyncManager(rclone_service=svc, transfer_manager=tm)

@pytest.fixture
def test_account():
    return Account(
        id="acc_sync_test",
        email="sync@gmail.com",
        display_name="Sync Test Account",
        remote_name="gdrive_sync",
        drive_letter="G:"
    )

def test_build_copy_command(sync_mgr, test_account, tmp_path):
    """Test safe copy command construction."""
    dest = tmp_path / "offline_folder"
    cmd, title = sync_mgr.build_sync_command(
        operation="Cloud -> Local (Download/Copy)",
        account=test_account,
        local_path=str(dest),
        dry_run=False
    )
    assert cmd[0].endswith("rclone.exe")
    assert cmd[3] == "copy"
    assert cmd[4] == "gdrive_sync:"
    assert "--vfs-cache-mode" not in cmd  # copy/sync does not use mount vfs flags
    assert "--use-json-log" in cmd
    assert "--dry-run" not in cmd
    assert title == "Cloud -> Local (Download)"

def test_build_mirror_command_with_dry_run(sync_mgr, test_account, tmp_path):
    """Test mirror sync command with dry-run enabled."""
    dest = tmp_path / "offline_folder"
    cmd, title = sync_mgr.build_sync_command(
        operation="Cloud -> Local (Mirror/Sync)",
        account=test_account,
        local_path=str(dest),
        dry_run=True
    )
    assert cmd[3] == "sync"
    assert "--dry-run" in cmd
    assert title == "Cloud -> Local (Mirror Sync)"

def test_build_bisync_command(sync_mgr, test_account, tmp_path):
    """Test bidirectional bisync command with baseline --resync."""
    dest = tmp_path / "offline_folder"
    cmd, title = sync_mgr.build_sync_command(
        operation="Two-Way Bi-Sync",
        account=test_account,
        local_path=str(dest),
        dry_run=False
    )
    assert cmd[3] == "bisync"
    assert "--resync" in cmd
    assert title == "Two-Way Bi-Sync"

def test_overlapping_job_prevention(sync_mgr, test_account, tmp_path):
    """Test that two simultaneous sync jobs on same destination are prevented."""
    dest = tmp_path / "exclusive_folder"
    dest.mkdir(parents=True, exist_ok=True)

    ok1, msg1, job1 = sync_mgr.start_sync(
        account=test_account,
        local_path=str(dest),
        operation="Cloud -> Local (Download/Copy)",
        dry_run=True
    )
    assert ok1 is True
    assert job1 is not None

    # Attempt second overlapping job
    ok2, msg2, job2 = sync_mgr.start_sync(
        account=test_account,
        local_path=str(dest),
        operation="Cloud -> Local (Mirror/Sync)",
        dry_run=True
    )
    assert ok2 is False
    assert "already active" in msg2.lower()
    assert job2 is None
