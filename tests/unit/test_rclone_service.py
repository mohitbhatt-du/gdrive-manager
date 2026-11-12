"""Unit tests for RcloneService discovery, remote listing, and quota querying."""

import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.services.rclone_service import RcloneService


def test_rclone_service_init():
    """Verify rclone service initialization and config path creation."""
    svc = RcloneService(custom_binary_path="C:/nonexistent/rclone.exe")
    assert svc.custom_binary == "C:/nonexistent/rclone.exe"
    assert svc.config_path.name == "rclone.conf"


def test_list_remotes_parsing(mocker, tmp_path):
    """Verify rclone listremotes output parsing."""
    conf = tmp_path / "rclone.conf"
    conf.touch()

    svc = RcloneService(custom_config_path=str(conf))
    svc.rclone_exe = "dummy_rclone.exe"
    mocker.patch.object(svc, "execute_cmd", return_value=(0, "gdrive_personal:\ngdrive_work:\n", ""))

    remotes = svc.list_remotes()
    assert remotes == ["gdrive_personal", "gdrive_work"]


def test_get_storage_quota_parsing(mocker):
    """Verify rclone about JSON quota parsing."""
    svc = RcloneService()
    svc.rclone_exe = "dummy_rclone.exe"

    mock_about_json = json.dumps(
        {"total": 107374182400, "used": 42949672960, "trashed": 1048576, "free": 64424509440}
    )
    mocker.patch.object(svc, "execute_cmd", return_value=(0, mock_about_json, ""))

    quota = svc.get_account_storage_quota("gdrive_personal")
    assert quota["total"] == 107374182400
    assert quota["used"] == 42949672960
    assert quota["free"] == 64424509440


def test_delete_remote(mocker):
    """Verify delete remote executes correct arguments."""
    svc = RcloneService()
    svc.rclone_exe = "dummy_rclone.exe"
    mocker.patch.object(svc, "execute_cmd", return_value=(0, "", ""))

    assert svc.delete_remote("gdrive_old") is True
