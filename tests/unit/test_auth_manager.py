"""Unit tests for AuthManager OAuth 2.0 lifecycle."""

from unittest.mock import MagicMock, patch
import pytest

from app.core.auth_manager import AuthManager
from app.models.account import Account


def test_auth_manager_missing_rclone():
    rclone_svc = MagicMock()
    rclone_svc.rclone_exe = None
    account_repo = MagicMock()
    cred_svc = MagicMock()

    auth_mgr = AuthManager(rclone_svc, account_repo, cred_svc)

    on_status = MagicMock()
    on_success = MagicMock()
    on_error = MagicMock()

    auth_mgr._run_auth_flow(
        account_name="Test Account",
        drive_letter="G:",
        streaming_enabled=True,
        offline_enabled=False,
        offline_path="",
        cache_size="10G",
        on_status_update=on_status,
        on_success=on_success,
        on_error=on_error
    )

    on_error.assert_called_once()
    assert "rclone executable not found" in on_error.call_args[0][0]
    on_success.assert_not_called()


def test_auth_manager_duplicate_remote():
    rclone_svc = MagicMock()
    rclone_svc.rclone_exe = "rclone.exe"
    account_repo = MagicMock()
    existing_acc = Account(
        id="gdrive_work",
        email="work@gmail.com",
        display_name="Work",
        remote_name="gdrive_work",
        drive_letter="H:"
    )
    account_repo.load_all.return_value = [existing_acc]
    cred_svc = MagicMock()

    auth_mgr = AuthManager(rclone_svc, account_repo, cred_svc)

    on_status = MagicMock()
    on_success = MagicMock()
    on_error = MagicMock()

    auth_mgr._run_auth_flow(
        account_name="Work",
        drive_letter="I:",
        streaming_enabled=True,
        offline_enabled=False,
        offline_path="",
        cache_size="10G",
        on_status_update=on_status,
        on_success=on_success,
        on_error=on_error
    )

    on_error.assert_called_once()
    assert "already exists" in on_error.call_args[0][0]
    on_success.assert_not_called()


def test_auth_manager_successful_flow():
    rclone_svc = MagicMock()
    rclone_svc.rclone_exe = "rclone.exe"
    rclone_svc.config_path = "dummy/rclone.conf"
    rclone_svc.get_account_storage_quota.return_value = {"used": 1024, "total": 2048}

    account_repo = MagicMock()
    account_repo.load_all.return_value = []
    cred_svc = MagicMock()

    auth_mgr = AuthManager(rclone_svc, account_repo, cred_svc)

    mock_proc = MagicMock()
    mock_proc.returncode = 0
    mock_proc.communicate.return_value = ("Success", "")

    on_status = MagicMock()
    on_success = MagicMock()
    on_error = MagicMock()

    with patch("subprocess.Popen", return_value=mock_proc):
        auth_mgr._run_auth_flow(
            account_name="New Account",
            drive_letter="G:",
            streaming_enabled=True,
            offline_enabled=False,
            offline_path="",
            cache_size="10G",
            on_status_update=on_status,
            on_success=on_success,
            on_error=on_error
        )

    on_error.assert_not_called()
    on_success.assert_called_once()
    account_arg = on_success.call_args[0][0]
    assert account_arg.display_name == "New Account"
    assert account_arg.remote_name == "gdrive_new_account"
    account_repo.add_account.assert_called_once()
    cred_svc.store_token.assert_called_once()
