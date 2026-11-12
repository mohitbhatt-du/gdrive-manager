"""Account data model for Google Drive accounts."""

from dataclasses import dataclass
from typing import Any


@dataclass
class Account:
    id: str
    email: str
    display_name: str
    remote_name: str
    drive_letter: str = "G:"
    streaming_enabled: bool = True
    offline_enabled: bool = False
    offline_path: str = ""
    cache_size: str = "10G"
    cache_expiry: str = "24h"
    read_only: bool = False
    auto_mount: bool = False
    used_storage_bytes: int = 0
    total_storage_bytes: int = 15 * 1024 * 1024 * 1024  # Default 15 GB
    is_mounted: bool = False
    mount_pid: int | None = None
    status: str = "Disconnected"  # Connected, Mounted, Syncing, Disconnected, Error
    status_message: str = ""
    is_sample: bool = False

    @property
    def operating_mode(self) -> str:
        """Return the current operating mode description."""
        if self.streaming_enabled and self.offline_enabled:
            return "Streaming + Offline"
        elif self.streaming_enabled:
            return "Streaming"
        elif self.offline_enabled:
            return "Offline"
        return "Disabled"

    @property
    def storage_percentage(self) -> float:
        """Return percentage of cloud storage used (0.0 to 100.0)."""
        if self.total_storage_bytes <= 0:
            return 0.0
        pct = (self.used_storage_bytes / self.total_storage_bytes) * 100
        return min(max(pct, 0.0), 100.0)

    @staticmethod
    def format_bytes(b: int) -> str:
        """Format byte count into human-readable representation."""
        if b <= 0:
            return "0 GB"
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if b < 1024.0:
                return f"{b:.1f} {unit}"
            b /= 1024.0
        return f"{b:.1f} PB"

    @property
    def formatted_used(self) -> str:
        return self.format_bytes(self.used_storage_bytes)

    @property
    def formatted_total(self) -> str:
        return self.format_bytes(self.total_storage_bytes)

    def to_dict(self) -> dict[str, Any]:
        """Convert account object to serializable dictionary."""
        return {
            "id": self.id,
            "email": self.email,
            "display_name": self.display_name,
            "remote_name": self.remote_name,
            "drive_letter": self.drive_letter,
            "streaming_enabled": self.streaming_enabled,
            "offline_enabled": self.offline_enabled,
            "offline_path": self.offline_path,
            "cache_size": self.cache_size,
            "cache_expiry": self.cache_expiry,
            "read_only": self.read_only,
            "auto_mount": self.auto_mount,
            "used_storage_bytes": self.used_storage_bytes,
            "total_storage_bytes": self.total_storage_bytes,
            "is_mounted": self.is_mounted,
            "status": self.status,
            "is_sample": self.is_sample,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Account":
        """Instantiate Account from dictionary."""
        return cls(
            id=data.get("id", ""),
            email=data.get("email", ""),
            display_name=data.get("display_name", ""),
            remote_name=data.get("remote_name", ""),
            drive_letter=data.get("drive_letter", "G:"),
            streaming_enabled=data.get("streaming_enabled", True),
            offline_enabled=data.get("offline_enabled", False),
            offline_path=data.get("offline_path", ""),
            cache_size=data.get("cache_size", "10G"),
            cache_expiry=data.get("cache_expiry", "24h"),
            read_only=data.get("read_only", False),
            auto_mount=data.get("auto_mount", False),
            used_storage_bytes=data.get("used_storage_bytes", 0),
            total_storage_bytes=data.get("total_storage_bytes", 15 * 1024 * 1024 * 1024),
            is_mounted=data.get("is_mounted", False),
            status=data.get("status", "Disconnected"),
            is_sample=data.get("is_sample", False),
        )


def get_sample_accounts() -> list[Account]:
    """Provide realistic sample account data for Phase 1 UI preview."""
    GB = 1024 * 1024 * 1024
    TB = 1024 * GB
    return [
        Account(
            id="sample_personal",
            email="alex.chen.personal@gmail.com",
            display_name="Personal Drive",
            remote_name="gdrive_personal",
            drive_letter="G:",
            streaming_enabled=True,
            offline_enabled=True,
            offline_path="D:/GDriveManager/Personal",
            cache_size="15G",
            used_storage_bytes=int(11.4 * GB),
            total_storage_bytes=15 * GB,
            is_mounted=True,
            status="Mounted",
            is_sample=True,
        ),
        Account(
            id="sample_work",
            email="alex.chen@workplace-ai.com",
            display_name="Work & Projects",
            remote_name="gdrive_work",
            drive_letter="H:",
            streaming_enabled=True,
            offline_enabled=False,
            offline_path="",
            cache_size="25G",
            used_storage_bytes=int(742 * GB),
            total_storage_bytes=2 * TB,
            is_mounted=True,
            status="Mounted",
            is_sample=True,
        ),
        Account(
            id="sample_university",
            email="alex.c@alumni.stanford.edu",
            display_name="Academic Archives",
            remote_name="gdrive_academic",
            drive_letter="I:",
            streaming_enabled=False,
            offline_enabled=True,
            offline_path="D:/GDriveManager/StanfordArchives",
            cache_size="5G",
            used_storage_bytes=int(64.8 * GB),
            total_storage_bytes=100 * GB,
            is_mounted=False,
            status="Connected",
            is_sample=True,
        ),
        Account(
            id="sample_secondary",
            email="chen.backups@gmail.com",
            display_name="Media Backups",
            remote_name="gdrive_media",
            drive_letter="J:",
            streaming_enabled=True,
            offline_enabled=True,
            offline_path="E:/MediaBackups",
            cache_size="50G",
            used_storage_bytes=int(1.8 * TB),
            total_storage_bytes=2 * TB,
            is_mounted=False,
            status="Disconnected",
            is_sample=True,
        ),
    ]
