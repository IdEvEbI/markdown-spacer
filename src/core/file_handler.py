"""
markdown-spacer 文件处理模块。

本模块负责 Markdown 文件的识别、读取、写入和批量处理，
包括文件类型验证、内容合法性检查、备份功能等。
"""

import os
from typing import Dict, List


def is_markdown_file(filename: str) -> bool:
    """判断文件名是否为 Markdown 文件。

    Args:
        filename: 要检查的文件名

    Returns:
        如果是 Markdown 文件（.md/.markdown 且主文件名非空）则返回 True
    """
    base, ext = os.path.splitext(filename)
    return ext.lower() in (".md", ".markdown") and base != ""


def is_valid_markdown_content(filepath: str) -> bool:
    """判断文件内容是否为有效的 Markdown 格式。

    Args:
        filepath: 要检查的文件路径

    Returns:
        如果文件内容符合 Markdown 格式（首个非空行以 # 或 --- 开头）则返回 True

    Note:
        此函数通过检查文件首个非空行的开头来判断是否为 Markdown 文件。
        如果文件读取失败，返回 False。
    """
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if line.startswith("---") or line.startswith("#"):
                    return True
                return False
        return False
    except Exception:
        return False


def read_markdown_file(filepath: str) -> str:
    """读取 Markdown 文件内容。

    Args:
        filepath: 要读取的文件路径

    Returns:
        文件内容字符串

    Raises:
        FileNotFoundError: 文件不存在时抛出
        PermissionError: 无读取权限时抛出
        UnicodeDecodeError: 文件编码错误时抛出
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        raise e


def write_markdown_file(filepath: str, content: str) -> None:
    """将内容写入 Markdown 文件。

    Args:
        filepath: 要写入的文件路径
        content: 要写入的内容

    Raises:
        PermissionError: 无写入权限时抛出
        OSError: 磁盘空间不足或其他系统错误时抛出
    """
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        raise e


def find_markdown_files(directory: str, recursive: bool = True) -> List[str]:
    """查找目录下所有 Markdown 文件。

    Args:
        directory: 要搜索的目录路径
        recursive: 是否递归搜索子目录，默认为 True

    Returns:
        找到的 Markdown 文件路径列表（只返回内容合法的文件）

    Note:
        此函数会同时检查文件扩展名和内容格式，确保返回的是有效的 Markdown 文件。
    """
    result = []
    if recursive:
        for root, _, files in os.walk(directory):
            for name in files:
                path = os.path.join(root, name)
                if is_markdown_file(name) and is_valid_markdown_content(path):
                    result.append(path)
    else:
        for name in os.listdir(directory):
            path = os.path.join(directory, name)
            if (
                os.path.isfile(path)
                and is_markdown_file(name)
                and is_valid_markdown_content(path)
            ):
                result.append(path)
    return result


def read_markdown_files(filepaths: List[str]) -> Dict[str, str]:
    """批量读取多个 Markdown 文件。

    Args:
        filepaths: 要读取的文件路径列表

    Returns:
        文件路径到内容的映射字典 {文件路径: 内容}

    Note:
        只读取内容合法的 Markdown 文件，读取失败的文件会被跳过。
    """
    result = {}
    for path in filepaths:
        if is_markdown_file(path) and is_valid_markdown_content(path):
            try:
                result[path] = read_markdown_file(path)
            except Exception:
                pass
    return result


def write_markdown_files(file_contents: Dict[str, str], backup: bool = False) -> None:
    """批量写入内容到多个 Markdown 文件。

    Args:
        file_contents: 文件路径到内容的映射字典 {文件路径: 内容}
        backup: 是否在写入前创建备份文件，默认为 False

    Note:
        支持备份模式，遇到异常时只跳过失败的文件，继续处理其他文件。
        备份文件以 .bak 后缀命名。
    """
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
