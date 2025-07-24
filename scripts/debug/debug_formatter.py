#!/usr/bin/env python3
"""
markdown-spacer 格式化器调试文件

用于快速测试和调试 MarkdownFormatter 的各种功能
"""

import os
import sys

# 添加项目根目录到 Python 路径（从 scripts/debug/ 目录向上两级）
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, project_root)

from src.core.formatter import MarkdownFormatter


def test_basic_spacing():
    """测试基础空格处理"""
    print("=== 基础空格处理测试 ===")
    fmt = MarkdownFormatter()

    test_cases = [
        ("中文English", "中文 English"),
        ("English中文", "English 中文"),
        ("中文123", "中文 123"),
        ("123中文", "123 中文"),
        ("English123", "English 123"),
        ("123English", "123 English"),
    ]

    for input_text, expected in test_cases:
        result = fmt.content_spacing_fix(input_text)
        status = "✅" if result == expected else "❌"
        print(f"{status} 输入: {input_text}")
        print(f"   期望: {expected}")
        print(f"   实际: {result}")
        print()


def test_math_symbols():
    """测试数学符号处理"""
    print("=== 数学符号处理测试 ===")
    fmt = MarkdownFormatter()

    test_cases = [
        ("A+B", "A + B"),
        ("张三-李四", "张三 - 李四"),
        ("10*5", "10 * 5"),
        ("A+B=C", "A + B=C"),
    ]

    for input_text, expected in test_cases:
        result = fmt.content_spacing_fix(input_text)
        status = "✅" if result == expected else "❌"
        print(f"{status} 输入: {input_text}")
        print(f"   期望: {expected}")
        print(f"   实际: {result}")
        print()


def test_punctuation():
    """测试标点符号处理"""
    print("=== 标点符号处理测试 ===")
    fmt = MarkdownFormatter()

    test_cases = [
        ("Hello,world", "Hello, world"),
        ("Hello.world", "Hello. world"),
        ("(test)world", "(test) world"),
    ]

    for input_text, expected in test_cases:
        result = fmt.content_spacing_fix(input_text)
        status = "✅" if result == expected else "❌"
        print(f"{status} 输入: {input_text}")
        print(f"   期望: {expected}")
        print(f"   实际: {result}")
        print()


def test_protection():
    """测试特殊内容保护"""
    print("=== 特殊内容保护测试 ===")
    fmt = MarkdownFormatter()

    test_cases = [
        # 数学公式保护
        ("数学公式：$中文English公式$", "数学公式：$中文English公式$"),
        ("块级公式：$$中文English公式$$", "块级公式：$$中文English公式$$"),
        # 行内代码保护
        ('代码：`print("Hello中文English")`', '代码：`print("Hello中文English")`'),
        # 链接保护
        (
            "链接：[中文English链接](http://example.com)",
            "链接：[中文English链接](http://example.com)",
        ),
        # 图片保护
        (
            "图片：![中文English图片](http://example.com/img.png)",
            "图片：![中文English图片](http://example.com/img.png)",
        ),
        # HTML标签保护
        ("HTML：<span>中文English</span>", "HTML：<span>中文English</span>"),
    ]

    for input_text, expected in test_cases:
        result = fmt.content_spacing_fix(input_text)
        status = "✅" if result == expected else "❌"
        print(f"{status} 输入: {input_text}")
        print(f"   期望: {expected}")
        print(f"   实际: {result}")
        print()


def test_mixed_content():
    """测试混合内容"""
    print("=== 混合内容测试 ===")
    fmt = MarkdownFormatter()

    test_cases = [
        # 混合内容：普通文本 + 数学公式 + 代码
        (
            '这是一个公式：$A+B$ 和代码：`print("Hello")` 以及普通文本：中文English',
            '这是一个公式：$A+B$ 和代码：`print("Hello")` 以及普通文本：中文 English',
        ),
        # 混合内容：链接 + 数学符号
        (
            "链接：[测试链接](url) 和数学：A+B=C",
            "链接：[测试链接](url) 和数学：A + B=C",
        ),
    ]

    for input_text, expected in test_cases:
        result = fmt.content_spacing_fix(input_text)
        status = "✅" if result == expected else "❌"
        print(f"{status} 输入: {input_text}")
        print(f"   期望: {expected}")
        print(f"   实际: {result}")
        print()


def test_regex_patterns():
    """测试正则表达式模式"""
    print("=== 正则表达式模式测试 ===")
    import re

    # 测试数学公式正则
    text = "数学公式：$中文English公式$"
    pattern = r"(\$[^$\n]*\$)"
    matches = re.findall(pattern, text)
    print(f"数学公式匹配: {matches}")

    # 测试行内代码正则
    text2 = '代码：`print("Hello中文English")`'
    pattern2 = r"(`[^`]*`)"
    matches2 = re.findall(pattern2, text2)
    print(f"行内代码匹配: {matches2}")

    # 测试链接正则
    text3 = "链接：[中文English链接](http://example.com)"
    pattern3 = r"(\[[^\]]*\]\([^)]*\))"
    matches3 = re.findall(pattern3, text3)
    print(f"链接匹配: {matches3}")


def test_html_protection():
    """专门测试HTML标签保护"""
    print("=== HTML标签保护测试 ===")
    fmt = MarkdownFormatter()

    test_cases = [
        ("<span>中文English</span>", "<span>中文English</span>"),
        ("<div>测试内容</div>", "<div>测试内容</div>"),
        ("<p>段落内容</p>", "<p>段落内容</p>"),
        ("<a href='#'>链接文本</a>", "<a href='#'>链接文本</a>"),
    ]

    for input_text, expected in test_cases:
        result = fmt.content_spacing_fix(input_text)
        status = "✅" if result == expected else "❌"
        print(f"{status} 输入: {input_text}")
        print(f"   期望: {expected}")
        print(f"   实际: {result}")
        print()


def main():
    """主函数"""
    print("🚀 markdown-spacer 格式化器调试工具")
    print("=" * 50)

    # 运行所有测试
    test_basic_spacing()
    test_math_symbols()
    test_punctuation()
    test_protection()
    test_mixed_content()
    test_regex_patterns()
    test_html_protection()  # 添加HTML保护测试

    print("🎉 调试完成！")


if __name__ == "__main__":
    main()
