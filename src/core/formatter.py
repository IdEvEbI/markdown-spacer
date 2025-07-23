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
        self._patterns = self._create_patterns()
        self._custom_rules = custom_rules or []
        self.debug = debug
        if self.debug:
            logging.basicConfig(level=logging.DEBUG)

    def _create_patterns(self) -> Dict[str, re.Pattern]:
        """创建格式化规则的正则表达式模式。

        Returns:
            编译好的正则表达式模式字典
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
                r"v(\d+\.\d+\.\d+|[\u4e00-\u9fa5]+\.[\u4e00-\u9fa5]+\.[\u4e00-\u9fa5]+"
                r"(-[A-Za-z0-9]+)?)"
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

            def _bold_quotes_with_space(m: re.Match[str]) -> str:
                content = m.group(1)
                # 如果内容中还有“或”，则认为是嵌套，直接返回原文
                if "“" in content or "”" in content:
                    return m.group(0)
                start, end = m.start(), m.end()
                before = formatted[start - 1] if start > 0 else ""
                after = formatted[end] if end < len(formatted) else ""
                bold = f"**{content}**"
                need_space_before = before and re.match(r"[\w\u4e00-\u9fa5]", before)
                need_space_after = after and re.match(r"[\w\u4e00-\u9fa5]", after)
                return (
                    (" " if need_space_before else "")
                    + bold
                    + (" " if need_space_after else "")
                )

            formatted = self._patterns["chinese_quotes"].sub(
                _bold_quotes_with_space, formatted
            )
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
            r"(v[\u4e00-\u9fa5]+\.[\u4e00-\u9fa5]+\.[\u4e00-\u9fa5]+)"
            r"(?![\u4e00-\u9fa5])([A-Za-z0-9])",
            r"\1 \2",
            formatted,
        )

        return formatted

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
