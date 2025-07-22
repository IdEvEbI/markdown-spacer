"""
Core formatting algorithm for markdown-spacer.
"""

import logging
import re
from typing import Dict, List, Optional, Pattern


class MarkdownFormatter:
    """Core formatter for handling spacing in Markdown content."""

    def __init__(
        self,
        bold_quotes: bool = False,
        custom_rules: Optional[List[Dict[str, Pattern[str]]]] = None,
        debug: bool = False,
    ) -> None:
        """Initialize the formatter.

        Args:
            bold_quotes: Whether to make Chinese double quotes content bold
            custom_rules: Optional list of custom regex rules to apply.
                Each rule: {"name": str, "pattern": Pattern, "repl": str}
            debug: Whether to enable debug logging
        """
        self.bold_quotes = bold_quotes
        self._patterns = self._create_patterns()
        self._custom_rules = custom_rules or []
        self.debug = debug
        if self.debug:
            logging.basicConfig(level=logging.DEBUG)

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
            # 数字与英文之间添加空格
            "number_english": re.compile(r"(\d)([a-zA-Z])"),
            # 英文与数字之间添加空格
            "english_number": re.compile(r"([a-zA-Z])(\d)"),
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
                r"("  # 支持多种日期格式
                r"\d{4}-\d{1,2}-\d{1,2}"
                r"|\d{1,2}-\d{1,2}"
                r"|\d{1,2}月\d{1,2}[日号]?"
                r"|\d{4}年\d{1,2}月\d{1,2}[日号]?"
                r"|\d{1,2}月\d{1,2}日"
                r"|\d{1,2}月\d{1,2}号"
                r")"
            ),
            # 版本号（保护，不处理），支持英文和中文格式
            "version": re.compile(
                r"v(\d+\.\d+\.\d+|[\u4e00-\u9fa5]+\.[\u4e00-\u9fa5]+\.[\u4e00-\u9fa5]+(-[A-Za-z0-9]+)?)"
            ),
            # 英文连字符（保护，不处理）
            "english_hyphen": re.compile(r"([a-zA-Z]+)-([a-zA-Z]+)"),
            # 中文括号内英文/英文括号内中文（保护，不处理）
            "chinese_paren_english": re.compile(r"（[a-zA-Z]+）"),
            "english_paren_chinese": re.compile(r"[a-zA-Z]+（[\u4e00-\u9fa5]+）"),
            # 英文标点后加空格（逗号、句号、问号、感叹号、分号、冒号）
            "en_punct_after": re.compile(r"([,\.!?;:])([A-Za-z\u4e00-\u9fa5])"),
            # 英文右括号后加空格
            "en_rparen_after": re.compile(r"(\))([A-Za-z\u4e00-\u9fa5])"),
            # 中文与 v 之间加空格（用于版本号前缀，v 后可跟数字或中文）
            "chinese_v": re.compile(r"([\u4e00-\u9fa5])([vV])(?=[\d\u4e00-\u9fa5]+\.)"),
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
        """Format a single line of content.

        Args:
            line: The line to format

        Returns:
            Formatted line
        """
        if self._is_protected_content(line):
            if self.debug:
                logging.debug(f"跳过单行特殊内容: {line}")
            return line

        formatted = line
        placeholders = {}
        placeholder_types = {}  # 新增：记录占位符类型
        placeholder_idx = 0

        # 0. 先处理中文+v之间加空格（用于版本号前缀）
        formatted = self._patterns["chinese_v"].sub(r"\1 \2", formatted)

        # 1. 先保护括号内容（括号内英文/括号内中文）
        paren_patterns = [
            self._patterns["chinese_paren_english"],
            self._patterns["english_paren_chinese"],
        ]
        for pattern in paren_patterns:

            def _paren_repl(m: re.Match[str]) -> str:
                nonlocal placeholder_idx
                key = f"__PROTECT_{placeholder_idx}__"
                placeholders[key] = m.group(0)
                placeholder_types[key] = "paren"
                placeholder_idx += 1
                if self.debug:
                    logging.debug(f"占位括号内容: {m.group(0)} -> {key}")
                return key

            formatted = pattern.sub(_paren_repl, formatted)

        # 2. 再保护日期、版本号、英文连字符
        protect_patterns = [
            self._patterns["date"],
            self._patterns["version"],
            self._patterns["english_hyphen"],
        ]
        for i, pattern in enumerate(protect_patterns):

            def _repl(m: re.Match[str], t: int = i) -> str:
                nonlocal placeholder_idx
                key = f"__PROTECT_{placeholder_idx}__"
                placeholders[key] = m.group(0)
                # 只对日期类型做特殊标记
                if t == 0:
                    placeholder_types[key] = "date"
                else:
                    placeholder_types[key] = "other"
                placeholder_idx += 1
                if self.debug:
                    logging.debug(f"占位保护内容: {m.group(0)} -> {key}")
                return key

            formatted = pattern.sub(_repl, formatted)

        # 3. 处理中文+日期占位符之间的空格（仅针对日期占位符，且后面不是中文时）
        def add_space_chinese_date(m: re.Match[str]) -> str:
            key = m.group(2)
            if placeholder_types.get(key) == "date":
                return m.group(1) + " " + key
            return m.group(1) + key

        formatted = re.sub(
            r"([\u4e00-\u9fa5])(__PROTECT_\d+__)(?![\u4e00-\u9fa5])",
            add_space_chinese_date,
            formatted,
        )

        # 3.1 处理日期占位符+中文之间的空格（日期类型加空格，其他类型不加空格）
        def space_date_chinese(m: re.Match[str]) -> str:
            key = m.group(1)
            if placeholder_types.get(key) == "date":
                return key + " " + m.group(2)
            return key + m.group(2)

        formatted = re.sub(
            r"(__PROTECT_\d+__)([\u4e00-\u9fa5])", space_date_chinese, formatted
        )

        # 3.2 处理中文+括号占位符时强制不加空格
        def no_space_chinese_paren(m: re.Match[str]) -> str:
            key = m.group(2)
            if placeholder_types.get(key) == "paren":
                return m.group(1) + key
            return m.group(1) + " " + key

        formatted = re.sub(
            r"([\u4e00-\u9fa5])(__PROTECT_\d+__)", no_space_chinese_paren, formatted
        )

        # 4. 应用空格处理规则（不影响已被保护的内容）
        formatted = self._patterns["chinese_english"].sub(r"\1 \2", formatted)
        formatted = self._patterns["english_chinese"].sub(r"\1 \2", formatted)
        formatted = self._patterns["chinese_number"].sub(r"\1 \2", formatted)
        formatted = self._patterns["number_chinese"].sub(r"\1 \2", formatted)
        formatted = self._patterns["number_english"].sub(r"\1 \2", formatted)
        formatted = self._patterns["english_number"].sub(r"\1 \2", formatted)
        formatted = self._patterns["math_symbols"].sub(r"\1 \2 \3", formatted)
        # 英文标点后加空格
        formatted = self._patterns["en_punct_after"].sub(r"\1 \2", formatted)
        # 英文右括号后加空格
        formatted = self._patterns["en_rparen_after"].sub(r"\1 \2", formatted)
        if self.bold_quotes:
            formatted = self._patterns["chinese_quotes"].sub(r"**\1**", formatted)
        formatted = self._patterns["chinese_hyphen"].sub(r"\1 - \2", formatted)
        # 4.5 应用自定义扩展规则（如有）
        for rule in self._custom_rules:
            pattern = rule["pattern"]
            repl = rule["repl"]
            if isinstance(pattern, re.Pattern) and isinstance(repl, str):
                if self.debug:
                    logging.debug(f"应用自定义规则: {rule.get('name', pattern)}")
                formatted = pattern.sub(repl, formatted)

        # 5. 还原所有保护性内容
        for key, value in placeholders.items():
            if self.debug:
                logging.debug(f"还原保护内容: {key} -> {value}")
            formatted = formatted.replace(key, value)

        # 6. 版本号后紧跟中英文时加空格
        formatted = re.sub(
            r"(v\d+\.\d+\.\d+)([A-Za-z\u4e00-\u9fa5])", r"\1 \2", formatted
        )
        formatted = re.sub(
            r"(v[\u4e00-\u9fa5]+\.[\u4e00-\u9fa5]+\.[\u4e00-\u9fa5]+)(?![\u4e00-\u9fa5])([A-Za-z0-9])",
            r"\1 \2",
            formatted,
        )

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
        return False
