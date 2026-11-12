"""Unit tests for MountManager subprocess execution and lifecycle."""

import subprocess
import sys
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.core.mount_manager import MountManager
from app.models.account import Account
from app.services.rclone_service import RcloneService


@pytest.fixture
def rclone_svc():
    svc = RcloneService()
    svc.rclone_exe = "dummy_rclone.exe"
    return svc


@pytest.fixture
def mount_mgr(rclone_svc):
    mgr = MountManager(rclone_service=rclone_svc)
    # Stop background thread after test
    yield mgr
    mgr._monitoring = False
    mgr.unmount_all()


def test_build_mount_command(mount_mgr, tmp_path):
    """Test mount command argument list construction."""
    acc = Account(
        id="acc_unit_1",
        email="unit@gmail.com",
        display_name="Unit Drive",
        remote_name="gdrive_unit",
        drive_letter="G:",
        cache_size="25G",
        cache_expiry="48h",
        read_only=True,
    )
    cache_dir = tmp_path / "cache"
    cmd = mount_mgr.build_mount_command(acc, cache_dir)

    assert cmd[0].endswith("rclone.exe")
    assert cmd[1] == "mount"
    assert cmd[2] == "gdrive_unit:"
    assert cmd[3] == "G:"
    assert "--vfs-cache-mode" in cmd
    assert "full" in cmd
    assert "--vfs-cache-max-size" in cmd
    assert "25G" in cmd
    assert "--vfs-cache-max-age" in cmd
    assert "48h" in cmd
    assert "--read-only" in cmd
    assert "--volname" in cmd
    assert "Unit Drive" in cmd


def test_mount_collision_prevention(mount_mgr, mocker):
    """Test that occupied drive letters are rejected."""
    mocker.patch("app.core.mount_manager.is_winfsp_installed", return_value=True)
    mocker.patch.object(mount_mgr.rclone_service, "is_available", return_value=True)
    mocker.patch("app.core.mount_manager.get_occupied_drive_letters", return_value=["C:", "D:", "G:"])

    acc = Account(
        id="acc_coll",
        email="c@gmail.com",
        display_name="Colliding Drive",
        remote_name="gdrive_coll",
        drive_letter="G:",
    )

    ok, msg = mount_mgr.mount_drive(acc)
    assert ok is False
    assert "occupied" in msg.lower()


def test_mount_winfsp_missing(mount_mgr, mocker):
    """Test that missing WinFsp driver is clearly reported."""
    mocker.patch("app.core.mount_manager.is_winfsp_installed", return_value=False)
    mocker.patch.object(mount_mgr.rclone_service, "is_available", return_value=True)

    acc = Account(
        id="acc_no_fsp",
        email="fsp@gmail.com",
        display_name="No WinFsp",
        remote_name="gdrive_nofsp",
        drive_letter="Z:",
    )

    ok, msg = mount_mgr.mount_drive(acc)
    assert ok is False
    assert "WinFsp" in msg


def test_successful_mount_and_unmount(mount_mgr, mocker):
    """Test successful mount process tracking and subsequent unmount."""
    mocker.patch("app.core.mount_manager.is_winfsp_installed", return_value=True)
    mocker.patch.object(mount_mgr.rclone_service, "is_available", return_value=True)
    mocker.patch("app.core.mount_manager.get_occupied_drive_letters", return_value=["C:"])

    # Mock subprocess.Popen
    mock_proc = mocker.MagicMock(spec=subprocess.Popen)
    mock_proc.pid = 98765
    mock_proc.poll.return_value = None
    mocker.patch("subprocess.Popen", return_value=mock_proc)

    acc = Account(
        id="acc_success",
        email="s@gmail.com",
        display_name="Success Drive",
        remote_name="gdrive_success",
        drive_letter="K:",
    )

    # 1. Mount
    ok, msg = mount_mgr.mount_drive(acc)
    assert ok is True
    assert acc.is_mounted is True
    assert acc.mount_pid == 98765
    assert mount_mgr.is_account_mounted("acc_success") is True

    # Duplicate mount prevention
    dup_ok, dup_msg = mount_mgr.mount_drive(acc)
    assert dup_ok is False
    assert "already mounted" in dup_msg.lower()

    # 2. Unmount
    un_ok, un_msg = mount_mgr.unmount_drive(acc)
    assert un_ok is True
    assert acc.is_mounted is False
    assert acc.mount_pid is None
    assert mount_mgr.is_account_mounted("acc_success") is False
    assert mock_proc.terminate.called
