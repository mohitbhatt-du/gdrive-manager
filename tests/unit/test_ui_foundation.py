"""Unit tests for Phase 1: Models, Utilities, and UI Foundation."""

import sys
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.models.account import Account, get_sample_accounts
from app.models.transfer_job import TransferJob
from app.ui.assets import get_drive_hardware_icon, get_gdrive_icon, get_symbol_icon
from app.utils.platform_checks import (
    get_available_drive_letters,
    get_occupied_drive_letters,
)


def test_account_model():
    """Test Account model properties, calculations, and dict conversion."""
    acc = Account(
        id="acc_test",
        email="test@gmail.com",
        display_name="Test Account",
        remote_name="remote_test",
        drive_letter="G:",
        streaming_enabled=True,
        offline_enabled=False,
        used_storage_bytes=5 * 1024 * 1024 * 1024,
        total_storage_bytes=10 * 1024 * 1024 * 1024,
    )
    assert acc.operating_mode == "Streaming"
    assert acc.storage_percentage == 50.0
    assert "5.0 GB" in acc.formatted_used
    assert "10.0 GB" in acc.formatted_total

    d = acc.to_dict()
    assert d["id"] == "acc_test"
    assert d["email"] == "test@gmail.com"

    restored = Account.from_dict(d)
    assert restored.display_name == "Test Account"
    assert restored.storage_percentage == 50.0


def test_account_hybrid_mode():
    """Test operating mode label for hybrid streaming and offline."""
    acc = Account(
        id="hybrid",
        email="h@gmail.com",
        display_name="Hybrid",
        remote_name="rem_h",
        streaming_enabled=True,
        offline_enabled=True,
    )
    assert acc.operating_mode == "Streaming + Offline"


def test_sample_accounts():
    """Verify sample accounts structure and flags."""
    samples = get_sample_accounts()
    assert len(samples) >= 4
    for s in samples:
        assert s.is_sample is True
        assert s.drive_letter.endswith(":")


def test_transfer_job_model():
    """Test TransferJob properties and calculations."""
    job = TransferJob(
        id="job-1",
        account_name="Test Drive",
        item_name="test.zip",
        operation_type="Download",
        total_bytes=1000,
        transferred_bytes=250,
        speed_bytes_per_sec=50,
        eta_seconds=15,
        status="Running",
    )
    assert job.progress_percentage == 25.0
    assert "250.0 B" in job.formatted_transferred
    assert "1000.0 B" in job.formatted_total
    assert job.formatted_eta == "00m 15s"


def test_platform_drive_letters():
    """Verify drive letters format."""
    occupied = get_occupied_drive_letters()
    assert isinstance(occupied, list)
    for d in occupied:
        assert len(d) == 2
        assert d[1] == ":"

    available = get_available_drive_letters()
    assert isinstance(available, list)
    # Available should not overlap with occupied
    assert set(available).isdisjoint(set(occupied))


def test_asset_generation():
    """Verify that all Pillow vector icons generate without error."""
    gdrive_ico = get_gdrive_icon(32)
    assert gdrive_ico is not None

    hw_ico = get_drive_hardware_icon(24)
    assert hw_ico is not None

    symbols = ["plus", "sync", "cloud", "folder", "gear", "play", "stop", "check", "close", "info", "open"]
    for s in symbols:
        ico = get_symbol_icon(s, 20)
        assert ico is not None


def test_main_window_instantiation(main_app):
    """Verify that MainWindow and its child pages instantiate properly."""
    app = main_app
    app.update_idletasks()

    assert "drives" in app.pages
    assert "streaming" in app.pages
    assert "offline" in app.pages
    assert "transfers" in app.pages
    assert "logs" in app.pages
    assert "settings" in app.pages
    assert "about" in app.pages

    # Switch across pages
    for p in ["streaming", "offline", "transfers", "logs", "settings", "about", "drives"]:
        app.show_page(p)
        assert app.current_page_id == p
