"""Google OAuth 2.0 authentication manager coordinating rclone remote creation."""

import os
import subprocess
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor

from app.config.account_repository import AccountRepository
from app.models.account import Account
from app.services.credential_service import CredentialService
from app.services.rclone_service import RcloneService
from app.utils.logger import get_logger

logger = get_logger("AuthManager")


class AuthManager:
    """Handles Google OAuth authentication lifecycle, remote creation, and token vaulting."""

    def __init__(
        self,
        rclone_service: RcloneService,
        account_repo: AccountRepository,
        credential_service: CredentialService,
    ):
        self.rclone_service = rclone_service
        self.account_repo = account_repo
        self.credential_service = credential_service
        self.executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="AuthWorker")

    def start_google_auth(
        self,
        account_name: str,
        drive_letter: str,
        streaming_enabled: bool,
        offline_enabled: bool,
        offline_path: str,
        cache_size: str,
        on_status_update: Callable[[str], None],
        on_success: Callable[[Account], None],
        on_error: Callable[[str], None],
    ):
        """Execute Google OAuth flow asynchronously in background thread."""
        self.executor.submit(
            self._run_auth_flow,
            account_name,
            drive_letter,
            streaming_enabled,
            offline_enabled,
            offline_path,
            cache_size,
            on_status_update,
            on_success,
            on_error,
        )

    def _run_auth_flow(
        self,
        account_name: str,
        drive_letter: str,
        streaming_enabled: bool,
        offline_enabled: bool,
        offline_path: str,
        cache_size: str,
        on_status_update: Callable[[str], None],
        on_success: Callable[[Account], None],
        on_error: Callable[[str], None],
    ):
        try:
            exe = self.rclone_service.rclone_exe
            if not exe:
                on_error("rclone executable not found. Please install rclone from Settings.")
                return

            # Sanitize remote name for rclone
            remote_name = "gdrive_" + "".join(c if c.isalnum() else "_" for c in account_name.lower())
            account_id = remote_name

            # Check if remote already exists in repository
            existing_accounts = self.account_repo.load_all()
            for acc in existing_accounts:
                if acc.remote_name == remote_name:
                    on_error(f"An account with remote name '{remote_name}' already exists.")
                    return

            on_status_update("Launching browser for Google OAuth sign-in...")
            logger.info(f"Starting Google Drive OAuth flow for remote '{remote_name}'...")

            # Run rclone config create <remote_name> drive scope drive config_is_local true
            cmd = [
                exe,
                "--config",
                str(self.rclone_service.config_path),
                "config",
                "create",
                remote_name,
                "drive",
                "scope",
                "drive",
                "config_is_local",
                "true",
            ]

            flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=flags,
            )

            on_status_update("Waiting for Google authorization in browser... Please sign in.")
            stdout, stderr = process.communicate(timeout=180)

            if process.returncode != 0:
                err_msg = stderr.strip() or stdout.strip() or "OAuth authentication cancelled or failed."
                logger.error(f"rclone config create failed: {err_msg}")
                on_error(f"Authentication failed: {err_msg}")
                return

            on_status_update("Retrieving cloud account storage info...")
            logger.info(f"Remote '{remote_name}' created successfully. Fetching quota...")

            # Retrieve real storage quota
            quota = self.rclone_service.get_account_storage_quota(remote_name)
            used_bytes = quota.get("used", 0)
            total_bytes = quota.get("total", 15 * 1024 * 1024 * 1024)

            # Secure tokens in Windows Credential Manager
            self.credential_service.store_token(
                account_id, {"remote_name": remote_name, "config_path": str(self.rclone_service.config_path)}
            )

            # Create Account model
            new_account = Account(
                id=account_id,
                email=f"{account_name.lower().replace(' ', '.')}@gmail.com",
                display_name=account_name,
                remote_name=remote_name,
                drive_letter=drive_letter,
                streaming_enabled=streaming_enabled,
                offline_enabled=offline_enabled,
                offline_path=offline_path,
                cache_size=cache_size,
                used_storage_bytes=used_bytes,
                total_storage_bytes=total_bytes,
                is_mounted=False,
                status="Connected",
                is_sample=False,
            )

            # Persist to repository
            self.account_repo.add_account(new_account)
            logger.info(f"Account '{account_name}' saved to repository.")

            on_success(new_account)

        except subprocess.TimeoutExpired:
            on_error("Google authorization timed out (3 minutes exceeded).")
        except Exception as e:
            logger.error(f"Unexpected error during auth flow: {e}", exc_info=True)
            on_error(f"Unexpected error: {str(e)}")
