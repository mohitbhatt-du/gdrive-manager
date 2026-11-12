"""Unit tests for StorageDetailsDialog modal."""

from unittest.mock import MagicMock, patch

from app.models.account import Account
from app.ui.dialogs.storage_details_dialog import StorageDetailsDialog


def test_storage_details_dialog_instantiation(main_app):
    account = Account(
        id="test_acc",
        email="test@gmail.com",
        display_name="Test Storage",
        remote_name="gdrive_test",
        drive_letter="G:",
        used_storage_bytes=5 * 1024 * 1024 * 1024,
        total_storage_bytes=15 * 1024 * 1024 * 1024,
    )

    storage_mgr = MagicMock()
    storage_mgr.get_storage_breakdown.return_value = {
        "cloud_used": 5 * 1024 * 1024 * 1024,
        "cloud_total": 15 * 1024 * 1024 * 1024,
        "offline_size": 1024 * 1024 * 1024,
        "vfs_cache_size": 512 * 1024 * 1024,
    }
    storage_mgr.purge_vfs_cache.return_value = (True, "Cache purged")

    purged_called = []
    dlg = StorageDetailsDialog(
        main_app,
        account=account,
        storage_manager=storage_mgr,
        on_cache_purged=lambda: purged_called.append(True),
    )
    main_app.update_idletasks()
    assert dlg.winfo_exists()

    # Trigger cache purge with mocked messagebox
    with patch("tkinter.messagebox.askyesno", return_value=True):
        with patch("tkinter.messagebox.showinfo"):
            dlg._handle_purge_cache()
    storage_mgr.purge_vfs_cache.assert_called_once_with("test_acc")
    assert len(purged_called) == 1

    dlg.destroy()
