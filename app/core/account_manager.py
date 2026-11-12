"""Central account manager coordinating repository, credentials, and cloud quotas."""

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor

from app.config.account_repository import AccountRepository
from app.models.account import Account, get_sample_accounts
from app.services.credential_service import CredentialService
from app.services.rclone_service import RcloneService
from app.utils.logger import get_logger

logger = get_logger("AccountManager")


class AccountManager:
    """Manages active Google Drive accounts, storage sync, and persistence."""

    def __init__(
        self,
        repository: AccountRepository,
        rclone_service: RcloneService,
        credential_service: CredentialService,
    ):
        self.repository = repository
        self.rclone_service = rclone_service
        self.credential_service = credential_service
        self.executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix="AccountWorker")

        self._accounts: list[Account] = []
        self._load_initial_accounts()

    def _load_initial_accounts(self):
        """Load real accounts from disk, or fallback to sample accounts if none exist."""
        saved = self.repository.load_all()
        if saved:
            self._accounts = saved
            logger.info(f"Loaded {len(saved)} real accounts from repository.")
        else:
            # Fallback to UI preview sample accounts
            self._accounts = get_sample_accounts()
            logger.info("No saved accounts found. Loaded sample accounts for UI demonstration.")

    def get_accounts(self) -> list[Account]:
        """Return currently loaded accounts."""
        return self._accounts

    def has_real_accounts(self) -> bool:
        """Check if any real (non-sample) accounts are configured."""
        return any(not a.is_sample for a in self._accounts)

    def add_account(self, account: Account) -> bool:
        """Register a new account, replacing sample preview if this is the first real account."""
        # If currently showing samples, remove sample accounts
        if not self.has_real_accounts():
            self._accounts = [a for a in self._accounts if not a.is_sample]

        # Check duplicates
        for existing in self._accounts:
            if existing.id == account.id or existing.remote_name == account.remote_name:
                logger.warning(f"Account {account.id} already exists in manager.")
                return False

        self._accounts.append(account)
        self.repository.save_all(self._accounts)
        logger.info(f"Account {account.display_name} registered successfully.")
        return True

    def update_account(self, account: Account) -> bool:
        """Update account settings and persist."""
        for idx, existing in enumerate(self._accounts):
            if existing.id == account.id:
                self._accounts[idx] = account
                if not account.is_sample:
                    self.repository.update_account(account)
                logger.info(f"Account {account.display_name} updated.")
                return True
        return False

    def remove_account(self, account_id: str) -> bool:
        """Remove account from memory, repository, credential vault, and rclone remote."""
        target = None
        for a in self._accounts:
            if a.id == account_id:
                target = a
                break

        if not target:
            return False

        self._accounts.remove(target)

        if not target.is_sample:
            self.repository.delete_account(account_id)
            self.credential_service.delete_token(account_id)
            self.executor.submit(self.rclone_service.delete_remote, target.remote_name)

        # If all real accounts are deleted, restore sample preview
        if not self._accounts:
            self._accounts = get_sample_accounts()

        logger.info(f"Removed account {account_id}")
        return True

    def refresh_storage_quotas(self, on_complete: Callable[[], None] | None = None):
        """Asynchronously refresh storage quotas for real accounts from cloud."""

        def _task():
            real_accounts = [a for a in self._accounts if not a.is_sample]
            for acc in real_accounts:
                try:
                    quota = self.rclone_service.get_account_storage_quota(acc.remote_name)
                    if quota.get("total", 0) > 0:
                        acc.used_storage_bytes = quota.get("used", 0)
                        acc.total_storage_bytes = quota.get("total", 0)
                except Exception as e:
                    logger.warning(f"Failed to refresh quota for {acc.display_name}: {e}")
            if on_complete:
                on_complete()

        self.executor.submit(_task)
