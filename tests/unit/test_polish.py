"""Unit tests for Phase 6 polish: startup registry, desktop notifications, logs page, and system tray."""

import winreg
from unittest.mock import MagicMock, patch

from app.ui.tray import SystemTrayManager
from app.utils.notifications import send_notification
from app.utils.startup import get_launch_command, is_startup_enabled, set_startup_enabled


def test_get_launch_command():
    cmd = get_launch_command()
    assert "main.py" in cmd or "python" in cmd.lower()


def test_is_startup_enabled_true():
    mock_key = MagicMock()
    with patch("winreg.OpenKey", return_value=mock_key):
        with patch("winreg.QueryValueEx", return_value=('"dummy.exe"', winreg.REG_SZ)):
            assert is_startup_enabled() is True


def test_is_startup_enabled_false():
    with patch("winreg.OpenKey", side_effect=FileNotFoundError):
        assert is_startup_enabled() is False


def test_set_startup_enabled_enable():
    mock_key = MagicMock()
    with patch("winreg.OpenKey", return_value=mock_key):
        with patch("winreg.SetValueEx") as mock_set:
            success = set_startup_enabled(True)
            assert success is True
            mock_set.assert_called_once()
            args, _ = mock_set.call_args
            assert args[1] == "GDriveManager"
            assert args[2] == 0
            assert args[3] == winreg.REG_SZ


def test_set_startup_enabled_disable():
    mock_key = MagicMock()
    with patch("winreg.OpenKey", return_value=mock_key):
        with patch("winreg.DeleteValue") as mock_del:
            success = set_startup_enabled(False)
            assert success is True
            mock_del.assert_called_once()
            args, _ = mock_del.call_args
            assert args[1] == "GDriveManager"


def test_send_notification_dispatch():
    with patch("subprocess.run") as mock_run:
        send_notification("Test Title", "Test Message")
        # Give daemon thread a brief moment to execute
        import time

        time.sleep(0.1)
        mock_run.assert_called()
        cmd = mock_run.call_args[0][0]
        assert cmd[0] == "powershell"
        assert "Test Title" in cmd[3]


def test_system_tray_manager_image_and_menu():
    on_show = MagicMock()
    on_mount = MagicMock()
    on_unmount = MagicMock()
    on_quit = MagicMock()

    tray = SystemTrayManager(
        on_show_window=on_show, on_mount_all=on_mount, on_unmount_all=on_unmount, on_quit=on_quit
    )

    img = tray._create_tray_image()
    assert img.size == (64, 64)
    assert img.mode == "RGBA"

    # Verify stop handles unstarted icon gracefully
    tray.stop()
    assert tray._icon is None


def test_logs_page_filtering(main_app, tmp_path):
    logs_page = main_app.pages["logs"]
    test_log = tmp_path / "test.log"
    test_log.write_text(
        "2026-01-01 [INFO] Startup completed\n"
        "2026-01-01 [DEBUG] Verbose detail\n"
        "2026-01-01 [WARNING] Disk low\n"
        "2026-01-01 [ERROR] Failed to mount\n",
        encoding="utf-8",
    )

    logs_page.log_file = test_log

    # Test All Levels
    logs_page.filter_var.set("All Levels")
    logs_page.refresh_logs()
    txt = logs_page.text_box.get("1.0", "end")
    assert "Startup completed" in txt
    assert "Failed to mount" in txt

    # Test ERROR filter
    logs_page.filter_var.set("ERROR")
    logs_page.refresh_logs()
    txt_error = logs_page.text_box.get("1.0", "end")
    assert "Failed to mount" in txt_error
    assert "Startup completed" not in txt_error


def test_onboarding_state(tmp_path, monkeypatch):
    from app.utils import onboarding

    fake_marker = tmp_path / ".onboarding_completed"
    monkeypatch.setattr(onboarding, "_get_marker_path", lambda: fake_marker)

    assert not onboarding.is_onboarding_completed()
    onboarding.set_onboarding_completed(True)
    assert onboarding.is_onboarding_completed()
    onboarding.reset_onboarding()
    assert not onboarding.is_onboarding_completed()


def test_setup_wizard_dialog(main_app):
    from app.ui.dialogs.setup_wizard_dialog import SetupWizardDialog

    connect_called = []
    dlg = SetupWizardDialog(main_app, on_connect_drive=lambda: connect_called.append(True))
    main_app.update_idletasks()
    assert dlg.winfo_exists()

    dlg._on_connect_account()
    main_app.update_idletasks()
    assert len(connect_called) == 1
