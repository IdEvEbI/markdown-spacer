"""
智能处理器单元测试模块。

测试 SmartFileProcessor 的功能，包括策略选择、文件处理等。
"""

import os
import tempfile

import pytest

from src.core.smart_processor import (
    ProcessingStrategy,
    SmartFileProcessor,
    get_file_processing_info,
    process_markdown_file_smart,
    process_markdown_file_smart_to_string,
)


class TestProcessingStrategy:
    """处理策略测试类。"""

    def test_strategy_constants(self) -> None:
        """测试策略常量。"""
        assert ProcessingStrategy.NORMAL == "normal"
        assert ProcessingStrategy.CHUNKED == "chunked"
        assert ProcessingStrategy.STREAMING == "streaming"


class TestSmartFileProcessor:
    """智能处理器测试类。"""

    def test_init(self) -> None:
        """测试初始化。"""
        processor = SmartFileProcessor()
        assert processor.formatter is not None
        assert processor.chunked_processor is not None
        assert processor.streaming_processor is not None
        assert processor.normal_threshold == 1.0
        assert processor.chunked_threshold == 10.0

    def test_get_file_size_mb(self) -> None:
        """测试文件大小获取。"""
        processor = SmartFileProcessor()

        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("测试内容" * 1000)
            temp_file = f.name

        try:
            size_mb = processor.get_file_size_mb(temp_file)
            assert size_mb > 0
            assert isinstance(size_mb, float)
        finally:
            os.unlink(temp_file)

    def test_select_processing_strategy_small_file(self) -> None:
        """测试小文件策略选择。"""
        processor = SmartFileProcessor()

        # 创建小文件
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("小文件内容")
            temp_file = f.name

        try:
            strategy = processor.select_processing_strategy(temp_file)
            assert strategy == ProcessingStrategy.NORMAL
        finally:
            os.unlink(temp_file)

    def test_select_processing_strategy_medium_file(self) -> None:
        """测试中等文件策略选择。"""
        processor = SmartFileProcessor()

        # 创建中等文件（1-10MB之间）
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("中等文件内容" * 100000)  # 写入大量内容
            temp_file = f.name

        try:
            strategy = processor.select_processing_strategy(temp_file)
            assert strategy == ProcessingStrategy.CHUNKED
        finally:
            os.unlink(temp_file)

    def test_select_processing_strategy_large_file(self) -> None:
        """测试大文件策略选择。"""
        processor = SmartFileProcessor()

        # 创建大文件（>10MB）
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("大文件内容" * 1000000)  # 写入大量内容
            temp_file = f.name

        try:
            strategy = processor.select_processing_strategy(temp_file)
            assert strategy == ProcessingStrategy.STREAMING
        finally:
            os.unlink(temp_file)

    def test_select_processing_strategy_file_not_found(self) -> None:
        """测试文件不存在的情况。"""
        processor = SmartFileProcessor()

        with pytest.raises(FileNotFoundError):
            processor.select_processing_strategy("不存在的文件.md")

    def test_process_file_normal_strategy(self) -> None:
        """测试普通策略文件处理。"""
        processor = SmartFileProcessor()

        # 创建小文件
        test_content = "# 普通处理测试\n\n中文English\n中文123English"

        with (
            tempfile.NamedTemporaryFile(mode="w", delete=False) as input_file,
            tempfile.NamedTemporaryFile(mode="w", delete=False) as output_file,
        ):
            input_file.write(test_content)
            input_file.flush()

            try:
                result = processor.process_file(input_file.name, output_file.name)

                # 验证处理结果
                assert result["success"] is True
                assert result["strategy"] == ProcessingStrategy.NORMAL
                assert result["file_size_mb"] > 0
                assert result["error"] is None

                # 验证输出文件
                with open(output_file.name, "r", encoding="utf-8") as f:
                    output_content = f.read()

                assert "# 普通处理测试" in output_content
                assert "中文 English" in output_content
                assert "中文 123" in output_content
            finally:
                os.unlink(input_file.name)
                os.unlink(output_file.name)

    def test_process_file_to_string_normal_strategy(self) -> None:
        """测试普通策略字符串处理。"""
        processor = SmartFileProcessor()

        # 创建小文件
        test_content = "# 字符串处理测试\n\n中文English\n中文123English"

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write(test_content)
            temp_file = f.name

        try:
            result = processor.process_file_to_string(temp_file)

            # 验证处理结果
            assert "# 字符串处理测试" in result
            assert "中文 English" in result
            assert "中文 123" in result
        finally:
            os.unlink(temp_file)

    def test_get_processing_info(self) -> None:
        """测试获取处理信息。"""
        processor = SmartFileProcessor()

        # 创建小文件
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("测试内容")
            temp_file = f.name

        try:
            info = processor.get_processing_info(temp_file)

            # 验证信息结构
            assert "filepath" in info
            assert "file_size_mb" in info
            assert "strategy" in info
            assert "thresholds" in info
            assert "description" in info

            # 验证值
            assert info["filepath"] == temp_file
            assert info["file_size_mb"] > 0
            assert info["strategy"] == ProcessingStrategy.NORMAL
            assert "normal" in info["thresholds"]
            assert "chunked" in info["thresholds"]
            assert "streaming" in info["thresholds"]
            assert "小文件" in info["description"]
        finally:
            os.unlink(temp_file)

    def test_set_thresholds(self) -> None:
        """测试设置阈值。"""
        processor = SmartFileProcessor()

        # 设置新阈值
        processor.set_thresholds(2.0, 20.0)

        assert processor.normal_threshold == 2.0
        assert processor.chunked_threshold == 20.0

    def test_set_thresholds_invalid(self) -> None:
        """测试设置无效阈值。"""
        processor = SmartFileProcessor()

        # 普通阈值大于分块阈值应该报错
        with pytest.raises(ValueError):
            processor.set_thresholds(10.0, 5.0)


class TestSmartFunctions:
    """智能处理函数测试类。"""

    def test_process_markdown_file_smart(self) -> None:
        """测试智能处理函数。"""
        test_content = "# 智能处理测试\n\n中文English\n中文123English"

        with (
            tempfile.NamedTemporaryFile(mode="w", delete=False) as input_file,
            tempfile.NamedTemporaryFile(mode="w", delete=False) as output_file,
        ):
            input_file.write(test_content)
            input_file.flush()

            try:
                result = process_markdown_file_smart(input_file.name, output_file.name)

                # 验证处理结果
                assert result["success"] is True
                assert result["strategy"] == ProcessingStrategy.NORMAL
                assert result["error"] is None

                # 验证输出文件
                with open(output_file.name, "r", encoding="utf-8") as f:
                    output_content = f.read()

                assert "# 智能处理测试" in output_content
                assert "中文 English" in output_content
            finally:
                os.unlink(input_file.name)
                os.unlink(output_file.name)

    def test_process_markdown_file_smart_to_string(self) -> None:
        """测试智能处理到字符串函数。"""
        test_content = "# 智能字符串测试\n\n中文English\n中文123English"

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write(test_content)
            temp_file = f.name

        try:
            result = process_markdown_file_smart_to_string(temp_file)

            # 验证处理结果
            assert "# 智能字符串测试" in result
            assert "中文 English" in result
            assert "中文 123" in result
        finally:
            os.unlink(temp_file)

    def test_get_file_processing_info(self) -> None:
        """测试获取文件处理信息函数。"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("测试内容")
            temp_file = f.name

        try:
            info = get_file_processing_info(temp_file)

            # 验证信息结构
            assert "filepath" in info
            assert "file_size_mb" in info
            assert "strategy" in info
            assert "thresholds" in info
            assert "description" in info
        finally:
            os.unlink(temp_file)


if __name__ == "__main__":
    # 运行测试
    print("开始智能处理器测试...")

    processor = SmartFileProcessor()
    print(
        f"默认阈值: 普通={processor.normal_threshold}MB, 分块={processor.chunked_threshold}MB"
    )

    # 测试策略选择
    print(
        f"策略常量: {ProcessingStrategy.NORMAL}, "
        f"{ProcessingStrategy.CHUNKED}, {ProcessingStrategy.STREAMING}"
    )

    print("智能处理器测试完成！")
