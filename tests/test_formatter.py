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


def test_punctuation_spacing() -> None:
    fmt = MarkdownFormatter()
    # 中文标点前后不加空格
    assert fmt.format_content("中文，English") == "中文，English"
    assert fmt.format_content("English。中文") == "English。中文"
    # 英文标点前后不加空格
    assert fmt.format_content("中文,English") == "中文, English"
    assert fmt.format_content("English.中文") == "English. 中文"
    # 标点与数字
    assert fmt.format_content("金额：123,456元") == "金额：123,456 元"
    # 标点与中英文混排
    assert fmt.format_content("你好!Hello.") == "你好! Hello."
    # 中文顿号与英文混排
    assert fmt.format_content("HTML、CSS、JavaScript") == "HTML、CSS、JavaScript"
    # 英文逗号与英文混排
    assert fmt.format_content("HTML,CSS,JavaScript") == "HTML, CSS, JavaScript"


def test_bracket_spacing() -> None:
    fmt = MarkdownFormatter()
    # 中文括号内英文不加空格
    assert fmt.format_content("这是（English）") == "这是（English）"
    # 中文括号内中文不加空格
    assert fmt.format_content("English（这是中文）") == "English（这是中文）"
    # 英文括号内英文正常
    assert fmt.format_content("(Hello)World") == "(Hello) World"
    # 中文括号内中文正常
    assert fmt.format_content("（你好）世界") == "（你好）世界"


def test_version_protection() -> None:
    fmt = MarkdownFormatter()
    # 版本号不加空格
    assert fmt.format_content("当前版本为v1.2.3") == "当前版本为 v1.2.3"
    assert fmt.format_content("v2.0.0-beta") == "v2.0.0-beta"
    # 版本号与中英文混排
    assert fmt.format_content("升级到v1.2.3后体验更好") == "升级到 v1.2.3 后体验更好"
    # 中文版本号不加空格
    assert fmt.format_content("当前版本为v主版本.次版本.修订版本") == "当前版本为 v主版本.次版本.修订版本"
    assert fmt.format_content("v主版本.次版本.修订版本发布") == "v主版本.次版本.修订版本发布"


def test_date_protection() -> None:
    fmt = MarkdownFormatter()
    # 纯数字日期
    assert fmt.format_content("今天是2025-07-22") == "今天是 2025-07-22"
    assert fmt.format_content("截止日期为07-22") == "截止日期为 07-22"
    assert fmt.format_content("会议时间：7月22日") == "会议时间：7月22日"
    assert fmt.format_content("2025年7月22日是个好日子") == "2025年7月22日 是个好日子"
    # 日期与英文混排
    assert fmt.format_content("Date: 2025-07-22.") == "Date: 2025-07-22."
    assert (
        fmt.format_content("The event is on 2025-07-22.")
        == "The event is on 2025-07-22."
    )
    # 日期与中文混排
    assert fmt.format_content("请于2025-07-22提交材料") == "请于 2025-07-22 提交材料"
    # 日期与数字混排
    assert fmt.format_content("编号2025-07-22-01") == "编号 2025-07-22-01"
    # 多种日期格式
    assert fmt.format_content("2025年7月22号") == "2025年7月22号"
    assert fmt.format_content("7月22号") == "7月22号"
    assert fmt.format_content("7-22") == "7-22"
