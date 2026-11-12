"""Shared pytest fixtures for GDrive Manager test suite."""

import sys
from pathlib import Path
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import customtkinter as ctk
from app.ui.main_window import MainWindow

@pytest.fixture(scope="session")
def main_app():
    """Create a single session-scoped MainWindow instance for all UI tests."""
    app = MainWindow(enable_tray=False)
    app.withdraw()
    yield app
    try:
        app.destroy()
    except Exception:
        pass

@pytest.fixture(scope="session")
def tk_root(main_app):
    """Alias fixture providing the root window for dialog tests."""
    return main_app
