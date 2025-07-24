"""
markdown-spacer 核心格式化算法模块。

本模块实现了 Markdown 文档中英文、数字间空格处理的核心算法，
包括正则表达式规则定义、内容格式化处理、特殊内容保护等功能。
"""

import logging
import re
from typing import Dict, List, Optional, Pattern

from src.utils.logger import get_logger


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

        # 设置logger
        self.logger = get_logger("formatter")
        if self.debug:
            self.logger.setLevel(logging.DEBUG)

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
            # 基础空格处理规则 - 合并优化
            "basic_spacing": re.compile(
                r"([\u4e00-\u9fa5])([a-zA-Z])|([a-zA-Z])([\u4e00-\u9fa5])|"
                r"([\u4e00-\u9fa5])(\d)|(\d)([\u4e00-\u9fa5])|"
                r"(\d)([a-zA-Z])(?!\s*[>=<≤≥＝≠])|([a-zA-Z])(\d)"
            ),
            # 数学符号空格处理规则
            "math_symbols": re.compile(
                r"([\u4e00-\u9fa5a-zA-Z0-9])([+/*=<>])([\u4e00-\u9fa5a-zA-Z0-9])"
            ),
            # 减号符号空格处理规则（排除版本号中的连字符）
            "minus_symbol": re.compile(
                r"([\u4e00-\u9fa5a-zA-Z0-9])(-)([\u4e00-\u9fa5a-zA-Z0-9])(?!\d)(?!\w*-)"
            ),
            # 英文标点后空格处理规则（排除文件扩展名中的点号）
            "punctuation_after": re.compile(
                r"([,\.!?;:])([A-Za-z\u4e00-\u9fa5])(?!\w*\.\w+)"
            ),
            "rparen_after": re.compile(r"(\))([A-Za-z\u4e00-\u9fa5])"),
            # 中文斜杠分隔空格处理规则
            "chinese_slash": re.compile(
                r"([\u4e00-\u9fa5])\s*/\s*([\u4e00-\u9fa5a-zA-Z])"
            ),
            # 编号与中文空格处理规则
            "number_chinese_priority": re.compile(r"([\u4e00-\u9fa5])(\d+)"),
            # 技术术语修复规则
            "version_number": re.compile(r"v (\d+(?:\.\d+)+(?:-[a-zA-Z0-9]+)?)"),
            "tech_abbr": re.compile(r"([A-Z]{2,}) - ([A-Z0-9]+)"),
            "tech_abbr_multi": re.compile(r"([A-Z]{2,}) - ([A-Z0-9]+) - ([A-Z09]+)"),
            "tool_name": re.compile(r"(flake) (8)"),
            # 数字与单位修复规则
            "number_unit": re.compile(
                r"(\d+) (MB|GB|KB|TB|B|℃|°C|°F|%|km|cm|mm|m|kg|g|mg|s|ms|h|d|"
                r"px|em|rem|pt)"
            ),
            "number_unit_plus": re.compile(r"(\d+)(MB|GB|KB|TB|B)\s*\+"),
            # 英文连字符修复规则
            "english_hyphen": re.compile(r"([a-zA-Z0-9]+) - ([a-zA-Z0-9]+)"),
            # 文件路径修复规则
            "file_extension": re.compile(r"(\w+) \. ([a-zA-Z0-9]+)"),
            "path_separator": re.compile(
                r"(?<=\w)\s*/\s*(?=\w)(?=.*\.\w+)(?!.*[\u4e00-\u9fa5])"
            ),
            "path_file_extension": re.compile(r"([\w\-/]+)\s+\.\s+([a-zA-Z0-9]+)"),
            # 比较符号修复规则
            "comparison_symbols": re.compile(
                r"(>=|<=|!=|==|>|<|＞|＜|≥|≤|＝|≠)\s*([0-9])"
            ),
            # 比较符号修复规则（处理已经被基础空格处理的情况）
            "comparison_symbols_fix": re.compile(
                r"(>=|<=|!=|==|>|<|＞|＜|≥|≤|＝|≠)\s+([0-9]+)\s+([A-Za-z]+)"
            ),
            "filename_protection": re.compile(
                r"([\w\-]+\.(txt|py|toml|yaml|yml|json|md|markdown))"
            ),
            # 日期格式修复规则
            "date_format": re.compile(r"(\d{4}) 年 (\d{1,2}) 月 (\d{1,2}) 日"),
            "date_format_short": re.compile(r"(\d{1,2}) 月 (\d{1,2}) 日"),
            # 中文双引号加粗规则
            "chinese_quotes_bold": re.compile(r'"([^"]*)"'),
            # 多空格合并规则
            "multiple_spaces": re.compile(r" +"),
        }

    def format_content(self, content: str) -> str:
        """格式化内容，添加适当的空格。"""
        # 1. 批量保护特殊内容
        protected_content: Dict[str, str] = {}
        content = self._protect_special_content(content, protected_content)
        # 2. 按行处理，收集到列表
        lines = content.splitlines(keepends=True)
        processed_lines = [self._format_line(line) for line in lines]
        content = "".join(processed_lines)
        # 3. 业务规则修复
        content = self._apply_business_rules(content)
        # 4. 中文双引号加粗（可选）
        if self.bold_quotes:
            content = self._fix_chinese_quotes_bold(content)
        # 5. 批量还原特殊内容
        content = self._restore_special_content(content, protected_content)
        return content

    def _format_line(self, line: str) -> str:
        """格式化单行内容，分离结构标记与内容块，对内容块递归做 spacing。"""
        # 标题行
        if self._is_title_line(line):
            prefix, content = self._extract_title_content(line)
            return prefix + self.content_spacing_fix(content)
        # 列表行（无序/有序/缩进）
        if self._is_list_line(line):
            prefix, content = self._extract_list_content(line)
            return prefix + self.content_spacing_fix(content)
        # 引用行
        if self._is_quote_line(line):
            prefix, content = self._extract_quote_content(line)
            return prefix + self.content_spacing_fix(content)
        # 表格行
        if self._is_table_line(line):
            # 检查是否为表格分隔行（如 | --- | --- |）
            if re.match(
                r"^\s*\|?\s*:?[-]+:?(\|\s*:?[-]+:?\s*)+\|?\s*$",
                line,
            ):
                return line  # 分隔线保持原样
            # 普通表格行，保留 | 分隔和前后空格，仅处理单元格内容
            raw_cells = re.split(r"(\|)", line)
            processed = []
            for cell in raw_cells:
                if cell == "|":
                    processed.append(cell)
                else:
                    # 保留原有前后空格，仅对内容做 spacing
                    leading = len(cell) - len(cell.lstrip(" "))
                    trailing = len(cell) - len(cell.rstrip(" "))
                    content = cell.strip(" ")
                    if content:
                        content = self.content_spacing_fix(content)
                    processed.append(" " * leading + content + " " * trailing)
            return "".join(processed)
        # 代码块、数学块、水平线等特殊结构直接返回
        if (
            self._is_code_block_line(line)
            or self._is_math_block_line(line)
            or self._is_horizontal_rule_line(line)
        ):
            return line
        # 普通行
        return self.content_spacing_fix(line)

    def content_spacing_fix(self, text: str) -> str:
        """内容块空格修复（基础实现）。"""
        # 文件名格式保护（如 requirements.txt、setup.py、pyproject.toml 等）
        protected_filenames: dict[str, str] = {}

        def protect_filename(m: re.Match[str]) -> str:
            key = f"__FILENAME_{len(protected_filenames)}__"
            protected_filenames[key] = m.group(0)
            return key

        text = re.sub(
            r"\b\w+\.(txt|py|toml|yaml|yml|json|md|markdown)\b", protect_filename, text
        )

        # 基础空格处理（分步 re.sub）
        text = re.sub(r"([\u4e00-\u9fa5])([a-zA-Z])", r"\1 \2", text)  # zh_en
        text = re.sub(r"([a-zA-Z])([\u4e00-\u9fa5])", r"\1 \2", text)  # en_zh
        text = re.sub(r"([\u4e00-\u9fa5])(\d)", r"\1 \2", text)  # zh_num
        text = re.sub(r"(\d)([\u4e00-\u9fa5])", r"\1 \2", text)  # num_zh
        text = re.sub(r"([a-zA-Z])(\d)", r"\1 \2", text)  # en_num
        text = re.sub(r"(\d)([a-zA-Z])", r"\1 \2", text)  # num_en

        # 数学符号空格处理
        if any(char in text for char in "+/*=<>"):
            text = self._patterns["math_symbols"].sub(r"\1 \2 \3", text)
        # 减号符号空格处理
        if "-" in text:
            text = self._patterns["minus_symbol"].sub(r"\1 \2 \3", text)
        # 标点符号空格处理
        if any(char in text for char in ",.!?;:"):
            text = self._patterns["punctuation_after"].sub(r"\1 \2", text)
        if ")" in text:
            text = self._patterns["rparen_after"].sub(r"\1 \2", text)
        # 中文斜杠分隔空格处理
        if "/" in text:
            text = self._patterns["chinese_slash"].sub(r"\1 / \2", text)
        # 编号与中文空格处理
        if any(char.isdigit() for char in text):
            text = self._patterns["number_chinese_priority"].sub(r"\1 \2", text)
        # 合并多个连续空格
        if " " in text:
            text = self._patterns["multiple_spaces"].sub(" ", text)
        # 业务规则修复
        text = self._apply_business_rules(text)
        # 恢复文件名格式
        for key, val in protected_filenames.items():
            text = text.replace(key, val)
        # 中文双引号加粗（可选）
        if getattr(self, "bold_quotes", False):
            text = self._fix_chinese_quotes_bold(text)
        return text

    def _apply_business_rules(self, text: str) -> str:
        """应用业务规则修复（删除不应该存在的空格）。

        Args:
            text: 要修复的文本

        Returns:
            修复后的文本
        """
        # 比较符号修复
        text = self._fix_comparison_symbols(text)

        # 技术术语修复
        text = self._fix_technical_terms(text)

        # 日期格式修复
        text = self._fix_date_format(text)

        # 文件路径修复（最后执行，避免影响其他规则）
        text = self._fix_file_paths(text)

        return text

    def _fix_technical_terms(self, text: str) -> str:
        """修复技术术语中的空格问题。

        Args:
            text: 要修复的文本

        Returns:
            修复后的文本
        """
        # 版本号修复：v 1.2.3 -> v1.2.3, v 2.0.0-beta -> v2.0.0-beta
        text = re.sub(r"v (\d+(?:\.\d+)+(?:-[a-zA-Z0-9]+)?)", r"v\1", text)

        # 版本号连字符修复：v2.0.0 - beta -> v2.0.0-beta
        text = re.sub(r"v(\d+(?:\.\d+)+) - ([a-zA-Z0-9]+)", r"v\1-\2", text)

        # 技术缩写修复（多个连字符）：ISO - 8859 - 1 -> ISO-8859-1
        text = self._patterns["tech_abbr_multi"].sub(r"\1-\2-\3", text)

        # 技术缩写修复（单个连字符）：UTF - 8 -> UTF-8
        text = self._patterns["tech_abbr"].sub(r"\1-\2", text)

        # 工具名修复：flake 8 -> flake8
        text = self._patterns["tool_name"].sub(r"\1\2", text)

        # 数字与单位修复
        text = self._patterns["number_unit"].sub(r"\1\2", text)
        text = self._patterns["number_unit_plus"].sub(r"\1\2+", text)

        # 英文连字符修复
        text = self._patterns["english_hyphen"].sub(r"\1-\2", text)

        # 只移除工具名末尾的空格，如 "black " -> "black"
        # 但不影响其他情况下的末尾空格
        # 使用更精确的匹配，只匹配单词后跟空格结尾的情况
        text = re.sub(r"([a-zA-Z0-9]+) $", r"\1", text)

        return text

    def _fix_file_paths(self, text: str) -> str:
        """修复文件路径中的空格问题。

        Args:
            text: 要修复的文本

        Returns:
            修复后的文本
        """
        # 文件扩展名修复：requirements . txt -> requirements.txt
        text = self._patterns["file_extension"].sub(r"\1.\2", text)

        # 路径关键词列表（用于识别路径）
        path_keywords = [
            "src",
            "docs",
            "config",
            "bin",
            "usr",
            "local",
            "home",
            "etc",
            "var",
            "tmp",
            "core",
            "utils",
            "helpers",
        ]

        # 检查是否包含路径特征
        has_path_features = (
            re.search(r"\.\s*\w+", text)  # 包含文件扩展名
            or any(keyword in text for keyword in path_keywords)  # 包含路径关键词
            or re.search(r"[A-Z]:\s*\\", text)  # Windows路径
        )

        if has_path_features:
            # Unix/Linux路径修复：处理斜杠分隔符
            # 匹配：任意字符 + 空格 + / + 空格 + 任意字符
            text = re.sub(r"([^\s])\s*/\s*([^\s])", r"\1/\2", text)

            # Windows路径修复：处理反斜杠分隔符
            # 匹配：盘符 + 空格 + \ + 空格 + 任意字符
            text = re.sub(r"([A-Z]:)\s*\\\s*([^\s])", r"\1\\\2", text)
            text = re.sub(r"([^\s])\s*\\\s*([^\s])", r"\1\\\2", text)

        # 路径中的文件扩展名修复：src/core/formatter. py -> src/core/formatter.py
        text = self._patterns["path_file_extension"].sub(r"\1.\2", text)

        # 兜底处理：修复文件路径中点号后的空格 . py -> .py
        if "/" in text or "\\" in text:
            text = re.sub(r"\.\s+([a-zA-Z0-9]+)", r".\1", text)

        return text

    def _fix_comparison_symbols(self, text: str) -> str:
        """修复比较符号中的空格问题。

        Args:
            text: 要修复的文本

        Returns:
            修复后的文本
        """
        # 比较符号修复：>=100 -> >= 100, <=50 -> <= 50, !=30 -> != 30
        text = self._patterns["comparison_symbols"].sub(r"\1 \2", text)
        # 比较符号修复（处理已经被基础空格处理的情况）：>= 100 GB -> >= 100GB
        text = self._patterns["comparison_symbols_fix"].sub(r"\1 \2\3", text)
        return text

    def _fix_date_format(self, text: str) -> str:
        """修复日期格式中的空格问题。

        Args:
            text: 要修复的文本

        Returns:
            修复后的文本
        """
        # 年份格式修复：2025 年 7 月 24 日 -> 2025年7月24日
        text = self._patterns["date_format"].sub(r"\1年\2月\3日", text)
        # 短日期格式修复：7 月 22 日 -> 7月22日
        text = self._patterns["date_format_short"].sub(r"\1月\2日", text)
        return text

    def _fix_chinese_quotes_bold(self, text: str) -> str:
        """
        只加粗最外层的中文双引号内容：
        - 成对出现的“内容”加粗为 **内容**，并在加粗内容前后智能补空格
        - 遇到嵌套结构（如“外层“内层”内容”）整段跳过不处理
        - 内容为空、全空白、特殊字符等不加粗
        """
        # 检查是否有嵌套结构，若有则直接返回原文
        stack = 0
        for c in text:
            if c == "“":
                stack += 1
                if stack > 1:
                    return text  # 嵌套，跳过
            elif c == "”":
                stack -= 1

        # 匹配所有并列的“内容”
        def repl(match: re.Match[str]) -> str:
            content = match.group(1)
            # 跳过内容为空、全空白、全标点等
            if not content.strip():
                return f"“{content}”"
            # 判断前后是否需要补空格
            start, end = match.start(), match.end()
            prefix_space = (
                start > 0
                and not text[start - 1].isspace()
                and text[start - 1] not in "，。！？；："
            )
            suffix_space = (
                end < len(text)
                and not text[end].isspace()
                and text[end] not in "，。！？；："
            )
            bold = f"**{content}**"
            if prefix_space:
                bold = " " + bold
            if suffix_space:
                bold = bold + " "
            return bold

        # 只处理最外层并列的“内容”
        return re.sub(r"“([^“”]+)”", repl, text)

    def _protect_special_content(self, text: str, protected_content: dict) -> str:
        """保护特殊内容，用占位符替换。

        Args:
            text: 要处理的文本
            protected_content: 存储被保护内容的字典

        Returns:
            替换后的文本
        """
        # 保护数学公式：$...$ 和 $$...$$
        text = self._protect_math_formulas(text, protected_content)

        # 保护行内代码：`...`
        text = self._protect_inline_code(text, protected_content)

        # 保护链接：[text](url)
        text = self._protect_links(text, protected_content)

        # 保护图片：![alt](url)
        text = self._protect_images(text, protected_content)

        # 保护HTML标签：<...>
        text = self._protect_html_tags(text, protected_content)

        # 保护文件名：requirements.txt, setup.py 等
        text = self._protect_filenames(text, protected_content)

        return text

    def _restore_special_content(self, text: str, protected_content: dict) -> str:
        """恢复特殊内容，将占位符替换回原内容。

        Args:
            text: 处理后的文本
            protected_content: 存储被保护内容的字典

        Returns:
            恢复后的文本
        """
        # 按占位符ID逆序恢复，避免嵌套问题
        for placeholder_id in sorted(protected_content.keys(), reverse=True):
            original_content = protected_content[placeholder_id]
            text = text.replace(placeholder_id, original_content)

        return text

    def _protect_math_formulas(self, text: str, protected_content: dict) -> str:
        """保护数学公式。

        Args:
            text: 要处理的文本
            protected_content: 存储被保护内容的字典

        Returns:
            替换后的文本
        """
        # 保护块级数学公式：$$...$$
        text = re.sub(
            r"(\$\$[^$]*\$\$)",
            lambda m: self._create_placeholder(m.group(1), protected_content),
            text,
        )

        # 保护行内数学公式：$...$
        text = re.sub(
            r"(\$[^$\n]*\$)",
            lambda m: self._create_placeholder(m.group(1), protected_content),
            text,
        )

        return text

    def _protect_inline_code(self, text: str, protected_content: dict) -> str:
        """保护行内代码。

        Args:
            text: 要处理的文本
            protected_content: 存储被保护内容的字典

        Returns:
            替换后的文本
        """
        # 保护行内代码：`...`
        text = re.sub(
            r"(`[^`]*`)",
            lambda m: self._create_placeholder(m.group(1), protected_content),
            text,
        )

        return text

    def _protect_links(self, text: str, protected_content: dict) -> str:
        """保护链接。

        Args:
            text: 要处理的文本
            protected_content: 存储被保护内容的字典

        Returns:
            替换后的文本
        """
        # 保护链接：[text](url)
        text = re.sub(
            r"(\[[^\]]*\]\([^)]*\))",
            lambda m: self._create_placeholder(m.group(1), protected_content),
            text,
        )

        return text

    def _protect_images(self, text: str, protected_content: dict) -> str:
        """保护图片。

        Args:
            text: 要处理的文本
            protected_content: 存储被保护内容的字典

        Returns:
            替换后的文本
        """
        # 保护图片：![alt](url)
        text = re.sub(
            r"(!\[[^\]]*\]\([^)]*\))",
            lambda m: self._create_placeholder(m.group(1), protected_content),
            text,
        )

        return text

    def _protect_html_tags(self, text: str, protected_content: dict) -> str:
        """保护HTML标签。

        Args:
            text: 要处理的文本
            protected_content: 存储被保护内容的字典

        Returns:
            替换后的文本
        """
        # 保护完整的HTML元素：<tag>content</tag>
        text = re.sub(
            r"(<[^>]*>[^<]*</[^>]*>)",
            lambda m: self._create_placeholder(m.group(1), protected_content),
            text,
        )

        # 保护自闭合HTML标签：<tag />
        text = re.sub(
            r"(<[^>]*/>)",
            lambda m: self._create_placeholder(m.group(1), protected_content),
            text,
        )

        # 保护开始标签：<tag>
        text = re.sub(
            r"(<[^>]*>)",
            lambda m: self._create_placeholder(m.group(1), protected_content),
            text,
        )

        return text

    def _protect_filenames(self, text: str, protected_content: dict) -> str:
        """保护文件名。

        Args:
            text: 要处理的文本
            protected_content: 存储被保护内容的字典

        Returns:
            替换后的文本
        """
        # 保护文件名：requirements.txt, setup.py 等
        text = re.sub(
            r"([\w\-]+\.(txt|py|toml|yaml|yml|json|md|markdown))",
            lambda m: self._create_placeholder(m.group(1), protected_content),
            text,
        )

        return text

    def _create_placeholder(self, content: str, protected_content: dict) -> str:
        """创建占位符并保存原内容。

        Args:
            content: 要保护的内容
            protected_content: 存储被保护内容的字典

        Returns:
            占位符
        """
        placeholder_id = f"__PROTECTED_{len(protected_content)}__"
        protected_content[placeholder_id] = content
        return placeholder_id

    def _is_protected_content(self, line: str) -> bool:
        """检查是否为受保护的内容。

        Args:
            line: 要检查的行

        Returns:
            如果是受保护的内容返回True，否则返回False
        """
        # 检查是否为代码块标记
        if line.strip().startswith("```"):
            return True
        # 检查是否为数学公式块
        if line.strip().startswith("$$"):
            return True
        return False

    # ==================== 行类型识别方法 ====================

    def _is_title_line(self, line: str) -> bool:
        """检查是否为标题行。

        Args:
            line: 要检查的行

        Returns:
            如果是标题行返回True，否则返回False
        """
        stripped = line.strip()
        return stripped.startswith("#") and not stripped.startswith("```")

    def _is_list_line(self, line: str) -> bool:
        """判断是否为列表行，包括所有缩进层级、嵌套、任务列表。"""
        # 支持任意空格缩进+[-*+]/数字.，任务列表
        return bool(re.match(r"^\s*(?:[-*+]|\d+\.)\s*(\[[ xX]\])?\s+", line))

    def _extract_list_content(self, line: str) -> tuple[str, str]:
        """提取所有缩进层级的列表行结构标记和内容。"""
        # 任务列表
        m = re.match(r"^(\s*[-*+]|\d+\.)\s*(\[[ xX]\])?\s+(.*)$", line)
        if m:
            prefix = m.group(1)
            if m.group(2):
                prefix += m.group(2) + " "
            else:
                prefix += " "
            return prefix, m.group(3)
        return "", line

    def _is_quote_line(self, line: str) -> bool:
        """检查是否为引用行。

        Args:
            line: 要检查的行

        Returns:
            如果是引用行返回True，否则返回False
        """
        stripped = line.strip()
        return stripped.startswith(">")

    def _extract_quote_content(self, line: str) -> tuple[str, str]:
        """提取引用行的前缀和内容，支持多级嵌套。"""
        m = re.match(r"^(\s*>+\s*)(.*)$", line)
        if m:
            return m.group(1), m.group(2)
        return "", line

    def _is_table_line(self, line: str) -> bool:
        """检查是否为表格行。

        Args:
            line: 要检查的行

        Returns:
            如果是表格行返回True，否则返回False
        """
        stripped = line.strip()
        # 检查是否包含表格分隔符 |
        if "|" not in stripped:
            return False
        # 检查是否为表格分隔行（包含 ---）
        if re.search(r"\|[\s]*[-:]+\s*\|", stripped):
            return True
        # 检查是否为普通表格行（至少包含两个 |）
        if stripped.count("|") >= 2:
            return True
        return False

    def _is_code_block_line(self, line: str) -> bool:
        """检查是否为代码块标记行。

        Args:
            line: 要检查的行

        Returns:
            如果是代码块标记行返回True，否则返回False
        """
        stripped = line.strip()
        return stripped.startswith("```")

    def _is_math_block_line(self, line: str) -> bool:
        """检查是否为数学公式块标记行。

        Args:
            line: 要检查的行

        Returns:
            如果是数学公式块标记行返回True，否则返回False
        """
        stripped = line.strip()
        return stripped.startswith("$$")

    def _is_horizontal_rule_line(self, line: str) -> bool:
        """检查是否为水平分割线。

        Args:
            line: 要检查的行

        Returns:
            如果是水平分割线返回True，否则返回False
        """
        stripped = line.strip()
        # 检查是否为水平分割线（至少3个连续的 -、* 或 _）
        return bool(re.match(r"^[-*_]{3,}$", stripped))

    # ==================== 内容块提取方法 ====================

    def _extract_title_content(self, line: str) -> tuple[str, str]:
        """提取标题行的前缀和内容。

        Args:
            line: 标题行

        Returns:
            元组 (前缀, 内容)，前缀包含 # 符号和空格，内容为标题文本
        """
        stripped = line.strip()
        # 找到第一个非 # 字符的位置
        content_start = 0
        for i, char in enumerate(stripped):
            if char != "#":
                content_start = i
                break

        # 提取前缀（包含 # 符号和后续空格）
        prefix = stripped[:content_start] + " "
        # 提取内容（去除前导空格）
        content = stripped[content_start:].lstrip()

        return prefix, content

    def _extract_table_cells(self, line: str) -> list[str]:
        """提取表格行的单元格内容。

        Args:
            line: 表格行

        Returns:
            单元格内容列表，每个元素包含单元格的原始内容（包含前后空格）
        """
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            return []

        # 去除首尾的 |，然后按 | 分割
        cells = stripped[1:-1].split("|")
        return cells
