"""Unit tests for AccountRepository persistence and atomic writes."""

import sys
from pathlib import Path
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.models.account import Account
from app.config.account_repository import AccountRepository

@pytest.fixture
def repo(tmp_path):
    storage_file = tmp_path / "accounts_test.json"
    return AccountRepository(storage_path=storage_file)

def test_empty_repo(repo):
    """Empty repo should return empty list."""
    assert repo.load_all() == []

def test_add_and_load_account(repo):
    """Test adding real accounts and reading back."""
    acc = Account(
        id="acc_real_1",
        email="real@gmail.com",
        display_name="Real Drive",
        remote_name="gdrive_real",
        drive_letter="G:",
        streaming_enabled=True,
        offline_enabled=True,
        offline_path="C:/Offline/Real",
        is_sample=False
    )
    assert repo.add_account(acc) is True

    loaded = repo.load_all()
    assert len(loaded) == 1
    assert loaded[0].id == "acc_real_1"
    assert loaded[0].display_name == "Real Drive"
    assert loaded[0].offline_path == "C:/Offline/Real"
    assert loaded[0].is_sample is False

def test_duplicate_prevention(repo):
    """Repo should reject duplicate account IDs or remotes."""
    acc1 = Account(id="acc_1", email="1@gmail.com", display_name="One", remote_name="remote_1")
    acc2 = Account(id="acc_1", email="2@gmail.com", display_name="Duplicate ID", remote_name="remote_2")
    acc3 = Account(id="acc_3", email="3@gmail.com", display_name="Duplicate Remote", remote_name="remote_1")

    assert repo.add_account(acc1) is True
    assert repo.add_account(acc2) is False
    assert repo.add_account(acc3) is False

def test_update_and_delete_account(repo):
    """Test updating existing account fields and deleting."""
    acc = Account(id="acc_target", email="t@gmail.com", display_name="Target", remote_name="rem_target", drive_letter="H:")
    repo.add_account(acc)

    # Update
    acc.display_name = "Updated Target"
    acc.drive_letter = "J:"
    assert repo.update_account(acc) is True

    reloaded = repo.load_all()
    assert reloaded[0].display_name == "Updated Target"
    assert reloaded[0].drive_letter == "J:"

    # Delete
    assert repo.delete_account("acc_target") is True
    assert repo.load_all() == []
