"""
分块处理器单元测试模块。

测试 ChunkedFileProcessor 的功能，包括分块处理、边界处理等。
"""

import os
import tempfile

import pytest

from src.core.chunked_processor import ChunkedFileProcessor, read_markdown_file_chunked


class TestChunkedFileProcessor:
    """分块处理器测试类。"""

    def test_init(self) -> None:
        """测试初始化。"""
        processor = ChunkedFileProcessor()
        assert processor.chunk_size == 1024 * 1024  # 1MB
        assert processor.formatter is not None

        # 测试自定义块大小
        processor = ChunkedFileProcessor(2048 * 1024)  # 2MB
        assert processor.chunk_size == 2048 * 1024

    def test_get_file_size_mb(self) -> None:
        """测试文件大小获取。"""
        processor = ChunkedFileProcessor()

        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("测试内容" * 1000)  # 写入一些内容
            temp_file = f.name

        try:
            size_mb = processor.get_file_size_mb(temp_file)
            assert size_mb > 0
            assert isinstance(size_mb, float)
        finally:
            os.unlink(temp_file)

    def test_should_use_chunked_processing(self) -> None:
        """测试是否应该使用分块处理。"""
        processor = ChunkedFileProcessor()

        # 创建小文件
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("小文件内容")
            small_file = f.name

        # 创建大文件
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("大文件内容" * 100000)  # 写入大量内容
            large_file = f.name

        try:
            # 小文件不应该使用分块处理
            assert not processor.should_use_chunked_processing(small_file)

            # 大文件应该使用分块处理
            assert processor.should_use_chunked_processing(large_file)
        finally:
            os.unlink(small_file)
            os.unlink(large_file)

    def test_process_chunk_with_boundary(self) -> None:
        """测试带边界的块处理。"""
        processor = ChunkedFileProcessor()

        # 测试正常块处理
        chunk = "第一行\n第二行\n第三行"
        result = processor._process_chunk_with_boundary(chunk, "", True)
        assert "第一行" in result["content"]
        assert "第二行" in result["content"]
        assert "第三行" in result["content"]
        assert result["buffer"] == ""

        # 测试非最后一块（保留最后一行到缓冲区）
        result = processor._process_chunk_with_boundary(chunk, "", False)
        assert "第一行" in result["content"]
        assert "第二行" in result["content"]
        assert "第三行" not in result["content"]  # 最后一行应该在缓冲区
        assert result["buffer"] == "第三行"

        # 测试缓冲区处理
        buffer = "上一行的剩余"
        result = processor._process_chunk_with_boundary(chunk, buffer, True)
        assert "上一行的剩余第一行" in result["content"]  # 缓冲区内容被合并

    def test_process_file_not_found(self) -> None:
        """测试文件不存在的情况。"""
        processor = ChunkedFileProcessor()

        with pytest.raises(FileNotFoundError):
            processor.process_file("不存在的文件.md")

    def test_process_invalid_markdown_file(self) -> None:
        """测试无效 Markdown 文件的处理。"""
        processor = ChunkedFileProcessor()

        # 创建无效的 Markdown 文件（不以 # 或 --- 开头）
        test_content = "这是普通文本内容\n中文English\n中文123English"

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write(test_content)
            temp_file = f.name

        try:
            # 由于分块处理器直接处理文件内容，不进行 Markdown 验证
            # 所以这里应该能正常处理，但实际使用时会被 file_handler 过滤掉
            result = processor.process_file(temp_file)

            # 验证处理结果（内容会被格式化）
            assert "中文 English" in result
            assert "中文 123" in result
        finally:
            os.unlink(temp_file)

    def test_process_small_file(self) -> None:
        """测试小文件处理。"""
        processor = ChunkedFileProcessor()

        # 创建有效的 Markdown 测试文件（以 # 开头）
        test_content = "# 测试文档\n\n中文English\n中文123English\n中文-English"

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write(test_content)
            temp_file = f.name

        try:
            result = processor.process_file(temp_file)

            # 验证处理结果
            assert "# 测试文档" in result  # 标题保持不变
            assert "中文 English" in result
            assert "中文 123" in result
            assert "中文 - English" in result
        finally:
            os.unlink(temp_file)

    def test_process_large_file_simulation(self) -> None:
        """测试大文件处理模拟。"""
        processor = ChunkedFileProcessor(chunk_size=50)  # 使用很小的块大小进行测试

        # 创建有效的 Markdown 测试文件（以 # 开头）
        test_content = "# 大文件测试\n\n" + "中文English\n" * 100  # 创建多行内容

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write(test_content)
            temp_file = f.name

        try:
            result = processor.process_file(temp_file)

            # 验证处理结果
            assert "# 大文件测试" in result  # 标题保持不变
            assert "中文 English" in result
            assert result.count("中文 English") == 100  # 应该有100行被处理
        finally:
            os.unlink(temp_file)


class TestReadMarkdownFileChunked:
    """分块读取函数测试类。"""

    def test_read_markdown_file_chunked(self) -> None:
        """测试分块读取函数。"""
        test_content = "# 分块测试\n\n中文English\n中文123English\n中文-English"

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write(test_content)
            temp_file = f.name

        try:
            result = read_markdown_file_chunked(temp_file)

            # 验证处理结果
            assert "# 分块测试" in result  # 标题保持不变
            assert "中文 English" in result
            assert "中文 123" in result
            assert "中文 - English" in result
        finally:
            os.unlink(temp_file)

    def test_read_markdown_file_chunked_custom_size(self) -> None:
        """测试自定义块大小的分块读取。"""
        test_content = "# 自定义大小测试\n\n" + "中文English\n" * 50

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write(test_content)
            temp_file = f.name

        try:
            result = read_markdown_file_chunked(temp_file, chunk_size=100)

            # 验证处理结果
            assert "# 自定义大小测试" in result  # 标题保持不变
            assert "中文 English" in result
            assert result.count("中文 English") == 50
        finally:
            os.unlink(temp_file)


if __name__ == "__main__":
    # 运行测试
    print("开始分块处理器测试...")

    processor = ChunkedFileProcessor()
    print(f"默认块大小: {processor.chunk_size} 字节")

    # 测试文件大小检测
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write("测试内容")
        temp_file = f.name

    try:
        size_mb = processor.get_file_size_mb(temp_file)
        print(f"测试文件大小: {size_mb:.2f} MB")
        print(f"应该使用分块处理: {processor.should_use_chunked_processing(temp_file)}")
    finally:
        os.unlink(temp_file)

    print("分块处理器测试完成！")
