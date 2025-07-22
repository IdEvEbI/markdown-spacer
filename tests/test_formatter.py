from src.core.formatter import MarkdownFormatter


def test_chinese_english_spacing() -> None:
    fmt = MarkdownFormatter()
    assert fmt.format_content("中文English") == "中文 English"
    assert fmt.format_content("English中文") == "English 中文"


def test_chinese_number_spacing() -> None:
    fmt = MarkdownFormatter()
    assert fmt.format_content("中文123") == "中文 123"
    assert fmt.format_content("123中文") == "123 中文"


def test_math_symbols_spacing() -> None:
    fmt = MarkdownFormatter()
    assert fmt.format_content("A+B") == "A + B"
    assert fmt.format_content("张三-李四") == "张三 - 李四"
    assert fmt.format_content("草稿/进行中/已完成/归档") == "草稿 / 进行中 / 已完成 / 归档"


def test_chinese_hyphen() -> None:
    fmt = MarkdownFormatter()
    assert fmt.format_content("张三-李四") == "张三 - 李四"
    assert fmt.format_content("Todo-List") == "Todo-List"  # 英文连字符不加空格


def test_code_block_protection() -> None:
    fmt = MarkdownFormatter()
    input_text = """```
中文English
```
"""
    assert fmt.format_content(input_text) == input_text


def test_inline_code_protection() -> None:
    fmt = MarkdownFormatter()
    input_text = "`中文English`"
    assert fmt.format_content(input_text) == input_text


def test_link_and_image_protection() -> None:
    fmt = MarkdownFormatter()
    link = "[中文English](http://example.com)"
    image = "![中文English](http://example.com/img.png)"
    assert fmt.format_content(link) == link
    assert fmt.format_content(image) == image


def test_table_protection() -> None:
    fmt = MarkdownFormatter()
    table = "| 列1 | 列2English |\n| ---- | ---- |\n| 中文 | English |"
    expected = "| 列 1 | 列 2 English |\n| ---- | ---- |\n| 中文 | English |"
    assert fmt.format_content(table) == expected


def test_list_and_title_protection() -> None:
    fmt = MarkdownFormatter()
    assert fmt.format_content("- 中文English") == "- 中文 English"
    assert fmt.format_content("# 中文English") == "# 中文 English"


def test_math_formula_protection() -> None:
    fmt = MarkdownFormatter()
    assert fmt.format_content("$中文English$") == "$中文English$"
    assert fmt.format_content("$$\n中文English\n$$") == "$$\n中文English\n$$"


def test_table_spacing() -> None:
    fmt = MarkdownFormatter()
    table = "| 列1 | 列2English |\n| ---- | ---- |\n| 中文 | English中文 |"
    expected = "| 列 1 | 列 2 English |\n| ---- | ---- |\n| 中文 | English 中文 |"
    assert fmt.format_content(table) == expected


def test_list_spacing() -> None:
    fmt = MarkdownFormatter()
    assert fmt.format_content("- 中文English") == "- 中文 English"
    assert fmt.format_content("* English中文") == "* English 中文"
    assert fmt.format_content("+ 中文123") == "+ 中文 123"


def test_title_spacing() -> None:
    fmt = MarkdownFormatter()
    assert fmt.format_content("# 中文English") == "# 中文 English"
    assert fmt.format_content("## English中文") == "## English 中文"
