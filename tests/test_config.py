"""
配置管理模块测试
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from src.core.config import Config


class TestConfig:
    """配置管理类测试"""

    def test_init_without_config_file(self) -> None:
        """测试无配置文件初始化"""
        config = Config()
        assert config.config_file is None
        assert config.settings["debug"] is False
        assert config.settings["log_level"] == "INFO"
        assert config.settings["timeout"] == 30
        assert config.settings["bold_quotes"] is False
        assert config.settings["backup_files"] is True
        assert config.settings["recursive"] is False

    def test_init_with_config_file(self) -> None:
        """测试有配置文件初始化"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            config_file = Path(f.name)

        try:
            config = Config(config_file)
            assert config.config_file == config_file
        finally:
            config_file.unlink()

    def test_get_existing_key(self) -> None:
        """测试获取存在的配置键"""
        config = Config()
        assert config.get("debug") is False
        assert config.get("log_level") == "INFO"

    def test_get_nonexistent_key(self) -> None:
        """测试获取不存在的配置键"""
        config = Config()
        assert config.get("nonexistent") is None
        assert config.get("nonexistent", "default") == "default"

    def test_set_key(self) -> None:
        """测试设置配置键"""
        config = Config()
        config.set("custom_key", "custom_value")
        assert config.get("custom_key") == "custom_value"

    def test_update_from_env_debug_true(self) -> None:
        """测试从环境变量更新debug配置（true）"""
        config = Config()
        with patch.dict(os.environ, {"MARKDOWN_SPACER_DEBUG": "true"}):
            config.update_from_env()
            assert config.get("debug") is True

    def test_update_from_env_debug_false(self) -> None:
        """测试从环境变量更新debug配置（false）"""
        config = Config()
        with patch.dict(os.environ, {"MARKDOWN_SPACER_DEBUG": "false"}):
            config.update_from_env()
            assert config.get("debug") is False

    def test_update_from_env_log_level(self) -> None:
        """测试从环境变量更新日志级别"""
        config = Config()
        with patch.dict(os.environ, {"MARKDOWN_SPACER_LOG_LEVEL": "DEBUG"}):
            config.update_from_env()
            assert config.get("log_level") == "DEBUG"

    def test_update_from_env_timeout_valid(self) -> None:
        """测试从环境变量更新超时配置（有效值）"""
        config = Config()
        with patch.dict(os.environ, {"MARKDOWN_SPACER_TIMEOUT": "60"}):
            config.update_from_env()
            assert config.get("timeout") == 60

    def test_update_from_env_timeout_invalid(self) -> None:
        """测试从环境变量更新超时配置（无效值）"""
        config = Config()
        original_timeout = config.get("timeout")
        with patch.dict(os.environ, {"MARKDOWN_SPACER_TIMEOUT": "invalid"}):
            config.update_from_env()
            assert config.get("timeout") == original_timeout

    def test_update_from_env_bold_quotes_true(self) -> None:
        """测试从环境变量更新双引号加粗配置（true）"""
        config = Config()
        with patch.dict(os.environ, {"MARKDOWN_SPACER_BOLD_QUOTES": "true"}):
            config.update_from_env()
            assert config.get("bold_quotes") is True

    def test_update_from_env_bold_quotes_false(self) -> None:
        """测试从环境变量更新双引号加粗配置（false）"""
        config = Config()
        with patch.dict(os.environ, {"MARKDOWN_SPACER_BOLD_QUOTES": "false"}):
            config.update_from_env()
            assert config.get("bold_quotes") is False

    def test_update_from_env_multiple_values(self) -> None:
        """测试从环境变量更新多个配置"""
        config = Config()
        with patch.dict(
            os.environ,
            {
                "MARKDOWN_SPACER_DEBUG": "true",
                "MARKDOWN_SPACER_LOG_LEVEL": "ERROR",
                "MARKDOWN_SPACER_TIMEOUT": "120",
                "MARKDOWN_SPACER_BOLD_QUOTES": "1",
            },
        ):
            config.update_from_env()
            assert config.get("debug") is True
            assert config.get("log_level") == "ERROR"
            assert config.get("timeout") == 120
            assert config.get("bold_quotes") is True
