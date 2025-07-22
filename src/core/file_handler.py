"""
File handling module for markdown-spacer.
"""

import os


def is_markdown_file(filename: str) -> bool:
    """判断文件名是否为 Markdown 文件（.md/.markdown 且主文件名非空）"""
    base, ext = os.path.splitext(filename)
    return ext.lower() in (".md", ".markdown") and base != ""


def read_markdown_file(filepath: str) -> str:
    """读取 Markdown 文件内容，UTF-8 编码，返回字符串。"""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def write_markdown_file(filepath: str, content: str) -> None:
    """将内容写入 Markdown 文件，UTF-8 编码，覆盖写入。"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
