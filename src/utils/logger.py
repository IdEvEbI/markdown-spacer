"""
markdown-spacer 日志工具模块。

本模块提供日志记录器的配置和管理功能，
支持不同级别的日志输出和格式化。
"""

import logging
from typing import Optional


def setup_logger(verbose: bool = False) -> logging.Logger:
    """设置 markdown-spacer 的日志记录器。

    Args:
        verbose: 是否启用详细日志输出

    Returns:
        配置好的日志记录器实例

    Note:
        如果日志记录器已经存在处理器，则直接返回现有实例，
        避免重复添加处理器。
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
    """获取日志记录器实例。

    Args:
        name: 日志记录器名称（可选）

    Returns:
        日志记录器实例

    Note:
        如果不指定名称，返回默认的 "markdown-spacer" 记录器。
        如果指定名称，返回 "markdown-spacer.{name}" 格式的记录器。
    """
    if name:
        return logging.getLogger(f"markdown-spacer.{name}")
    return logging.getLogger("markdown-spacer")
