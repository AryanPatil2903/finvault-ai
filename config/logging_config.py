"""
Structured logging setup with rotating file handler and console output.
Call setup_logging() once at application startup.
"""

import logging
import logging.config
import os
import sys
from typing import Any, Dict


# ── Log configuration dictionary ─────────────────────────────────────────────
LOGGING_CONFIG: Dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "detailed": {
            "format": (
                "%(asctime)s | %(levelname)-8s | "
                "%(name)s:%(funcName)s:%(lineno)d | %(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "%(levelname)s | %(name)s | %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": "detailed",
            "level": "DEBUG",
        },
        "file_app": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/app.log",
            "maxBytes": 10 * 1024 * 1024,   # 10 MB before rotation
            "backupCount": 5,
            "formatter": "detailed",
            "level": "INFO",
        },
        "file_error": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/error.log",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "detailed",
            "level": "ERROR",
        },
    },
    "loggers": {
        "finvault": {
            "handlers": ["console", "file_app", "file_error"],
            "level": "DEBUG",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "sqlalchemy.engine": {
            "handlers": ["console"],
            "level": "WARNING",   # Change to INFO to see all SQL
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
}


def setup_logging() -> None:
    """Initialize logging — must be called once at application startup."""
    os.makedirs("logs", exist_ok=True)
    logging.config.dictConfig(LOGGING_CONFIG)


def get_logger(name: str) -> logging.Logger:
    """
    Return a named child logger under the 'finvault' namespace.

    Usage:
        logger = get_logger("finance")
        logger.info("EMI calculated")
    """
    return logging.getLogger(f"finvault.{name}")