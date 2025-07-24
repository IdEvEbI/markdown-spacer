"""
markdown-spacer 格式化器测试模块。

本模块包含 MarkdownFormatter 类的单元测试，
验证中英文空格处理、特殊内容保护等功能的正确性。
"""

import pytest

from src.core.formatter import MarkdownFormatter


class TestMarkdownFormatter:
    """MarkdownFormatter 类测试套件。"""

    # ==================== 基础功能测试 ====================

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

    def test_patterns_compilation(self) -> None:
        """测试正则表达式模式编译。"""
        patterns = MarkdownFormatter._get_patterns()
        assert isinstance(patterns, dict)
        assert "basic_spacing" in patterns  # 合并后的基础空格处理正则
        assert "math_symbols" in patterns
        assert "minus_symbol" in patterns

    def test_cached_patterns(self) -> None:
        """测试正则表达式缓存机制。"""
        # 第一次调用
        patterns1 = MarkdownFormatter._get_patterns()
        # 第二次调用应该返回缓存的模式
        patterns2 = MarkdownFormatter._get_patterns()
        assert patterns1 is patterns2

    # ==================== 分层处理架构测试 ====================

    def test_line_type_recognition(self) -> None:
        """测试行类型识别功能。"""
        fmt = MarkdownFormatter()

        # 标题行识别
        assert fmt._is_title_line("# 标题") is True
        assert fmt._is_title_line("## 二级标题") is True
        assert fmt._is_title_line("普通文本") is False

        # 列表行识别
        assert fmt._is_list_line("- 列表项") is True
        assert fmt._is_list_line("* 列表项") is True
        assert fmt._is_list_line("+ 列表项") is True
        assert fmt._is_list_line("1. 有序列表") is True
        assert fmt._is_list_line("普通文本") is False

        # 引用行识别
        assert fmt._is_quote_line("> 引用内容") is True
        assert fmt._is_quote_line("普通文本") is False

        # 表格行识别
        assert fmt._is_table_line("| 列1 | 列2 |") is True
        assert fmt._is_table_line("| --- | --- |") is True
        assert fmt._is_table_line("普通文本") is False

        # 代码块识别
        assert fmt._is_code_block_line("```") is True
        assert fmt._is_code_block_line("```python") is True
        assert fmt._is_code_block_line("普通文本") is False

    def test_content_block_extraction(self) -> None:
        """测试内容块提取功能。"""
        fmt = MarkdownFormatter()

        # 标题内容提取
        prefix, content = fmt._extract_title_content("# 标题内容")
        assert prefix == "# "
        assert content == "标题内容"

        # 列表内容提取
        prefix, content = fmt._extract_list_content("- 列表内容")
        assert prefix == "- "
        assert content == "列表内容"

        # 引用内容提取
        prefix, content = fmt._extract_quote_content("> 引用内容")
        assert prefix == "> "
        assert content == "引用内容"

        # 表格单元格内容提取
        cells = fmt._extract_table_cells("| 单元格1 | 单元格2 |")
        assert cells == [" 单元格1 ", " 单元格2 "]

    def test_structure_preservation(self) -> None:
        """测试结构标记保护功能。"""
        fmt = MarkdownFormatter()

        # 标题结构保护
        result = fmt._format_line("# 中文English")
        assert result.startswith("# ")
        assert "中文 English" in result

        # 列表结构保护
        result = fmt._format_line("- 中文English")
        assert result.startswith("- ")
        assert "中文 English" in result

        # 引用结构保护
        result = fmt._format_line("> 中文English")
        assert result.startswith("> ")
        assert "中文 English" in result

        # 表格结构保护
        result = fmt._format_line("| 中文 | English |")
        assert result.startswith("|")
        assert result.endswith("|")
        assert "中文" in result
        assert "English" in result

    # ==================== 特殊内容保护测试 ====================

    def test_code_block_protection(self) -> None:
        """测试代码块保护。"""
        fmt = MarkdownFormatter()

        # 多行代码块保护
        code_block = """```
print('Hello World')
中文English
```
"""
        assert fmt.format_content(code_block) == code_block

        # 带语言标识的代码块
        code_block_python = """```python
def hello():
    print('Hello World')
```
"""
        assert fmt.format_content(code_block_python) == code_block_python

    def test_inline_code_protection(self) -> None:
        """测试行内代码保护。"""
        fmt = MarkdownFormatter()

        # 行内代码保护
        inline_code = "`print('Hello')`"
        assert fmt.format_content(inline_code) == inline_code

        # 行内代码中的中英文混排
        inline_mixed = "`中文English`"
        assert fmt.format_content(inline_mixed) == inline_mixed

    def test_link_and_image_protection(self) -> None:
        """测试链接和图片保护。"""
        fmt = MarkdownFormatter()

        # 链接保护
        link = "[中文English](http://example.com)"
        assert fmt.format_content(link) == link

        # 图片保护
        image = "![中文English](http://example.com/img.png)"
        assert fmt.format_content(image) == image

    def test_math_formula_protection(self) -> None:
        """测试数学公式保护。"""
        fmt = MarkdownFormatter()

        # 行内数学公式
        inline_math = "$中文English$"
        assert fmt.format_content(inline_math) == inline_math

        # 块级数学公式
        block_math = """$$
中文English
$$
"""
        assert fmt.format_content(block_math) == block_math

    def test_html_tag_protection(self) -> None:
        """测试HTML标签保护。"""
        fmt = MarkdownFormatter()

        # HTML标签保护
        html = "<span>中文English</span>"
        assert fmt.format_content(html) == html

    # ==================== 基本空格处理测试 ====================

    def test_basic_spacing_rules(self) -> None:
        """测试基本空格处理规则。"""
        fmt = MarkdownFormatter()

        # 中英文间空格
        assert fmt.content_spacing_fix("中文English") == "中文 English"
        assert fmt.content_spacing_fix("English中文") == "English 中文"

        # 中数字间空格
        assert fmt.content_spacing_fix("中文123") == "中文 123"
        assert fmt.content_spacing_fix("123中文") == "123 中文"

        # 英数字间空格
        assert fmt.content_spacing_fix("English123") == "English 123"
        assert fmt.content_spacing_fix("123English") == "123 English"

    def test_math_symbols_spacing(self) -> None:
        """测试数学符号空格处理。"""
        fmt = MarkdownFormatter()

        # 数学符号
        assert fmt.content_spacing_fix("A+B") == "A + B"
        assert fmt.content_spacing_fix("张三-李四") == "张三 - 李四"
        assert fmt.content_spacing_fix("10*5") == "10 * 5"

    def test_punctuation_spacing(self) -> None:
        """测试标点符号空格处理。"""
        fmt = MarkdownFormatter()

        # 英文标点后空格
        assert fmt.content_spacing_fix("Hello,world") == "Hello, world"
        assert fmt.content_spacing_fix("Hello.world") == "Hello. world"

        # 英文右括号后空格
        assert fmt.content_spacing_fix("(test)world") == "(test) world"

    def test_chinese_slash_spacing(self) -> None:
        """测试中文斜杠分隔空格处理。"""
        fmt = MarkdownFormatter()

        # 中文斜杠分隔
        assert fmt.content_spacing_fix("文本/JSON") == "文本 / JSON"
        assert fmt.content_spacing_fix("前端/后端") == "前端 / 后端"

    def test_number_chinese_spacing(self) -> None:
        """测试编号与中文空格处理。"""
        fmt = MarkdownFormatter()

        # 编号与中文
        assert fmt.content_spacing_fix("优先级1") == "优先级 1"
        assert fmt.content_spacing_fix("版本2.0") == "版本 2.0"

    # ==================== 多空格合并测试 ====================

    def test_multiple_spaces_merge(self) -> None:
        """测试多空格合并。"""
        fmt = MarkdownFormatter()

        # 多个连续空格合并
        assert fmt.content_spacing_fix("中文   English") == "中文 English"
        assert fmt.content_spacing_fix("A    B    C") == "A B C"

    # ==================== 业务规则修复测试 ====================

    def test_version_number_fix(self) -> None:
        """测试版本号修复。"""
        fmt = MarkdownFormatter()

        # 版本号修复
        assert fmt.content_spacing_fix("v 1.2.3") == "v1.2.3"
        assert fmt.content_spacing_fix("v 2.0.0-beta") == "v2.0.0-beta"

    def test_number_unit_fix(self) -> None:
        """测试数字与单位修复。"""
        fmt = MarkdownFormatter()

        # 数字与单位修复
        assert fmt.content_spacing_fix("10 MB") == "10MB"
        assert fmt.content_spacing_fix("100 GB") == "100GB"
        assert fmt.content_spacing_fix("5 ms") == "5ms"
        assert fmt.content_spacing_fix("20 ℃") == "20℃"

    def test_tech_abbr_fix(self) -> None:
        """测试技术缩写修复。"""
        fmt = MarkdownFormatter()

        # 技术缩写修复
        assert fmt.content_spacing_fix("UTF - 8") == "UTF-8"
        assert fmt.content_spacing_fix("JSON - LD") == "JSON-LD"
        assert fmt.content_spacing_fix("ISO - 8859 - 1") == "ISO-8859-1"

    def test_english_hyphen_fix(self) -> None:
        """测试英文连字符修复。"""
        fmt = MarkdownFormatter()

        # 英文连字符修复
        assert fmt.content_spacing_fix("Todo - List") == "Todo-List"
        assert fmt.content_spacing_fix("e - mail") == "e-mail"

    def test_file_extension_fix(self) -> None:
        """测试文件扩展名修复。"""
        fmt = MarkdownFormatter()

        # 文件扩展名修复
        assert fmt.content_spacing_fix("requirements . txt") == "requirements.txt"
        assert fmt.content_spacing_fix("main . cpp") == "main.cpp"

    def test_tool_name_fix(self) -> None:
        """测试工具名修复。"""
        fmt = MarkdownFormatter()

        # 工具名修复
        assert fmt.content_spacing_fix("flake 8") == "flake8"
        assert fmt.content_spacing_fix("black ") == "black"

    def test_path_fix(self) -> None:
        """测试路径修复。"""
        fmt = MarkdownFormatter()

        # 基本路径修复
        assert (
            fmt.content_spacing_fix("src / core / formatter. py")
            == "src/core/formatter.py"
        )
        assert (
            fmt.content_spacing_fix("docs / design / plan. md") == "docs/design/plan.md"
        )

        # 多个路径在同一行的测试用例
        assert (
            fmt.content_spacing_fix(
                "请查看 src / core / formatter. py 和 docs / design / plan. md"
            )
            == "请查看 src/core/formatter.py 和 docs/design/plan.md"
        )
        assert (
            fmt.content_spacing_fix("配置文件：config / app. yaml 和 config / db. json")
            == "配置文件：config/app.yaml 和 config/db.json"
        )

        # 路径与中文内容混合的复杂场景测试
        assert (
            fmt.content_spacing_fix("项目结构：src / core / 核心模块 / formatter. py")
            == "项目结构：src/core/核心模块/formatter.py"
        )
        assert (
            fmt.content_spacing_fix("文档路径：docs / 中文文档 / 设计文档. md")
            == "文档路径：docs/中文文档/设计文档.md"
        )

        # 复杂路径场景测试
        assert (
            fmt.content_spacing_fix("深度路径：src / core / utils / helpers / formatter. py")
            == "深度路径：src/core/utils/helpers/formatter.py"
        )
        assert (
            fmt.content_spacing_fix("多级目录：project / src / core / formatter. py")
            == "多级目录：project/src/core/formatter.py"
        )

        # 边界情况测试
        assert (
            fmt.content_spacing_fix("/usr / local / bin / python")
            == "/usr/local/bin/python"
        )
        assert (
            fmt.content_spacing_fix("C: / Program Files / Python / python. exe")
            == "C:/Program Files/Python/python.exe"
        )

    def test_comparison_symbol_fix(self) -> None:
        """测试比较符号修复。"""
        fmt = MarkdownFormatter()

        # 比较符号修复
        assert fmt.content_spacing_fix(">=100GB") == ">= 100GB"
        assert fmt.content_spacing_fix("<5ms") == "< 5ms"
        assert fmt.content_spacing_fix("!=30s") == "!= 30s"

    def test_date_format_fix(self) -> None:
        """测试日期格式修复。"""
        fmt = MarkdownFormatter()

        # 日期格式修复
        assert fmt.content_spacing_fix("2025 年 7 月 24 日") == "2025年7月24日"
        assert fmt.content_spacing_fix("7 月 22 日") == "7月22日"

    def test_number_unit_plus_fix(self) -> None:
        """测试数字+单位+加号修复。"""
        fmt = MarkdownFormatter()

        # 数字+单位+加号修复
        assert fmt.content_spacing_fix("4 GB +") == "4GB+"
        assert fmt.content_spacing_fix("8 GB +") == "8GB+"

    def test_filename_protection(self) -> None:
        """测试文件名格式保护。"""
        fmt = MarkdownFormatter()

        # 文件名格式保护
        assert fmt.content_spacing_fix("requirements.txt") == "requirements.txt"
        assert fmt.content_spacing_fix("setup.py") == "setup.py"
        assert fmt.content_spacing_fix("pyproject.toml") == "pyproject.toml"

    # ==================== 中文双引号加粗测试 ====================

    def test_chinese_quotes_bold(self) -> None:
        """测试中文双引号加粗功能。"""
        fmt = MarkdownFormatter(bold_quotes=True)

        # 基本加粗
        assert fmt.content_spacing_fix('他说："你好"') == "他说：**你好**"
        assert fmt.content_spacing_fix('世界"你好"啊') == "世界 **你好** 啊"
        assert fmt.content_spacing_fix('这是"重点"内容') == "这是 **重点** 内容"

        # 嵌套引号不处理
        assert fmt.content_spacing_fix('"外层"内层"内容"') == '"外层"内层"内容"'
        assert fmt.content_spacing_fix('"这是"重点"内容"') == '"这是"重点"内容"'

        # 复杂情况测试
        assert fmt.content_spacing_fix('他说："你好"，然后"再见"') == "他说：**你好**，然后 **再见**"
        assert fmt.content_spacing_fix('"外层"内层"内容"外层') == '"外层"内层"内容"外层'

        # 边界情况测试
        assert fmt.content_spacing_fix('"单独引号"') == '"单独引号"'
        assert fmt.content_spacing_fix('开始"结束') == '开始"结束'  # 不完整的引号对
        assert fmt.content_spacing_fix('"开始结束') == '"开始结束'  # 不完整的引号对

        # 禁用加粗功能测试
        fmt_disabled = MarkdownFormatter(bold_quotes=False)
        assert fmt_disabled.content_spacing_fix('他说："你好"') == '他说："你好"'

    # ==================== 边界情况测试 ====================

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

    def test_complex_markdown_document(self) -> None:
        """测试复杂Markdown文档处理。"""
        fmt = MarkdownFormatter()

        # 从文件加载测试文档
        test_file_path = "tests/test_files/complex_document.md"
        with open(test_file_path, "r", encoding="utf-8") as f:
            complex_doc = f.read()

        result = fmt.format_content(complex_doc)

        # 验证结构保持
        assert "# 项目标题" in result
        assert "## 功能列表" in result
        assert "```python" in result
        assert "| 列 1 |" in result  # 表格内容中的中英文混排应该被处理

        # 验证内容处理
        assert "中文 English" in result
        assert "中文 123" in result
        assert "A + B" in result  # 数学符号处理已实现

        # 验证特殊格式处理
        assert "UTF-8" in result  # 技术缩写应该被处理
        assert "10MB" in result  # 单位应该被处理
        assert "v1.2.3" in result  # 版本号应该被处理

        # 验证保护内容
        assert "```python" in result  # 代码块应该被保护
        assert "$中文English公式$" in result  # 数学公式应该被保护
        assert "[中文English链接]" in result  # 链接应该被保护

        # 验证嵌套结构
        assert "- 子项 1 English" in result  # 嵌套列表应该被处理
        assert "> 这是一个引用块 English" in result  # 引用应该被处理

        # 验证边界情况
        assert "这里 有 多个 空格 需要 合并" in result  # 连续空格应该被合并


if __name__ == "__main__":
    pytest.main([__file__])
