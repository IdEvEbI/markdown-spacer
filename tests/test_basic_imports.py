"""
基础模块导入测试
"""

from src.core.file_handler import (
    is_markdown_file,
    read_markdown_file,
    write_markdown_file,
)

# 已移除 FileHandler 类相关测试，保持与当前实现一致


def test_core_modules_import() -> None:
    assert callable(is_markdown_file)
    assert callable(read_markdown_file)
    assert callable(write_markdown_file)


# 其他测试可根据需要补充
