"""
markdown-spacer 核心格式化算法模块。

本模块实现了 Markdown 文档中英文、数字间空格处理的核心算法，
包括正则表达式规则定义、内容格式化处理、特殊内容保护等功能。
"""

import logging
import re
from typing import Dict, List, Optional, Pattern


class MarkdownFormatter:
    """Markdown 内容空格处理核心格式化器。

    负责处理 Markdown 文档中中文、英文、数字之间的空格问题，
    支持特殊内容保护、自定义规则扩展等功能。

    Attributes:
        bold_quotes: 是否将中文双引号内容加粗
        _patterns: 编译好的正则表达式模式字典
        _custom_rules: 自定义正则表达式规则列表
        debug: 是否启用调试日志
    """

    # 类级别的正则表达式缓存，避免重复编译
    _cached_patterns: Optional[Dict[str, re.Pattern]] = None

    def __init__(
        self,
        bold_quotes: bool = False,
        custom_rules: Optional[List[Dict[str, Pattern[str]]]] = None,
        debug: bool = False,
    ) -> None:
        """初始化格式化器。

        Args:
            bold_quotes: 是否将中文双引号内容加粗
            custom_rules: 可选的自定义正则表达式规则列表。
                每个规则格式：{"name": str, "pattern": Pattern, "repl": str}
            debug: 是否启用调试日志
        """
        self.bold_quotes = bold_quotes
        self._patterns = self._get_patterns()
        self._custom_rules = custom_rules or []
        self.debug = debug
        if self.debug:
            logging.basicConfig(level=logging.DEBUG)

    @classmethod
    def _get_patterns(cls) -> Dict[str, re.Pattern]:
        """获取编译好的正则表达式模式，使用类级别缓存。

        Returns:
            编译好的正则表达式模式字典
        """
        if cls._cached_patterns is None:
            cls._cached_patterns = cls._create_patterns()
        return cls._cached_patterns

    @classmethod
    def _create_patterns(cls) -> Dict[str, re.Pattern]:
        """创建格式化规则的正则表达式模式。

        Returns:
            编译好的正则表达式模式字典
        """
        return {
            # 基础空格处理规则（待实现）
            "chinese_english": re.compile(r"([\u4e00-\u9fa5])([a-zA-Z])"),
            "english_chinese": re.compile(r"([a-zA-Z])([\u4e00-\u9fa5])"),
            "chinese_number": re.compile(r"([\u4e00-\u9fa5])(\d)"),
            "number_chinese": re.compile(r"(\d)([\u4e00-\u9fa5])"),
            "number_english": re.compile(r"(\d)([a-zA-Z])"),
            "english_number": re.compile(r"([a-zA-Z])(\d)"),
        }

    def format_content(self, content: str) -> str:
        """格式化内容，添加适当的空格。

        Args:
            content: 要格式化的内容

        Returns:
            格式化后的内容
        """
        lines = content.split("\n")
        formatted_lines = []
        in_code_block = False
        in_math_block = False

        for idx, line in enumerate(lines):
            # 检查多行代码块
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                if self.debug:
                    logging.debug(
                        f"Line {idx}: {'进入' if in_code_block else '退出'}代码块 -> {line}"
                    )
                formatted_lines.append(line)
                continue

            # 检查多行数学公式块
            if line.strip().startswith("$$"):
                in_math_block = not in_math_block
                if self.debug:
                    logging.debug(
                        f"Line {idx}: {'进入' if in_math_block else '退出'}数学公式块 -> {line}"
                    )
                formatted_lines.append(line)
                continue

            # 跳过所有多行保护块
            if in_code_block or in_math_block or self._is_protected_content(line):
                if self.debug:
                    logging.debug(f"Line {idx}: 跳过特殊内容 -> {line}")
                formatted_lines.append(line)
                continue

            formatted_lines.append(self._format_line(line))

        return "\n".join(formatted_lines)

    def _format_line(self, line: str) -> str:
        """格式化单行内容。

        Args:
            line: 要格式化的行

        Returns:
            格式化后的行
        """
        # 跳过块级代码和行内代码
        if line.strip().startswith("```") or line.strip().startswith("`"):
            return line

        # 结构类型检测
        is_table = bool(re.match(r"^\|.*\|$", line.strip()))
        is_list = bool(re.match(r"^\s*([-*+]|\d+\.)\s*", line))
        is_title = bool(re.match(r"^#+\s*", line))
        is_quote = bool(re.match(r"^>\s*", line))

        # 表格分隔线严格输出 | ---- | ---- |
        if is_table and re.match(r"^\|[\s\-\|]+\|$", line.strip()):
            parts = [p for p in line.strip().split("|")[1:-1]]
            new_parts = ["----" for _ in parts]
            return "| " + " | ".join(new_parts) + " |"

        # 表格内容行，按 | 分割，内容块修复
        if is_table:
            cells = line.strip().split("|")
            new_cells = []
            for cell in cells:
                cell_strip = cell.strip()
                if cell_strip:
                    cell_strip = self.content_spacing_fix(cell_strip)
                new_cells.append(" " + cell_strip + " " if cell_strip else "")
            return "|".join(new_cells)

        # 标题、列表、引用，分离前缀和正文，正文修复
        if is_title:
            m = re.match(r"^(#+\s*)(.*)$", line)
            if m:
                prefix, content = m.group(1), m.group(2)
                return (
                    prefix.rstrip() + " " + self.content_spacing_fix(content.lstrip())
                )

        if is_list:
            m = re.match(r"^(\s*([-*+]|\d+\.)\s*)(.*)$", line)
            if m:
                prefix, content = m.group(1), m.group(3)
                return (
                    prefix.rstrip() + " " + self.content_spacing_fix(content.lstrip())
                )

        if is_quote:
            m = re.match(r"^(>\s*)(.*)$", line)
            if m:
                prefix, content = m.group(1), m.group(2)
                return (
                    prefix.rstrip() + " " + self.content_spacing_fix(content.lstrip())
                )

        # 普通正文行
        return self.content_spacing_fix(line)

    def content_spacing_fix(self, text: str) -> str:
        """内容块空格修复（基础实现）。

        Args:
            text: 要修复的文本

        Returns:
            修复后的文本
        """
        # 基础空格处理（待完善）
        text = self._patterns["chinese_english"].sub(r"\1 \2", text)
        text = self._patterns["english_chinese"].sub(r"\1 \2", text)
        text = self._patterns["chinese_number"].sub(r"\1 \2", text)
        text = self._patterns["number_chinese"].sub(r"\1 \2", text)
        text = self._patterns["number_english"].sub(r"\1 \2", text)
        text = self._patterns["english_number"].sub(r"\1 \2", text)

        # 合并多个连续空格
        text = re.sub(r" +", " ", text)

        return text

    def _is_protected_content(self, line: str) -> bool:
        """检查行是否包含不应格式化的保护内容。

        Args:
            line: 要检查的行

        Returns:
            如果行包含保护内容则返回 True
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
        return False
