"""Storage Manager calculating cloud quota, local offline directory usage, and VFS cache size."""

import os
import shutil
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

from app.models.account import Account
from app.services.rclone_service import RcloneService
from app.utils.logger import get_logger
from app.utils.paths import get_app_data_dir

logger = get_logger("StorageManager")


@dataclass
class StorageBreakdown:
    """Detailed storage metrics distinguishing cloud, offline directory, and VFS streaming cache."""

    account_id: str
    cloud_used_bytes: int = 0
    cloud_total_bytes: int = 0
    offline_used_bytes: int = 0
    offline_file_count: int = 0
    vfs_cache_used_bytes: int = 0
    vfs_cache_limit: str = "10G"
    is_quota_exact: bool = True

    @staticmethod
    def format_bytes(b: int | float) -> str:
        val = float(b)
        if val <= 0:
            return "0 B"
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if val < 1024.0:
                return f"{val:.1f} {unit}"
            val /= 1024.0
        return f"{val:.1f} PB"

    @property
    def formatted_cloud_used(self) -> str:
        return self.format_bytes(self.cloud_used_bytes)

    @property
    def formatted_cloud_total(self) -> str:
        return self.format_bytes(self.cloud_total_bytes)

    @property
    def formatted_offline_used(self) -> str:
        return self.format_bytes(self.offline_used_bytes)

    @property
    def formatted_cache_used(self) -> str:
        return self.format_bytes(self.vfs_cache_used_bytes)

    @property
    def cloud_percentage(self) -> float:
        if self.cloud_total_bytes <= 0:
            return 0.0
        pct = (self.cloud_used_bytes / self.cloud_total_bytes) * 100
        return min(max(pct, 0.0), 100.0)


class StorageManager:
    """Manages computation and isolation of cloud, offline, and temporary cache metrics."""

    def __init__(self, rclone_service: RcloneService):
        self.rclone_service = rclone_service
        self.executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="StorageWorker")

    def calculate_storage_breakdown(self, account: Account) -> StorageBreakdown:
        """Calculate complete storage breakdown for an account."""
        # 1. Cloud Storage
        cloud_used = account.used_storage_bytes
        cloud_total = account.total_storage_bytes
        is_exact = True

        if not account.is_sample and self.rclone_service.is_available():
            try:
                quota = self.rclone_service.get_account_storage_quota(account.remote_name)
                if quota.get("total", 0) > 0:
                    cloud_used = quota.get("used", 0)
                    cloud_total = quota.get("total", 0)
                else:
                    is_exact = False
            except Exception as e:
                logger.warning(f"Failed to query exact cloud quota for {account.display_name}: {e}")
                is_exact = False

        # 2. Local Offline Directory Storage
        offline_bytes = 0
        offline_files = 0
        if account.offline_enabled and account.offline_path:
            p = Path(account.offline_path)
            if p.exists() and p.is_dir():
                try:
                    for entry in os.scandir(str(p)):
                        if entry.is_file(follow_symlinks=False):
                            offline_bytes += entry.stat().st_size
                            offline_files += 1
                        elif entry.is_dir(follow_symlinks=False):
                            for root, _, files in os.walk(entry.path):
                                for f in files:
                                    try:
                                        fp = os.path.join(root, f)
                                        offline_bytes += os.path.getsize(fp)
                                        offline_files += 1
                                    except Exception:
                                        pass
                except Exception as e:
                    logger.warning(f"Error scanning offline directory {p}: {e}")

        # 3. Local VFS Streaming Cache Storage
        cache_bytes = 0
        cache_dir = get_app_data_dir() / "vfs_cache" / account.id
        if cache_dir.exists() and cache_dir.is_dir():
            try:
                for root, _, files in os.walk(str(cache_dir)):
                    for f in files:
                        try:
                            cache_bytes += os.path.getsize(os.path.join(root, f))
                        except Exception:
                            pass
            except Exception as e:
                logger.warning(f"Error scanning VFS cache directory {cache_dir}: {e}")

        return StorageBreakdown(
            account_id=account.id,
            cloud_used_bytes=cloud_used,
            cloud_total_bytes=cloud_total,
            offline_used_bytes=offline_bytes,
            offline_file_count=offline_files,
            vfs_cache_used_bytes=cache_bytes,
            vfs_cache_limit=account.cache_size,
            is_quota_exact=is_exact,
        )

    def calculate_async(self, account: Account, callback: Callable[[StorageBreakdown], None]):
        """Asynchronously compute breakdown and invoke callback."""

        def _task():
            breakdown = self.calculate_storage_breakdown(account)
            callback(breakdown)

        self.executor.submit(_task)

    def purge_vfs_cache(self, account_id: str) -> bool:
        """Purge temporary VFS cache files without affecting cloud or offline data."""
        cache_dir = get_app_data_dir() / "vfs_cache" / account_id
        if not cache_dir.exists():
            return True

        try:
            shutil.rmtree(cache_dir)
            cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Purged VFS streaming cache for account {account_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to purge VFS cache for account {account_id}: {e}")
            return False
