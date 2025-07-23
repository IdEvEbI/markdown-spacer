"""
流式文件处理模块。

本模块提供大文件的流式处理功能，通过逐行读取和处理，
减少内存占用，提高处理效率，天然避免边界问题。
"""

import os
from typing import Generator

from src.core.formatter import MarkdownFormatter


class CodeBlockHandler:
    """代码块边界处理器。

    处理 Markdown 代码块的开始和结束标记，确保代码块内容不被格式化。
    """

    def __init__(self) -> None:
        """初始化代码块处理器。"""
        self.in_code_block = False
        self.code_block_buffer: list[str] = []

    def process_line_with_code_block(
        self, line: str, formatter: MarkdownFormatter
    ) -> str:
        """处理包含代码块的行。

        Args:
            line: 要处理的行
            formatter: Markdown 格式化器

        Returns:
            处理后的行
        """
        stripped_line = line.strip()

        # 检测代码块开始或结束
        if stripped_line.startswith("```"):
            if not self.in_code_block:
                # 代码块开始
                self.in_code_block = True
                self.code_block_buffer = [line]
                return line  # 不处理代码块开始行
            else:
                # 代码块结束
                self.in_code_block = False
                self.code_block_buffer.append(line)
                return "\n".join(self.code_block_buffer)

        if self.in_code_block:
            # 在代码块内，不处理格式化
            self.code_block_buffer.append(line)
            return line
        else:
            # 不在代码块内，正常处理
            return formatter.format_content(line)


class StreamingFileProcessor:
    """流式文件处理器。

    通过逐行读取和处理文件，减少内存占用，天然避免边界问题。
    支持代码块保护，确保代码内容不被格式化。
    """

    def __init__(self) -> None:
        """初始化流式处理器。"""
        self.formatter = MarkdownFormatter()
        self.code_block_handler = CodeBlockHandler()

    def process_file_stream(self, filepath: str, output_path: str) -> None:
        """流式处理文件并直接写入输出文件。

        Args:
            filepath: 输入文件路径
            output_path: 输出文件路径

        Raises:
            FileNotFoundError: 文件不存在时抛出
            PermissionError: 无读取权限时抛出
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"文件不存在: {filepath}")

        with (
            open(filepath, "r", encoding="utf-8") as input_file,
            open(output_path, "w", encoding="utf-8") as output_file,
        ):
            for line in input_file:
                # 逐行处理，避免边界问题
                processed_line = self.code_block_handler.process_line_with_code_block(
                    line, self.formatter
                )
                output_file.write(processed_line)

    def process_file_generator(self, filepath: str) -> Generator[str, None, None]:
        """生成器方式处理文件，逐行返回结果。

        Args:
            filepath: 要处理的文件路径

        Yields:
            处理后的每一行

        Raises:
            FileNotFoundError: 文件不存在时抛出
            PermissionError: 无读取权限时抛出
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"文件不存在: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                processed_line = self.code_block_handler.process_line_with_code_block(
                    line, self.formatter
                )
                yield processed_line

    def process_file_to_string(self, filepath: str) -> str:
        """流式处理文件并返回完整字符串。

        Args:
            filepath: 要处理的文件路径

        Returns:
            处理后的完整文件内容

        Raises:
            FileNotFoundError: 文件不存在时抛出
            PermissionError: 无读取权限时抛出
        """
        result_lines = []
        for line in self.process_file_generator(filepath):
            result_lines.append(line)
        return "".join(result_lines)

    def get_file_size_mb(self, filepath: str) -> float:
        """获取文件大小（MB）。

        Args:
            filepath: 文件路径

        Returns:
            文件大小（MB）
        """
        return os.path.getsize(filepath) / (1024 * 1024)

    def should_use_streaming_processing(self, filepath: str) -> bool:
        """判断是否应该使用流式处理。

        Args:
            filepath: 文件路径

        Returns:
            如果文件大小超过 10MB 则返回 True
        """
        return self.get_file_size_mb(filepath) > 10.0


def read_markdown_file_stream(filepath: str, output_path: str) -> None:
    """流式处理 Markdown 文件。

    Args:
        filepath: 要处理的文件路径
        output_path: 输出文件路径

    Raises:
        FileNotFoundError: 文件不存在时抛出
        PermissionError: 无读取权限时抛出
    """
    processor = StreamingFileProcessor()
    processor.process_file_stream(filepath, output_path)


def process_markdown_file_stream_to_string(filepath: str) -> str:
    """流式处理 Markdown 文件并返回字符串。

    Args:
        filepath: 要处理的文件路径

    Returns:
        处理后的文件内容

    Raises:
        FileNotFoundError: 文件不存在时抛出
        PermissionError: 无读取权限时抛出
    """
    processor = StreamingFileProcessor()
    return processor.process_file_to_string(filepath)
