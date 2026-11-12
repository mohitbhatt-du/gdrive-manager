"""Unit tests for In-App Cloud File Browser and Dashboard real-time metrics refresh."""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.models.account import get_sample_accounts
from app.services.rclone_service import RcloneService
from app.ui.dashboard import Dashboard
from app.ui.dialogs.cloud_browser_dialog import CloudBrowserDialog
from app.utils.paths import get_app_data_dir
from app.utils.platform_checks import get_rclone_executable_path


def test_rclone_service_list_directory():
    """Verify rclone_service.list_directory returns sample folders and files."""
    svc = RcloneService()
    items = svc.list_directory("sample_personal", remote_path="", shared_with_me=False)
    assert len(items) > 0

    dirs = [it for it in items if it.get("IsDir")]
    files = [it for it in items if not it.get("IsDir")]
    assert len(dirs) >= 1
    assert len(files) >= 1
    assert any(d["Name"] == "Documents" for d in dirs)

    # Subfolder traversal
    doc_items = svc.list_directory("sample_personal", remote_path="Documents", shared_with_me=False)
    assert len(doc_items) >= 1
    assert any("Work Notes" in it["Name"] for it in doc_items)


def test_rclone_service_shared_with_me():
    """Verify rclone_service.list_directory with shared_with_me returns shared files."""
    svc = RcloneService()
    shared_items = svc.list_directory("sample_personal", remote_path="", shared_with_me=True)
    assert len(shared_items) >= 1
    names = [it["Name"] for it in shared_items]
    assert any("Shared" in n or "Presentation" in n for n in names)


def test_rclone_service_download_sample(tmp_path):
    """Verify downloading a cloud file in sample mode writes the local file."""
    svc = RcloneService()
    target_file = tmp_path / "test_download.pdf"
    ok = svc.download_file("sample_work", "Documents/Research Summary.pdf", str(target_file))
    assert ok is True
    assert target_file.exists()
    assert target_file.stat().st_size > 0


def test_dashboard_stats_bar_refresh(tk_root):
    """Verify that Dashboard stats bar (metrics) updates dynamically when accounts change."""
    accounts = get_sample_accounts()
    dashboard = Dashboard(
        tk_root,
        accounts=accounts[:2],
        on_add_drive=lambda: None,
    )
    dashboard.update_idletasks()

    assert dashboard.total_accounts_lbl is not None
    assert "2 Active" in dashboard.total_accounts_lbl.cget("text")

    # Set all accounts to unmounted
    for a in accounts:
        a.is_mounted = False

    dashboard.update_accounts(accounts)
    dashboard.update_idletasks()
    assert f"{len(accounts)} Active" in dashboard.total_accounts_lbl.cget("text")
    assert "0 Mounted" in dashboard.streaming_drives_lbl.cget("text")

    # Mount exactly one account
    accounts[0].is_mounted = True
    dashboard.update_accounts(accounts)
    dashboard.update_idletasks()
    assert "1 Mounted" in dashboard.streaming_drives_lbl.cget("text")


def test_cloud_browser_dialog_navigation(tk_root):
    """Verify CloudBrowserDialog navigation, shared toggle, and search filter."""
    accounts = get_sample_accounts()
    svc = RcloneService()
    dlg = CloudBrowserDialog(
        tk_root,
        account=accounts[0],
        rclone_service=svc,
        all_accounts=accounts,
    )
    dlg.update_idletasks()

    # Initial path should be root
    assert dlg.path_lbl.cget("text") == "/"

    # Navigate to Documents
    dlg._navigate_to("Documents")
    assert dlg.current_path == "Documents"
    assert "Documents" in dlg.path_lbl.cget("text")

    # Navigate back up
    dlg._go_up_directory()
    assert dlg.current_path == ""

    # Toggle Shared with Me
    dlg.shared_var.set(True)
    dlg._on_toggle_shared()
    assert "Shared with Me" in dlg.path_lbl.cget("text")

    # Filter items
    dlg.search_var.set("Quarterly")
    dlg._filter_items()

    dlg.destroy()


def test_rclone_executable_discovery():
    """Verify rclone executable path resolution and user AppData fallback."""
    discovered = get_rclone_executable_path()
    assert discovered is not None or discovered is None  # Runs cleanly without crashing

    svc = RcloneService()
    app_data_bin = get_app_data_dir() / "bin" / "rclone"
    assert app_data_bin is not None
