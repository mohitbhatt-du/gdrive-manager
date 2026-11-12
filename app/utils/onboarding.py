"""Onboarding and first-launch state management."""

from pathlib import Path
from app.utils.paths import get_app_data_dir, DATA_DIR

def _get_marker_path() -> Path:
    try:
        return get_app_data_dir() / ".onboarding_completed"
    except Exception:
        return DATA_DIR / ".onboarding_completed"

def is_onboarding_completed() -> bool:
    """Return True if user has previously completed or dismissed first-launch onboarding."""
    return _get_marker_path().exists()

def set_onboarding_completed(completed: bool = True):
    """Mark onboarding status."""
    marker = _get_marker_path()
    if completed:
        try:
            marker.parent.mkdir(parents=True, exist_ok=True)
            marker.touch()
        except Exception:
            pass
    else:
        if marker.exists():
            try:
                marker.unlink()
            except Exception:
                pass

def reset_onboarding():
    """Reset onboarding marker to show wizard on next launch."""
    set_onboarding_completed(False)
