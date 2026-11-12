"""Unit tests for AccountManager."""

import sys
from pathlib import Path
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.models.account import Account
from app.config.account_repository import AccountRepository
from app.services.credential_service import CredentialService
from app.services.rclone_service import RcloneService
from app.core.account_manager import AccountManager

@pytest.fixture
def manager(tmp_path):
    storage_file = tmp_path / "accounts.json"
    repo = AccountRepository(storage_path=storage_file)
    rclone = RcloneService()
    cred = CredentialService()
    return AccountManager(repository=repo, rclone_service=rclone, credential_service=cred)

def test_initial_sample_fallback(manager):
    """When repo is empty, manager should populate sample accounts for UI demonstration."""
    accounts = manager.get_accounts()
    assert len(accounts) >= 4
    assert manager.has_real_accounts() is False

def test_add_first_real_account(manager):
    """Adding a real account should replace the sample accounts."""
    real_acc = Account(
        id="acc_real_01",
        email="myreal@gmail.com",
        display_name="Primary Cloud",
        remote_name="gdrive_primary",
        drive_letter="G:",
        is_sample=False
    )
    assert manager.add_account(real_acc) is True
    assert manager.has_real_accounts() is True

    accounts = manager.get_accounts()
    assert len(accounts) == 1
    assert accounts[0].display_name == "Primary Cloud"

def test_update_and_remove_account(manager):
    """Test updating and deleting real accounts in AccountManager."""
    acc = Account(id="acc_x", email="x@gmail.com", display_name="Account X", remote_name="gdrive_x", is_sample=False)
    manager.add_account(acc)

    # Update
    acc.display_name = "Account X Renamed"
    assert manager.update_account(acc) is True
    assert manager.get_accounts()[0].display_name == "Account X Renamed"

    # Remove
    assert manager.remove_account("acc_x") is True
    # If all real accounts are removed, fallback samples are restored
    assert manager.has_real_accounts() is False
    assert len(manager.get_accounts()) >= 4
