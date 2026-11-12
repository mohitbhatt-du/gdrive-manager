"""Transfer job data model for downloads, uploads, and synchronizations."""

from dataclasses import dataclass
from typing import Optional, List
import time

@dataclass
class TransferJob:
    id: str
    account_name: str
    item_name: str
    operation_type: str  # "Download", "Upload", "Sync (Cloud -> Local)", "Sync (Local -> Cloud)", "Two-Way Sync"
    total_bytes: int
    transferred_bytes: int = 0
    speed_bytes_per_sec: float = 0.0
    eta_seconds: Optional[int] = None
    status: str = "Queued"  # "Queued", "Running", "Paused", "Completed", "Failed", "Cancelled"
    error_message: str = ""
    is_sample: bool = False

    @property
    def progress_percentage(self) -> float:
        if self.total_bytes <= 0:
            return 0.0
        pct = (self.transferred_bytes / self.total_bytes) * 100
        return min(max(pct, 0.0), 100.0)

    @staticmethod
    def format_bytes(b: int) -> str:
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if b < 1024.0:
                return f"{b:.1f} {unit}"
            b /= 1024.0
        return f"{b:.1f} PB"

    @property
    def formatted_transferred(self) -> str:
        return self.format_bytes(self.transferred_bytes)

    @property
    def formatted_total(self) -> str:
        return self.format_bytes(self.total_bytes)

    @property
    def formatted_speed(self) -> str:
        if self.status != "Running" or self.speed_bytes_per_sec <= 0:
            return "-- MB/s"
        return f"{self.format_bytes(int(self.speed_bytes_per_sec))}/s"

    @property
    def formatted_eta(self) -> str:
        if self.status != "Running" or self.eta_seconds is None or self.eta_seconds < 0:
            return "--:--"
        mins, secs = divmod(self.eta_seconds, 60)
        hours, mins = divmod(mins, 60)
        if hours > 0:
            return f"{hours}h {mins:02d}m"
        return f"{mins:02d}m {secs:02d}s"

def get_sample_transfers() -> List[TransferJob]:
    """Provide sample transfer jobs for Phase 1 UI preview."""
    MB = 1024 * 1024
    GB = 1024 * MB
    return [
        TransferJob(
            id="job-101",
            account_name="Personal Drive",
            item_name="Quarterly_Financial_Report_2026.xlsx",
            operation_type="Download",
            total_bytes=42 * MB,
            transferred_bytes=int(28.5 * MB),
            speed_bytes_per_sec=4.2 * MB,
            eta_seconds=3,
            status="Running",
            is_sample=True
        ),
        TransferJob(
            id="job-102",
            account_name="Work & Projects",
            item_name="AI_Model_Weights_v2.bin",
            operation_type="Upload",
            total_bytes=int(1.8 * GB),
            transferred_bytes=int(1.2 * GB),
            speed_bytes_per_sec=12.5 * MB,
            eta_seconds=49,
            status="Running",
            is_sample=True
        ),
        TransferJob(
            id="job-103",
            account_name="Academic Archives",
            item_name="Research_Papers_2025_Archive.tar.gz",
            operation_type="Sync (Cloud -> Local)",
            total_bytes=int(4.5 * GB),
            transferred_bytes=int(4.5 * GB),
            speed_bytes_per_sec=0,
            eta_seconds=0,
            status="Completed",
            is_sample=True
        ),
        TransferJob(
            id="job-104",
            account_name="Media Backups",
            item_name="4K_Drone_Footage_RAW.mov",
            operation_type="Upload",
            total_bytes=int(8.4 * GB),
            transferred_bytes=int(2.1 * GB),
            speed_bytes_per_sec=0,
            eta_seconds=None,
            status="Paused",
            is_sample=True
        ),
        TransferJob(
            id="job-105",
            account_name="Personal Drive",
            item_name="Restricted_Encrypted_Backup.kdbx",
            operation_type="Download",
            total_bytes=15 * MB,
            transferred_bytes=2 * MB,
            speed_bytes_per_sec=0,
            eta_seconds=None,
            status="Failed",
            error_message="Access denied: Token expired or permission revoked",
            is_sample=True
        ),
    ]
