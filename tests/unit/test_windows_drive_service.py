"""Unit tests for WindowsDriveService."""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.services.windows_drive_service import WindowsDriveService


def test_is_drive_ready(mocker):
    """Test checking drive path readiness."""
    mocker.patch("os.path.exists", return_value=True)
    assert WindowsDriveService.is_drive_ready("G:") is True

    mocker.patch("os.path.exists", return_value=False)
    assert WindowsDriveService.is_drive_ready("Z:") is False


def test_open_in_explorer(mocker):
    """Test explorer.exe invocation."""
    mock_popen = mocker.patch("subprocess.Popen")
    assert WindowsDriveService.open_in_explorer("G:") is True
    mock_popen.assert_called_once_with(["explorer.exe", "G:\\"])
