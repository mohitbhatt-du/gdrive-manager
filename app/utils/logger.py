"""Application logging configuration."""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from app.utils.paths import LOGS_DIR

_logger: logging.Logger | None = None

def get_logger(name: str = "GDriveManager") -> logging.Logger:
    """Get or configure the application logger."""
    global _logger
    if _logger is not None and name == "GDriveManager":
        return _logger

    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        log_file = LOGS_DIR / "app.log"

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s:%(module)s:%(lineno)d]: %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(module)s]: %(message)s",
            datefmt="%H:%M:%S"
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    if name == "GDriveManager":
        _logger = logger
    return logger
