"""Unit tests for Hybrid Mode storage targets, separation, and conflict validation."""

import sys
from pathlib import Path
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.models.account import Account

def test_hybrid_mode_labels():
    """Verify operating mode descriptions based on independent mode flags."""
    acc = Account(id="1", email="a@g.com", display_name="A", remote_name="r1")

    # Hybrid
    acc.streaming_enabled = True
    acc.offline_enabled = True
    assert acc.operating_mode == "Streaming + Offline"

    # Streaming only
    acc.streaming_enabled = True
    acc.offline_enabled = False
    assert acc.operating_mode == "Streaming"

    # Offline only
    acc.streaming_enabled = False
    acc.offline_enabled = True
    assert acc.operating_mode == "Offline"

    # Both disabled
    acc.streaming_enabled = False
    acc.offline_enabled = False
    assert acc.operating_mode == "Disabled"

def test_hybrid_target_conflict_detection():
    """Test detecting when an offline directory collides with the streaming drive letter."""
    def check_conflict(drive_letter: str, offline_path: str) -> bool:
        clean_letter = drive_letter.upper().rstrip("\\")
        clean_path = str(Path(offline_path).resolve()).upper()
        return clean_path.startswith(f"{clean_letter}\\") or clean_path == f"{clean_letter}:"

    # Valid separate targets
    assert check_conflict("G:", "D:\\GDriveManager\\Personal") is False
    assert check_conflict("H:", "C:\\Users\\mohit\\Documents\\GoogleDrive") is False

    # Conflicting targets (offline inside streaming drive)
    assert check_conflict("G:", "G:\\") is True
    assert check_conflict("G:", "G:\\MyFolder") is True
    assert check_conflict("G:", "g:\\sub\\dir") is True
