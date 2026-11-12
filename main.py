"""GDrive Manager - Windows Desktop Application Entrypoint."""

import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import customtkinter as ctk

from app.ui.main_window import MainWindow
from app.utils.logger import get_logger
from app.utils.paths import ensure_directories


def main():
    """Start GDrive Manager desktop application."""
    # Ensure logs, data, and asset directories exist
    ensure_directories()

    logger = get_logger("GDriveManager")
    logger.info("Starting GDrive Manager Desktop Application...")

    # Set CustomTkinter design mode
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")

    # Launch GUI
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
