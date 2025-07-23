"""
分块文件处理模块。

本模块提供大文件的分块处理功能，通过将大文件分割成小块进行处理，
减少内存占用，提高处理效率。
"""

import os

from src.core.formatter import MarkdownFormatter


class ChunkedFileProcessor:
    """分块文件处理器。

    将大文件分割成小块进行处理，减少内存占用。
    支持边界处理，确保不会破坏 Markdown 结构。
    """

    def __init__(self, chunk_size: int = 1024 * 1024) -> None:
        """初始化分块处理器。

        Args:
            chunk_size: 分块大小（字节），默认 1MB
        """
        self.chunk_size = chunk_size
        self.formatter = MarkdownFormatter()

    def process_file(self, filepath: str) -> str:
        """分块处理文件，处理边界问题。

        Args:
            filepath: 要处理的文件路径

        Returns:
            处理后的文件内容

        Raises:
            FileNotFoundError: 文件不存在时抛出
            PermissionError: 无读取权限时抛出
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"文件不存在: {filepath}")

        result_lines = []
        chunk_count = 0
        buffer = ""  # 存储未完成的行

        with open(filepath, "r", encoding="utf-8") as f:
            chunk = f.read(self.chunk_size)
            while chunk:
                chunk_count += 1
                is_last = len(chunk) < self.chunk_size  # 最后一块通常小于块大小

                # 处理当前块
                processed_chunk = self._process_chunk_with_boundary(
                    chunk, buffer, is_last
                )
                result_lines.append(processed_chunk["content"])
                buffer = processed_chunk["buffer"]  # 更新缓冲区

                # 读取下一块
                chunk = f.read(self.chunk_size)

        return "".join(result_lines)

    def _process_chunk_with_boundary(
        self, chunk: str, buffer: str, is_last_chunk: bool
    ) -> dict[str, str]:
        """处理带边界的块。

        Args:
            chunk: 当前数据块
            buffer: 上一块的缓冲区内容
            is_last_chunk: 是否为最后一块

        Returns:
            包含处理结果和缓冲区的字典
        """
        # 将缓冲区内容与当前块合并
        full_content = buffer + chunk

        # 按行分割
        lines = full_content.split("\n")

        if is_last_chunk:
            # 最后一块，处理所有行
            processed_lines = []
            for line in lines:
                processed_lines.append(self.formatter.format_content(line))
            return {"content": "\n".join(processed_lines), "buffer": ""}  # 清空缓冲区
        else:
            # 不是最后一块，处理完整行，保留最后一行到缓冲区
            processed_lines = []
            for line in lines[:-1]:  # 除了最后一行
                processed_lines.append(self.formatter.format_content(line))

            return {
                "content": "\n".join(processed_lines),
                "buffer": lines[-1] if lines else "",  # 保存最后一行
            }

    def _process_chunk(
        self, chunk: str, is_first_chunk: bool = True, is_last_chunk: bool = True
    ) -> str:
        """处理单个数据块，处理边界问题。

        Args:
            chunk: 数据块内容
            is_first_chunk: 是否为第一块
            is_last_chunk: 是否为最后一块

        Returns:
            处理后的内容
        """
        lines = chunk.split("\n")
        processed_lines = []

        # 处理完整行（除了最后一行）
        for i, line in enumerate(lines[:-1]):
            processed_lines.append(self.formatter.format_content(line))

        # 处理最后一行（可能不完整）
        if lines:
            last_line = lines[-1]
            if not is_last_chunk:
                # 不是最后一块，保留最后一行不处理
                processed_lines.append(last_line)
            else:
                # 是最后一块，处理最后一行
                processed_lines.append(self.formatter.format_content(last_line))

        return "\n".join(processed_lines)

    def get_file_size_mb(self, filepath: str) -> float:
        """获取文件大小（MB）。

        Args:
            filepath: 文件路径

        Returns:
            文件大小（MB）
        """
        return os.path.getsize(filepath) / (1024 * 1024)

    def should_use_chunked_processing(self, filepath: str) -> bool:
        """判断是否应该使用分块处理。

        Args:
            filepath: 文件路径

        Returns:
            如果文件大小超过 1MB 则返回 True
        """
        return self.get_file_size_mb(filepath) > 1.0


def read_markdown_file_chunked(filepath: str, chunk_size: int = 1024 * 1024) -> str:
    """分块读取 Markdown 文件。

    Args:
        filepath: 要读取的文件路径
        chunk_size: 分块大小（字节），默认 1MB

    Returns:
        处理后的文件内容

    Raises:
        FileNotFoundError: 文件不存在时抛出
        PermissionError: 无读取权限时抛出
    """
    processor = ChunkedFileProcessor(chunk_size)
    return processor.process_file(filepath)
