"""Secure credential storage using Windows Credential Manager via keyring."""

import json
from typing import Optional, Dict, Any
import keyring
from app.utils.logger import get_logger

logger = get_logger("CredentialService")

SERVICE_NAME = "GDriveManager"

class CredentialService:
    """Manages sensitive OAuth tokens and secrets in Windows Credential Manager."""

    @staticmethod
    def store_token(account_id: str, token_data: Dict[str, Any]) -> bool:
        """Store OAuth token dict as JSON in Windows Credential Manager."""
        try:
            payload = json.dumps(token_data)
            keyring.set_password(SERVICE_NAME, account_id, payload)
            logger.info(f"Securely stored credentials in Windows Credential Manager for {account_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to store credential for {account_id}: {e}")
            return False

    @staticmethod
    def get_token(account_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve and parse OAuth token dict from Windows Credential Manager."""
        try:
            payload = keyring.get_password(SERVICE_NAME, account_id)
            if payload:
                return json.loads(payload)
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve credential for {account_id}: {e}")
            return None

    @staticmethod
    def delete_token(account_id: str) -> bool:
        """Delete stored credential for account."""
        try:
            keyring.delete_password(SERVICE_NAME, account_id)
            logger.info(f"Removed credential for {account_id} from Windows Credential Manager")
            return True
        except keyring.errors.PasswordDeleteError:
            # Not found
            return True
        except Exception as e:
            logger.error(f"Failed to delete credential for {account_id}: {e}")
            return False
