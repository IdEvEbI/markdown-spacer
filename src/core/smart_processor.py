"""
智能文件处理模块。

本模块提供智能文件处理功能，根据文件大小、内容特征等
自动选择最合适的处理策略（普通处理、分块处理、流式处理）。
"""

import os

from src.core.chunked_processor import ChunkedFileProcessor
from src.core.formatter import MarkdownFormatter
from src.core.streaming_processor import StreamingFileProcessor


class ProcessingStrategy:
    """处理策略枚举。"""

    NORMAL = "normal"  # 普通处理
    CHUNKED = "chunked"  # 分块处理
    STREAMING = "streaming"  # 流式处理


class SmartFileProcessor:
    """智能文件处理器。

    根据文件特征自动选择最合适的处理策略。
    """

    def __init__(self) -> None:
        """初始化智能处理器。"""
        self.formatter = MarkdownFormatter()
        self.chunked_processor = ChunkedFileProcessor()
        self.streaming_processor = StreamingFileProcessor()

        # 处理策略阈值（MB）
        self.normal_threshold = 1.0  # 1MB以下使用普通处理
        self.chunked_threshold = 10.0  # 1-10MB使用分块处理
        # 10MB以上使用流式处理

    def get_file_size_mb(self, filepath: str) -> float:
        """获取文件大小（MB）。

        Args:
            filepath: 文件路径

        Returns:
            文件大小（MB）
        """
        return os.path.getsize(filepath) / (1024 * 1024)

    def select_processing_strategy(self, filepath: str) -> str:
        """选择处理策略。

        Args:
            filepath: 文件路径

        Returns:
            选择的处理策略
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"文件不存在: {filepath}")

        file_size_mb = self.get_file_size_mb(filepath)

        if file_size_mb <= self.normal_threshold:
            return ProcessingStrategy.NORMAL
        elif file_size_mb <= self.chunked_threshold:
            return ProcessingStrategy.CHUNKED
        else:
            return ProcessingStrategy.STREAMING

    def process_file(self, input_path: str, output_path: str) -> dict:
        """智能处理文件。

        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径

        Returns:
            处理结果信息字典
        """
        strategy = self.select_processing_strategy(input_path)
        file_size_mb = self.get_file_size_mb(input_path)

        result = {
            "strategy": strategy,
            "file_size_mb": file_size_mb,
            "success": False,
            "error": None,
        }

        try:
            if strategy == ProcessingStrategy.NORMAL:
                # 普通处理
                with open(input_path, "r", encoding="utf-8") as f:
                    content = f.read()
                formatted_content = self.formatter.format_content(content)
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(formatted_content)

            elif strategy == ProcessingStrategy.CHUNKED:
                # 分块处理
                content = self.chunked_processor.process_file(input_path)
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(content)

            elif strategy == ProcessingStrategy.STREAMING:
                # 流式处理
                self.streaming_processor.process_file_stream(input_path, output_path)

            result["success"] = True

        except Exception as e:
            result["error"] = str(e)

        return result

    def process_file_to_string(self, filepath: str) -> str:
        """智能处理文件并返回字符串。

        Args:
            filepath: 文件路径

        Returns:
            处理后的文件内容
        """
        strategy = self.select_processing_strategy(filepath)

        if strategy == ProcessingStrategy.NORMAL:
            # 普通处理
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            return self.formatter.format_content(content)

        elif strategy == ProcessingStrategy.CHUNKED:
            # 分块处理
            return self.chunked_processor.process_file(filepath)

        elif strategy == ProcessingStrategy.STREAMING:
            # 流式处理
            return self.streaming_processor.process_file_to_string(filepath)

        else:
            raise ValueError(f"未知的处理策略: {strategy}")

    def get_processing_info(self, filepath: str) -> dict:
        """获取文件处理信息。

        Args:
            filepath: 文件路径

        Returns:
            处理信息字典
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"文件不存在: {filepath}")

        strategy = self.select_processing_strategy(filepath)
        file_size_mb = self.get_file_size_mb(filepath)

        info = {
            "filepath": filepath,
            "file_size_mb": file_size_mb,
            "strategy": strategy,
            "thresholds": {
                "normal": self.normal_threshold,
                "chunked": self.chunked_threshold,
                "streaming": "> 10MB",
            },
        }

        # 添加策略说明
        if strategy == ProcessingStrategy.NORMAL:
            info["description"] = "小文件，使用普通处理（内存加载）"
        elif strategy == ProcessingStrategy.CHUNKED:
            info["description"] = "中等文件，使用分块处理（平衡内存和性能）"
        elif strategy == ProcessingStrategy.STREAMING:
            info["description"] = "大文件，使用流式处理（最小内存占用）"

        return info

    def set_thresholds(self, normal_mb: float, chunked_mb: float) -> None:
        """设置处理策略阈值。

        Args:
            normal_mb: 普通处理阈值（MB）
            chunked_mb: 分块处理阈值（MB）
        """
        if normal_mb >= chunked_mb:
            raise ValueError("普通处理阈值必须小于分块处理阈值")

        self.normal_threshold = normal_mb
        self.chunked_threshold = chunked_mb


def process_markdown_file_smart(input_path: str, output_path: str) -> dict:
    """智能处理 Markdown 文件。

    Args:
        input_path: 输入文件路径
        output_path: 输出文件路径

    Returns:
        处理结果信息字典
    """
    processor = SmartFileProcessor()
    return processor.process_file(input_path, output_path)


def process_markdown_file_smart_to_string(filepath: str) -> str:
    """智能处理 Markdown 文件并返回字符串。

    Args:
        filepath: 文件路径

    Returns:
        处理后的文件内容
    """
    processor = SmartFileProcessor()
    return processor.process_file_to_string(filepath)


def get_file_processing_info(filepath: str) -> dict:
    """获取文件处理信息。

    Args:
        filepath: 文件路径

    Returns:
        处理信息字典
    """
    processor = SmartFileProcessor()
    return processor.get_processing_info(filepath)
