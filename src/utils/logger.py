import logging
import os
from pathlib import Path

from src.core.log_config import setup_logging

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_IS_LOGGING_CONFIGURED = False


def _configure_logging_once() -> None:
    global _IS_LOGGING_CONFIGURED
    if _IS_LOGGING_CONFIGURED:
        return
    setup_logging()
    _IS_LOGGING_CONFIGURED = True


def set_logger(file_path: str) -> logging.Logger:
    """Create a logger with the relative path as its name.

    Usage:
        logger = set_logger(__file__)
        # Produces logger named e.g. "services.apps.pnl.pnl_revamp"

    Args:
        file_path: Pass __file__ to get the relative module path automatically.
    """
    _configure_logging_once()

    try:
        rel = os.path.relpath(file_path, _PROJECT_ROOT)
        name = rel.replace(os.sep, ".").replace("/", ".").removesuffix(".py")
    except ValueError:
        name = file_path

    return logging.getLogger(name)
