"""Unit tests for Dialog modals in GDrive Manager."""

import sys
from pathlib import Path
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import customtkinter as ctk
from app.models.account import Account
from app.ui.dialogs.confirmation_dialog import ConfirmationDialog
from app.ui.dialogs.add_account_dialog import AddAccountDialog
from app.ui.dialogs.drive_settings_dialog import DriveSettingsDialog

def test_confirmation_dialog(tk_root):
    """Test confirmation dialog callback on confirm."""
    confirmed = []
    dlg = ConfirmationDialog(
        tk_root,
        title="Test Confirm",
        message="Are you sure?",
        on_confirm=lambda: confirmed.append(True)
    )
    dlg.update_idletasks()
    assert dlg.title() == "Test Confirm"
    dlg._handle_confirm()
    assert confirmed == [True]

def test_add_account_dialog(tk_root):
    """Test AddAccountDialog creation and submission."""
    created_accounts = []
    dlg = AddAccountDialog(
        tk_root,
        on_account_created=lambda acc: created_accounts.append(acc)
    )
    dlg.update_idletasks()
    assert len(dlg.available_letters) > 0

    # Fill form
    dlg.name_var.set("Test Vault")
    dlg.letter_var.set("Z:")
    dlg.mode_var.set("Streaming Only (Explorer Virtual Drive)")
    dlg._handle_submit()

    assert len(created_accounts) == 1
    acc = created_accounts[0]
    assert acc.display_name == "Test Vault"
    assert acc.drive_letter == "Z:"
    assert acc.streaming_enabled is True
    assert acc.offline_enabled is False

def test_drive_settings_dialog(tk_root):
    """Test DriveSettingsDialog update and delete callbacks."""
    acc = Account(
        id="sample_test",
        email="test@gmail.com",
        display_name="Original Name",
        remote_name="rem_test",
        drive_letter="G:",
        streaming_enabled=True,
        offline_enabled=False,
    )
    updated_accounts = []
    dlg = DriveSettingsDialog(
        tk_root,
        account=acc,
        on_account_updated=lambda a: updated_accounts.append(a)
    )
    dlg.update_idletasks()

    dlg.name_var.set("Renamed Vault")
    dlg.cache_size_var.set("50G")
    dlg.read_only_var.set(True)
    dlg._handle_save()

    assert len(updated_accounts) == 1
    assert acc.display_name == "Renamed Vault"
    assert acc.cache_size == "50G"
    assert acc.read_only is True
