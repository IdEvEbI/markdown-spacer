"""
markdown-spacer 格式化器测试模块。

本模块包含 MarkdownFormatter 类的单元测试，
验证中英文空格处理、特殊内容保护等功能的正确性。
"""

import pytest

from src.core.formatter import MarkdownFormatter


class TestMarkdownFormatter:
    """MarkdownFormatter 类测试套件。"""

    def test_basic_initialization(self) -> None:
        """测试基本初始化。"""
        fmt = MarkdownFormatter()
        assert fmt.bold_quotes is False
        assert fmt.debug is False
        assert fmt._custom_rules == []

    def test_initialization_with_bold_quotes(self) -> None:
        """测试启用中文双引号加粗的初始化。"""
        fmt = MarkdownFormatter(bold_quotes=True)
        assert fmt.bold_quotes is True

    def test_initialization_with_debug(self) -> None:
        """测试启用调试模式的初始化。"""
        fmt = MarkdownFormatter(debug=True)
        assert fmt.debug is True

    def test_format_content_basic(self) -> None:
        """测试基本内容格式化。"""
        fmt = MarkdownFormatter()
        # 基本中英文空格处理
        assert fmt.format_content("中文English") == "中文 English"
        assert fmt.format_content("English中文") == "English 中文"
        assert fmt.format_content("中文123English") == "中文 123 English"

    def test_content_spacing_fix_basic(self) -> None:
        """测试内容空格修复基本功能。"""
        fmt = MarkdownFormatter()
        # 正向空格添加
        assert fmt.content_spacing_fix("中文English") == "中文 English"
        assert fmt.content_spacing_fix("English中文") == "English 中文"
        assert fmt.content_spacing_fix("中文123English") == "中文 123 English"

    def test_format_line_basic(self) -> None:
        """测试单行格式化基本功能。"""
        fmt = MarkdownFormatter()
        # 普通文本行
        assert fmt._format_line("中文English") == "中文 English"
        # 标题行
        assert fmt._format_line("# 标题") == "# 标题"
        # 列表行
        assert fmt._format_line("- 列表项") == "- 列表项"

    def test_protected_content(self) -> None:
        """测试特殊内容保护。"""
        fmt = MarkdownFormatter()
        # 代码块保护
        code_block = "```\nprint('Hello World')\n```"
        assert fmt.format_content(code_block) == code_block
        # 行内代码保护
        inline_code = "`print('Hello')`"
        assert fmt.format_content(inline_code) == inline_code

    def test_patterns_compilation(self) -> None:
        """测试正则表达式模式编译。"""
        patterns = MarkdownFormatter._get_patterns()
        assert isinstance(patterns, dict)
        assert "chinese_english" in patterns
        assert "english_chinese" in patterns
        assert "chinese_number" in patterns
        assert "number_chinese" in patterns

    def test_cached_patterns(self) -> None:
        """测试正则表达式缓存机制。"""
        # 第一次调用
        patterns1 = MarkdownFormatter._get_patterns()
        # 第二次调用应该返回缓存的模式
        patterns2 = MarkdownFormatter._get_patterns()
        assert patterns1 is patterns2

    def test_empty_content(self) -> None:
        """测试空内容处理。"""
        fmt = MarkdownFormatter()
        assert fmt.format_content("") == ""
        assert fmt.format_content("\n\n") == "\n\n"
        assert fmt.content_spacing_fix("") == ""

    def test_whitespace_only_content(self) -> None:
        """测试纯空白内容处理。"""
        fmt = MarkdownFormatter()
        # 多空格会被合并为单空格
        assert fmt.format_content("   ") == " "
        assert fmt.format_content("\t\n") == "\t\n"
        assert fmt.content_spacing_fix("   ") == " "


if __name__ == "__main__":
    pytest.main([__file__])
