"""
Core formatting algorithm for markdown-spacer.
"""

import re
from typing import Dict


class MarkdownFormatter:
    """Core formatter for handling spacing in Markdown content."""

    def __init__(self, bold_quotes: bool = False) -> None:
        """Initialize the formatter.

        Args:
            bold_quotes: Whether to make Chinese double quotes content bold
        """
        self.bold_quotes = bold_quotes
        self._patterns = self._create_patterns()

    def _create_patterns(self) -> Dict[str, re.Pattern]:
        """Create regex patterns for formatting rules.

        Returns:
            Dictionary of compiled regex patterns
        """
        return {
            # 中文与英文之间添加空格
            "chinese_english": re.compile(r"([\u4e00-\u9fa5])([a-zA-Z])"),
            # 英文与中文之间添加空格
            "english_chinese": re.compile(r"([a-zA-Z])([\u4e00-\u9fa5])"),
            # 中文与数字之间添加空格
            "chinese_number": re.compile(r"([\u4e00-\u9fa5])(\d)"),
            # 数字与中文之间添加空格
            "number_chinese": re.compile(r"(\d)([\u4e00-\u9fa5])"),
            # 数学符号连接，A+B -> A + B，张三-李四 -> 张三 - 李四
            "math_symbols": re.compile(
                r"([\u4e00-\u9fa5a-zA-Z0-9])([+\-/*=<>])([\u4e00-\u9fa5a-zA-Z0-9])"
            ),
            # 中文双引号内容（可选加粗）
            "chinese_quotes": re.compile(r"“(.+?)”"),
            # 中文连字符，张三-李四 -> 张三 - 李四
            "chinese_hyphen": re.compile(r"([\u4e00-\u9fa5]+)-([\u4e00-\u9fa5]+)"),
            # 日期（保护，不处理）
            "date": re.compile(
                r"(\d{4}-\d{1,2}-\d{1,2}|\d{1,2}-\d{1,2}|\d{1,2}月\d{1,2}[日号]?|\d{4}年\d{1,2}月\d{1,2}[日号]?)"
            ),
            # 版本号（保护，不处理）
            "version": re.compile(r"v\d+\.\d+\.\d+"),
            # 英文连字符（保护，不处理）
            "english_hyphen": re.compile(r"([a-zA-Z]+)-([a-zA-Z]+)"),
            # 中文括号内英文/英文括号内中文（保护，不处理）
            "chinese_paren_english": re.compile(r"（[a-zA-Z]+）"),
            "english_paren_chinese": re.compile(r"[a-zA-Z]+（[\u4e00-\u9fa5]+）"),
        }

    def format_content(self, content: str) -> str:
        """Format the content by adding appropriate spacing.

        Args:
            content: The content to format

        Returns:
            Formatted content
        """
        lines = content.split("\n")
        formatted_lines = []
        in_code_block = False
        for line in lines:
            # 检查多行代码块
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                formatted_lines.append(line)
                continue
            # 跳过代码块、表格、列表等特殊内容
            if in_code_block or self._is_protected_content(line):
                formatted_lines.append(line)
                continue
            formatted_lines.append(self._format_line(line))
        return "\n".join(formatted_lines)

    def _format_line(self, line: str) -> str:
        """Format a single line of content.

        Args:
            line: The line to format

        Returns:
            Formatted line
        """
        if self._is_protected_content(line):
            return line

        formatted = line

        # Apply spacing rules
        formatted = self._patterns["chinese_english"].sub(r"\1 \2", formatted)
        formatted = self._patterns["english_chinese"].sub(r"\1 \2", formatted)
        formatted = self._patterns["chinese_number"].sub(r"\1 \2", formatted)
        formatted = self._patterns["number_chinese"].sub(r"\1 \2", formatted)

        # Math symbols
        formatted = self._patterns["math_symbols"].sub(r"\1 \2 \3", formatted)

        # Chinese quotes (optional bold)
        if self.bold_quotes:
            formatted = self._patterns["chinese_quotes"].sub(r"**\1**", formatted)

        # Chinese hyphens
        formatted = self._patterns["chinese_hyphen"].sub(r"\1 - \2", formatted)

        return formatted

    def _is_protected_content(self, line: str) -> bool:
        """Check if line contains protected content that should not be formatted.

        Args:
            line: The line to check

        Returns:
            True if line contains protected content
        """
        # 行内代码
        if line.strip().startswith("`"):
            return True
        # HTML tags
        if re.search(r"<[^>]+>", line):
            return True
        # 链接和图片
        if re.search(r"\[.*\]\(.*\)", line) or re.search(r"!\[.*\]\(.*\)", line):
            return True
        # 数学公式
        if re.search(r"\$\$.*\$\$", line) or re.search(r"\$.*\$", line):
            return True
        # 表格（以 | 分隔）
        if "|" in line:
            return True
        # 引用块
        if line.strip().startswith(">"):
            return True
        # 列表项
        if line.strip().startswith(("- ", "* ", "+ ")):
            return True
        # 标题行
        if line.strip().startswith("#"):
            return True
        return False
