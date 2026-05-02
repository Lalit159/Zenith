"""
Centralized logging configuration for Zenith order matching engine.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Create logs directory if it doesn't exist
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Configure logging format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def setup_logger(name: str, level=logging.DEBUG) -> logging.Logger:
    """
    Setup and return a logger with console and file handlers.

    Args:
        name: Logger name (usually __name__)
        level: Logging level (default: DEBUG)

    Returns:
        Configured logger instance

    Log Level Hierarchy (from least to most severe):
        DEBUG (10) → INFO (20) → WARNING (30) → ERROR (40) → CRITICAL (50)

    Handler Configuration:
        - Console Handler: INFO level (shows INFO, WARNING, ERROR, CRITICAL)
          User-facing output, excludes low-level DEBUG details
        - File Handler: DEBUG level (shows DEBUG, INFO, WARNING, ERROR, CRITICAL)
          Developer-focused detailed logs for debugging and auditing
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding duplicate handlers
    if logger.handlers:
        return logger

    # Console handler (INFO level and above)
    # Shows: INFO, WARNING, ERROR, CRITICAL (but NOT DEBUG)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    console_handler.setFormatter(console_formatter)

    # File handler (DEBUG level and above - all levels)
    # Shows: DEBUG, INFO, WARNING, ERROR, CRITICAL
    # Rotating: 10MB per file, keeps 5 backups (prevents disk space issues)
    file_handler = RotatingFileHandler(
        LOG_DIR / f"{name}.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    file_handler.setFormatter(file_formatter)

    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
