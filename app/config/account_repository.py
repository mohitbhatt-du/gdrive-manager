"""Account metadata persistence with atomic writes and schema validation."""

import json
from pathlib import Path

from app.models.account import Account
from app.utils.logger import get_logger
from app.utils.paths import get_app_data_dir

logger = get_logger("AccountRepository")


class AccountRepository:
    """Manages persistence of non-sensitive Google Drive account metadata."""

    def __init__(self, storage_path: Path | None = None):
        if storage_path:
            self.file_path = storage_path
        else:
            self.file_path = get_app_data_dir() / "accounts.json"

        # Ensure parent directory exists
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def load_all(self) -> list[Account]:
        """Load and validate all configured accounts from disk."""
        if not self.file_path.exists():
            return []

        try:
            with open(self.file_path, encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, dict) or "accounts" not in data:
                logger.warning(f"Corrupted or invalid accounts schema in {self.file_path}. Returning empty.")
                return []

            accounts = []
            for item in data.get("accounts", []):
                try:
                    # Mark loaded accounts as real accounts
                    item["is_sample"] = False
                    acc = Account.from_dict(item)
                    accounts.append(acc)
                except Exception as e:
                    logger.warning(f"Failed to deserialize account entry: {e}")

            return accounts
        except Exception as e:
            logger.error(f"Error loading accounts file {self.file_path}: {e}")
            return []

    def save_all(self, accounts: list[Account]) -> bool:
        """Atomically persist accounts list to JSON file."""
        temp_file = self.file_path.with_suffix(".tmp")
        try:
            # Filter out sample preview accounts from persistent storage
            real_accounts = [a for a in accounts if not a.is_sample]

            data = {"version": 1, "accounts": [a.to_dict() for a in real_accounts]}

            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            # Atomic rename / replace
            temp_file.replace(self.file_path)
            logger.debug(f"Saved {len(real_accounts)} accounts to {self.file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to atomically write accounts to {self.file_path}: {e}")
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except Exception:
                    pass
            return False

    def add_account(self, account: Account) -> bool:
        """Add an account if ID does not already exist."""
        accounts = self.load_all()
        for existing in accounts:
            if existing.id == account.id or existing.remote_name == account.remote_name:
                logger.warning(
                    f"Account with ID '{account.id}' or remote '{account.remote_name}' already exists."
                )
                return False
        accounts.append(account)
        return self.save_all(accounts)

    def update_account(self, account: Account) -> bool:
        """Update an existing account in storage."""
        accounts = self.load_all()
        updated = False
        for idx, existing in enumerate(accounts):
            if existing.id == account.id:
                accounts[idx] = account
                updated = True
                break
        if updated:
            return self.save_all(accounts)
        return False

    def delete_account(self, account_id: str) -> bool:
        """Remove account by ID."""
        accounts = self.load_all()
        new_list = [a for a in accounts if a.id != account_id]
        if len(new_list) != len(accounts):
            return self.save_all(new_list)
        return False
