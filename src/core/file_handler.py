"""
File handling module for markdown-spacer.
"""

import os
from typing import Dict, List


def is_markdown_file(filename: str) -> bool:
    """判断文件名是否为 Markdown 文件（.md/.markdown 且主文件名非空）"""
    base, ext = os.path.splitext(filename)
    return ext.lower() in (".md", ".markdown") and base != ""


def read_markdown_file(filepath: str) -> str:
    """读取 Markdown 文件内容，UTF-8 编码，返回字符串。"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        raise e


def write_markdown_file(filepath: str, content: str) -> None:
    """将内容写入 Markdown 文件，UTF-8 编码，覆盖写入。"""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        raise e


def find_markdown_files(directory: str, recursive: bool = True) -> List[str]:
    """查找目录下所有 Markdown 文件，支持递归与非递归。
    返回文件路径列表（字符串）。
    """
    result = []
    if recursive:
        for root, _, files in os.walk(directory):
            for name in files:
                if is_markdown_file(name):
                    result.append(os.path.join(root, name))
    else:
        for name in os.listdir(directory):
            path = os.path.join(directory, name)
            if os.path.isfile(path) and is_markdown_file(name):
                result.append(path)
    return result


def read_markdown_files(filepaths: List[str]) -> Dict[str, str]:
    """批量读取多个 Markdown 文件，返回 {文件路径: 内容} 映射。只读取合法 Markdown 文件。"""
    result = {}
    for path in filepaths:
        if is_markdown_file(path):
            try:
                result[path] = read_markdown_file(path)
            except Exception:
                pass
    return result


def write_markdown_files(file_contents: Dict[str, str], backup: bool = False) -> None:
    """批量写入内容到多个 Markdown 文件，支持备份模式。遇到异常只跳过失败文件。"""
    for path, content in file_contents.items():
        try:
            if backup and os.path.isfile(path):
                backup_path = path + ".bak"
                with (
                    open(path, "r", encoding="utf-8") as fsrc,
                    open(backup_path, "w", encoding="utf-8") as fdst,
                ):
                    fdst.write(fsrc.read())
            write_markdown_file(path, content)
        except Exception:
            pass  # 跳过失败文件
