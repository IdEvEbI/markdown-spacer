"""
markdown-spacer 核心格式化算法模块。

本模块实现了 Markdown 文档中英文、数字间空格处理的核心算法，
包括正则表达式规则定义、内容格式化处理、特殊内容保护等功能。
"""

import logging
import re
from re import Match
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
            # 基础空格处理规则
            "chinese_english": re.compile(r"([\u4e00-\u9fa5])([a-zA-Z])"),
            "english_chinese": re.compile(r"([a-zA-Z])([\u4e00-\u9fa5])"),
            "chinese_number": re.compile(r"([\u4e00-\u9fa5])(\d)"),
            "number_chinese": re.compile(r"(\d)([\u4e00-\u9fa5])"),
            "number_english": re.compile(r"(\d)([a-zA-Z])(?!\s*[>=<≤≥＝≠])"),
            "english_number": re.compile(r"([a-zA-Z])(\d)"),
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
            "tech_abbr_multi": re.compile(r"([A-Z]{2,}) - ([A-Z0-9]+) - ([A-Z0-9]+)"),
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
        """格式化单行内容（重构版本）。

        使用分层处理架构：
        1. 识别行类型
        2. 提取结构标记和内容块
        3. 对内容块进行空格处理
        4. 重新组装行

        Args:
            line: 要格式化的行

        Returns:
            格式化后的行
        """
        # 检查是否为受保护的内容（代码块、数学公式等）
        if self._is_protected_content(line):
            return line

        # 检查是否为水平分割线
        if self._is_horizontal_rule_line(line):
            return line

        # 标题行处理
        if self._is_title_line(line):
            prefix, content = self._extract_title_content(line)
            processed_content = self.content_spacing_fix(content)
            return prefix + processed_content

        # 列表行处理
        if self._is_list_line(line):
            prefix, content = self._extract_list_content(line)
            processed_content = self.content_spacing_fix(content)
            return prefix + processed_content

        # 引用行处理
        if self._is_quote_line(line):
            prefix, content = self._extract_quote_content(line)
            processed_content = self.content_spacing_fix(content)
            return prefix + processed_content

        # 表格行处理
        if self._is_table_line(line):
            # 检查是否为表格分隔行
            if re.search(r"\|[\s]*[-:]+\s*\|", line.strip()):
                # 表格分隔行，保持原样
                return line

            # 普通表格行，处理单元格内容
            cells = self._extract_table_cells(line)
            processed_cells = []
            for cell in cells:
                cell_content = cell.strip()
                if cell_content:
                    processed_content = self.content_spacing_fix(cell_content)
                    processed_cells.append(" " + processed_content + " ")
                else:
                    processed_cells.append(" ")

            return "|" + "|".join(processed_cells) + "|"

        # 普通文本行处理
        return self.content_spacing_fix(line)

    def content_spacing_fix(self, text: str) -> str:
        """内容块空格修复（基础实现）。

        处理流程：
        1. 特殊内容保护
        2. 基础空格处理
        3. 业务规则修复
        4. 恢复特殊内容

        Args:
            text: 要处理的文本

        Returns:
            处理后的文本
        """
        # [DEBUG] 调试输出 - 开发完成后统一清理
        print(f"[DEBUG] 开始处理: '{text}'")

        # 特殊内容保护：先保存特殊内容，用占位符替换
        protected_content: Dict[str, str] = {}
        text = self._protect_special_content(text, protected_content)
        print(f"[DEBUG] 特殊内容保护后: '{text}'")

        # 基础空格处理
        text = self._patterns["chinese_english"].sub(r"\1 \2", text)
        text = self._patterns["english_chinese"].sub(r"\1 \2", text)
        text = self._patterns["chinese_number"].sub(r"\1 \2", text)
        text = self._patterns["number_chinese"].sub(r"\1 \2", text)
        text = self._patterns["number_english"].sub(r"\1 \2", text)
        text = self._patterns["english_number"].sub(r"\1 \2", text)
        print(f"[DEBUG] 基础空格处理后: '{text}'")

        # 数学符号空格处理
        text = self._patterns["math_symbols"].sub(r"\1 \2 \3", text)
        print(f"[DEBUG] 数学符号处理后: '{text}'")

        # 减号符号空格处理（排除版本号中的连字符）
        text = self._patterns["minus_symbol"].sub(r"\1 \2 \3", text)
        print(f"[DEBUG] 减号符号处理后: '{text}'")

        # 标点符号空格处理
        text = self._patterns["punctuation_after"].sub(r"\1 \2", text)
        text = self._patterns["rparen_after"].sub(r"\1 \2", text)
        print(f"[DEBUG] 标点符号处理后: '{text}'")

        # 中文斜杠分隔空格处理
        text = self._patterns["chinese_slash"].sub(r"\1 / \2", text)
        print(f"[DEBUG] 斜杠分隔处理后: '{text}'")

        # 编号与中文空格处理
        text = self._patterns["number_chinese_priority"].sub(r"\1 \2", text)
        print(f"[DEBUG] 编号中文处理后: '{text}'")

        # 合并多个连续空格
        text = re.sub(r" +", " ", text)
        print(f"[DEBUG] 多空格合并后: '{text}'")

        # 业务规则修复（删除不应该存在的空格）- 最后进行
        text = self._apply_business_rules(text)
        print(f"[DEBUG] 业务规则修复后: '{text}'")

        # 中文双引号加粗（可选功能）
        if self.bold_quotes:
            text = self._fix_chinese_quotes_bold(text)
            print(f"[DEBUG] 中文双引号加粗后: '{text}'")

        # 恢复特殊内容
        text = self._restore_special_content(text, protected_content)
        print(f"[DEBUG] 恢复特殊内容后: '{text}'")
        print(f"[DEBUG] 最终结果: '{text}'")
        print("[DEBUG] " + "-" * 50)

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
        """修复中文双引号加粗。

        Args:
            text: 要修复的文本

        Returns:
            修复后的文本
        """
        # 如果文本以引号开始，说明是嵌套引号，不处理
        if text.startswith('"'):
            return text

        def replace_quotes(match: Match[str]) -> str:
            """替换引号内容的回调函数"""
            content = match.group(1)
            # 在加粗内容前后添加空格（如果前后不是空格或标点）
            bold_content = "**" + content + "**"

            # 检查前面是否需要空格
            if (
                match.start() > 0
                and not text[match.start() - 1].isspace()
                and text[match.start() - 1] not in "，。！？；："
            ):
                bold_content = " " + bold_content

            # 检查后面是否需要空格
            if (
                match.end() < len(text)
                and not text[match.end()].isspace()
                and text[match.end()] not in "，。！？；："
            ):
                bold_content = bold_content + " "

            return bold_content

        # 使用正则表达式查找所有引号对，但只处理第一个完整的引号对
        # 匹配模式：非引号字符 + 引号 + 内容 + 引号 + 非引号字符
        pattern = r'"([^"]*)"'
        return re.sub(pattern, replace_quotes, text)

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
        """检查是否为列表行。

        Args:
            line: 要检查的行

        Returns:
            如果是列表行返回True，否则返回False
        """
        stripped = line.strip()
        # 无序列表：-、*、+
        if stripped.startswith(("-", "*", "+")):
            return True
        # 有序列表：数字. 格式
        if re.match(r"^\d+\.\s", stripped):
            return True
        # 任务列表：[ ] 或 [x]
        if re.match(r"^[-*+]\s*\[[ xX]\]", stripped):
            return True
        return False

    def _is_quote_line(self, line: str) -> bool:
        """检查是否为引用行。

        Args:
            line: 要检查的行

        Returns:
            如果是引用行返回True，否则返回False
        """
        stripped = line.strip()
        return stripped.startswith(">")

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

    def _extract_list_content(self, line: str) -> tuple[str, str]:
        """提取列表行的前缀和内容。

        Args:
            line: 列表行

        Returns:
            元组 (前缀, 内容)，前缀包含列表标记和空格，内容为列表项文本
        """
        stripped = line.strip()

        # 处理有序列表：数字. 格式
        if re.match(r"^\d+\.\s", stripped):
            match = re.match(r"^(\d+\.\s+)(.*)", stripped)
            if match:
                return match.group(1), match.group(2)

        # 处理任务列表：[-*+] [ ] 格式
        if re.match(r"^[-*+]\s*\[[ xX]\]", stripped):
            match = re.match(r"^([-*+]\s*\[[ xX]\]\s+)(.*)", stripped)
            if match:
                return match.group(1), match.group(2)

        # 处理普通无序列表：[-*+] 格式
        if stripped.startswith(("-", "*", "+")):
            # 找到第一个空格后的内容
            space_pos = stripped.find(" ")
            if space_pos != -1:
                prefix = stripped[: space_pos + 1]
                content = stripped[space_pos + 1 :]
                return prefix, content

        # 默认情况
        return "", stripped

    def _extract_quote_content(self, line: str) -> tuple[str, str]:
        """提取引用行的前缀和内容。

        Args:
            line: 引用行

        Returns:
            元组 (前缀, 内容)，前缀包含 > 符号和空格，内容为引用文本
        """
        stripped = line.strip()
        if stripped.startswith(">"):
            # 找到第一个非 > 字符的位置
            content_start = 0
            for i, char in enumerate(stripped):
                if char != ">":
                    content_start = i
                    break

            # 提取前缀（包含 > 符号和后续空格）
            prefix = stripped[:content_start] + " "
            # 提取内容（去除前导空格）
            content = stripped[content_start:].lstrip()

            return prefix, content

        return "", stripped

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
