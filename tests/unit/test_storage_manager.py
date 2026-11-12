"""Unit tests for StorageManager cloud, offline, and VFS cache calculation."""

import sys
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.core.storage_manager import StorageManager
from app.models.account import Account
from app.services.rclone_service import RcloneService


@pytest.fixture
def storage_mgr():
    svc = RcloneService()
    return StorageManager(rclone_service=svc)


def test_storage_breakdown_metrics(storage_mgr, tmp_path):
    """Test breakdown correctly calculates local offline directory and VFS cache."""
    # Create offline test files
    offline_dir = tmp_path / "offline_data"
    offline_dir.mkdir()
    (offline_dir / "file1.bin").write_bytes(b"A" * 1024)
    (offline_dir / "file2.bin").write_bytes(b"B" * 2048)

    acc = Account(
        id="acc_storage_test",
        email="st@gmail.com",
        display_name="Storage Test",
        remote_name="gdrive_st",
        streaming_enabled=True,
        offline_enabled=True,
        offline_path=str(offline_dir),
        used_storage_bytes=5 * 1024 * 1024,
        total_storage_bytes=10 * 1024 * 1024,
        is_sample=True,
    )

    breakdown = storage_mgr.calculate_storage_breakdown(acc)

    # Cloud
    assert breakdown.cloud_used_bytes == 5 * 1024 * 1024
    assert breakdown.cloud_total_bytes == 10 * 1024 * 1024
    assert breakdown.cloud_percentage == 50.0

    # Offline
    assert breakdown.offline_used_bytes == 1024 + 2048
    assert breakdown.offline_file_count == 2
    assert "3.0 KB" in breakdown.formatted_offline_used


def test_purge_vfs_cache(storage_mgr, mocker, tmp_path):
    """Test purging local VFS cache."""
    fake_app_data = tmp_path / "app_data"
    mocker.patch("app.core.storage_manager.get_app_data_dir", return_value=fake_app_data)

    cache_dir = fake_app_data / "vfs_cache" / "test_purge_acc"
    cache_dir.mkdir(parents=True)
    (cache_dir / "chunk.tmp").write_text("cache chunk data")

    assert (cache_dir / "chunk.tmp").exists()
    assert storage_mgr.purge_vfs_cache("test_purge_acc") is True
    assert not (cache_dir / "chunk.tmp").exists()
    assert cache_dir.exists()  # re-created empty
