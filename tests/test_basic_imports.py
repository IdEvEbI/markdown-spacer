"""
基础模块导入测试
"""

import pytest


def test_core_modules_import() -> None:
    """测试核心模块导入"""
    try:
        from src.cli.parser import parse_arguments
        from src.core.config import Config
        from src.core.file_handler import FileHandler
        from src.core.formatter import MarkdownFormatter
        from src.utils.exceptions import MarkdownSpacerError
        from src.utils.logger import setup_logger

        # 验证导入的模块
        assert MarkdownFormatter is not None
        assert FileHandler is not None
        assert Config is not None
        assert parse_arguments is not None
        assert setup_logger is not None
        assert MarkdownSpacerError is not None
    except ImportError as e:
        pytest.fail(f"Failed to import core modules: {e}")


def test_main_module_import() -> None:
    """测试主模块导入"""
    try:
        from src.markdown_spacer import main

        assert callable(main)
    except ImportError as e:
        pytest.fail(f"Failed to import main module: {e}")


def test_formatter_initialization() -> None:
    """测试格式化器初始化"""
    from src.core.formatter import MarkdownFormatter

    formatter = MarkdownFormatter()
    assert formatter is not None
    assert hasattr(formatter, "format_content")


def test_file_handler_initialization() -> None:
    """测试文件处理器初始化"""
    from src.core.file_handler import FileHandler

    handler = FileHandler()
    assert handler is not None
    assert hasattr(handler, "process_single_file")


def test_config_initialization() -> None:
    """测试配置管理器初始化"""
    from src.core.config import Config

    config = Config()
    assert config is not None
    assert config.get("debug") is False
    assert config.get("log_level") == "INFO"
