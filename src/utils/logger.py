"""
Logging utilities for markdown-spacer.
"""

import logging
from typing import Optional


def setup_logger(verbose: bool = False) -> logging.Logger:
    """Setup logger for markdown-spacer.

    Args:
        verbose: Whether to enable verbose logging

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("markdown-spacer")

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    # Set log level
    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # Create console handler
    console_handler = logging.StreamHandler()

    # Create formatter
    if verbose:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    else:
        formatter = logging.Formatter("%(message)s")

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get logger instance.

    Args:
        name: Logger name (optional)

    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(f"markdown-spacer.{name}")
    return logging.getLogger("markdown-spacer")
