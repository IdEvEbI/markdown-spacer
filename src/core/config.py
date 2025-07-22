"""
配置管理模块
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """配置管理类"""

    def __init__(self, config_file: Optional[Path] = None) -> None:
        """初始化配置

        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.settings: Dict[str, Any] = {}
        self._load_defaults()
        if config_file:
            self._load_from_file()

    def _load_defaults(self) -> None:
        """加载默认配置"""
        self.settings = {
            "debug": False,
            "log_level": "INFO",
            "timeout": 30,
            "bold_quotes": False,
            "backup_files": True,
            "recursive": False,
        }

    def _load_from_file(self) -> None:
        """从文件加载配置"""
        # TODO: 实现文件加载逻辑
        pass

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值

        Args:
            key: 配置键
            default: 默认值

        Returns:
            配置值
        """
        return self.settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """设置配置值

        Args:
            key: 配置键
            value: 配置值
        """
        self.settings[key] = value

    def update_from_env(self) -> None:
        """从环境变量更新配置"""
        env_mapping = {
            "MARKDOWN_SPACER_DEBUG": "debug",
            "MARKDOWN_SPACER_LOG_LEVEL": "log_level",
            "MARKDOWN_SPACER_TIMEOUT": "timeout",
            "MARKDOWN_SPACER_BOLD_QUOTES": "bold_quotes",
        }

        for env_key, config_key in env_mapping.items():
            env_value = os.getenv(env_key)
            if env_value is not None:
                # 类型转换
                if config_key == "debug":
                    self.settings[config_key] = env_value.lower() in (
                        "true",
                        "1",
                        "yes",
                    )
                elif config_key == "timeout":
                    try:
                        self.settings[config_key] = int(env_value)
                    except ValueError:
                        pass
                elif config_key == "bold_quotes":
                    self.settings[config_key] = env_value.lower() in (
                        "true",
                        "1",
                        "yes",
                    )
                else:
                    self.settings[config_key] = env_value
