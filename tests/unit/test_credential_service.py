"""Unit tests for CredentialService using keyring mock."""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.services.credential_service import CredentialService


def test_credential_store_and_retrieve(mocker):
    """Test storing and retrieving OAuth token payload in Windows Credential Manager."""
    vault = {}

    def mock_set(service, key, password):
        vault[f"{service}:{key}"] = password

    def mock_get(service, key):
        return vault.get(f"{service}:{key}")

    def mock_del(service, key):
        vault.pop(f"{service}:{key}", None)

    mocker.patch("keyring.set_password", side_effect=mock_set)
    mocker.patch("keyring.get_password", side_effect=mock_get)
    mocker.patch("keyring.delete_password", side_effect=mock_del)

    token_data = {"access_token": "ya29.xyz", "refresh_token": "1//0abc", "expiry": "2026-11-12T12:00:00"}

    # Store
    assert CredentialService.store_token("account_101", token_data) is True

    # Retrieve
    retrieved = CredentialService.get_token("account_101")
    assert retrieved is not None
    assert retrieved["access_token"] == "ya29.xyz"
    assert retrieved["refresh_token"] == "1//0abc"

    # Delete
    assert CredentialService.delete_token("account_101") is True
    assert CredentialService.get_token("account_101") is None
