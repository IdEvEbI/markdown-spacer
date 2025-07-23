"""
流式处理器单元测试模块。

测试 StreamingFileProcessor 和 CodeBlockHandler 的功能，
包括流式处理、代码块保护等。
"""

import os
import tempfile

import pytest

from src.core.streaming_processor import (
    CodeBlockHandler,
    StreamingFileProcessor,
    process_markdown_file_stream_to_string,
    read_markdown_file_stream,
)


class TestCodeBlockHandler:
    """代码块处理器测试类。"""

    def test_init(self) -> None:
        """测试初始化。"""
        handler = CodeBlockHandler()
        assert not handler.in_code_block
        assert handler.code_block_buffer == []

    def test_process_normal_line(self) -> None:
        """测试处理普通行。"""
        handler = CodeBlockHandler()
        formatter = None  # 这里我们只测试代码块逻辑，不实际格式化

        # 使用真实的 MarkdownFormatter
        from src.core.formatter import MarkdownFormatter

        formatter = MarkdownFormatter()

        # 测试普通行处理
        result = handler.process_line_with_code_block("中文English", formatter)
        assert result == "中文 English"

    def test_process_code_block_start(self) -> None:
        """测试代码块开始。"""
        handler = CodeBlockHandler()
        from src.core.formatter import MarkdownFormatter

        formatter = MarkdownFormatter()

        # 测试代码块开始
        result = handler.process_line_with_code_block("```python", formatter)
        assert result == "```python"
        assert handler.in_code_block
        assert handler.code_block_buffer == ["```python"]

    def test_process_code_block_content(self) -> None:
        """测试代码块内容。"""
        handler = CodeBlockHandler()
        from src.core.formatter import MarkdownFormatter

        formatter = MarkdownFormatter()

        # 开始代码块
        handler.process_line_with_code_block("```python", formatter)

        # 测试代码块内容（不应该被格式化）
        result = handler.process_line_with_code_block("print('中文English')", formatter)
        assert result == "print('中文English')"  # 内容保持不变
        assert handler.in_code_block

    def test_process_code_block_end(self) -> None:
        """测试代码块结束。"""
        handler = CodeBlockHandler()
        from src.core.formatter import MarkdownFormatter

        formatter = MarkdownFormatter()

        # 开始代码块
        handler.process_line_with_code_block("```python", formatter)
        handler.process_line_with_code_block("print('hello')", formatter)

        # 结束代码块
        result = handler.process_line_with_code_block("```", formatter)
        assert "```python" in result
        assert "print('hello')" in result
        assert "```" in result
        assert not handler.in_code_block


class TestStreamingFileProcessor:
    """流式处理器测试类。"""

    def test_init(self) -> None:
        """测试初始化。"""
        processor = StreamingFileProcessor()
        assert processor.formatter is not None
        assert processor.code_block_handler is not None

    def test_get_file_size_mb(self) -> None:
        """测试文件大小获取。"""
        processor = StreamingFileProcessor()

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

    def test_should_use_streaming_processing(self) -> None:
        """测试是否应该使用流式处理。"""
        processor = StreamingFileProcessor()

        # 创建小文件
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("小文件内容")
            small_file = f.name

        # 创建大文件
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("大文件内容" * 1000000)  # 写入大量内容
            large_file = f.name

        try:
            # 小文件不应该使用流式处理
            assert not processor.should_use_streaming_processing(small_file)

            # 大文件应该使用流式处理
            assert processor.should_use_streaming_processing(large_file)
        finally:
            os.unlink(small_file)
            os.unlink(large_file)

    def test_process_file_to_string(self) -> None:
        """测试流式处理文件到字符串。"""
        processor = StreamingFileProcessor()

        # 创建有效的 Markdown 测试文件
        test_content = "# 流式测试\n\n中文English\n中文123English\n中文-English"

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write(test_content)
            temp_file = f.name

        try:
            result = processor.process_file_to_string(temp_file)

            # 验证处理结果
            assert "# 流式测试" in result
            assert "中文 English" in result
            assert "中文 123" in result
            assert "中文 - English" in result
        finally:
            os.unlink(temp_file)

    def test_process_file_with_code_blocks(self) -> None:
        """测试包含代码块的文件处理。"""
        processor = StreamingFileProcessor()

        # 创建包含代码块的测试文件
        test_content = """# 代码块测试

这是普通文本，中文English应该被格式化。

```python
print('中文English')  # 这行不应该被格式化
print('hello world')
```

这是代码块后的文本，中文123English也应该被格式化。
"""

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write(test_content)
            temp_file = f.name

        try:
            result = processor.process_file_to_string(temp_file)

            # 验证处理结果
            assert "# 代码块测试" in result
            assert "中文 English" in result  # 普通文本被格式化
            assert "中文 123" in result  # 普通文本被格式化
            assert "print('中文English')" in result  # 代码块内容不被格式化
            assert "```python" in result  # 代码块标记存在
        finally:
            os.unlink(temp_file)

    def test_process_file_stream(self) -> None:
        """测试流式处理文件到输出文件。"""
        processor = StreamingFileProcessor()

        # 创建测试文件
        test_content = "# 流式输出测试\n\n中文English\n中文123English"

        with (
            tempfile.NamedTemporaryFile(mode="w", delete=False) as input_file,
            tempfile.NamedTemporaryFile(mode="w", delete=False) as output_file,
        ):
            input_file.write(test_content)
            input_file.flush()

            try:
                # 流式处理
                processor.process_file_stream(input_file.name, output_file.name)

                # 读取输出文件
                with open(output_file.name, "r", encoding="utf-8") as f:
                    result = f.read()

                # 验证处理结果
                assert "# 流式输出测试" in result
                assert "中文 English" in result
                assert "中文 123" in result
            finally:
                os.unlink(input_file.name)
                os.unlink(output_file.name)

    def test_process_file_generator(self) -> None:
        """测试生成器方式处理文件。"""
        processor = StreamingFileProcessor()

        # 创建测试文件
        test_content = "# 生成器测试\n\n中文English\n中文123English"

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write(test_content)
            temp_file = f.name

        try:
            # 使用生成器处理
            lines = list(processor.process_file_generator(temp_file))

            # 验证结果
            assert len(lines) == 4  # 4行内容
            assert any("# 生成器测试" in line for line in lines)
            assert any("中文 English" in line for line in lines)
            assert any("中文 123" in line for line in lines)
        finally:
            os.unlink(temp_file)

    def test_process_file_not_found(self) -> None:
        """测试文件不存在的情况。"""
        processor = StreamingFileProcessor()

        with pytest.raises(FileNotFoundError):
            processor.process_file_to_string("不存在的文件.md")


class TestStreamingFunctions:
    """流式处理函数测试类。"""

    def test_read_markdown_file_stream(self) -> None:
        """测试流式读取函数。"""
        test_content = "# 函数测试\n\n中文English\n中文123English"

        with (
            tempfile.NamedTemporaryFile(mode="w", delete=False) as input_file,
            tempfile.NamedTemporaryFile(mode="w", delete=False) as output_file,
        ):
            input_file.write(test_content)
            input_file.flush()

            try:
                # 流式处理
                read_markdown_file_stream(input_file.name, output_file.name)

                # 读取输出文件
                with open(output_file.name, "r", encoding="utf-8") as f:
                    result = f.read()

                # 验证处理结果
                assert "# 函数测试" in result
                assert "中文 English" in result
                assert "中文 123" in result
            finally:
                os.unlink(input_file.name)
                os.unlink(output_file.name)

    def test_process_markdown_file_stream_to_string(self) -> None:
        """测试流式处理到字符串函数。"""
        test_content = "# 字符串测试\n\n中文English\n中文123English"

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write(test_content)
            temp_file = f.name

        try:
            result = process_markdown_file_stream_to_string(temp_file)

            # 验证处理结果
            assert "# 字符串测试" in result
            assert "中文 English" in result
            assert "中文 123" in result
        finally:
            os.unlink(temp_file)


if __name__ == "__main__":
    # 运行测试
    print("开始流式处理器测试...")

    processor = StreamingFileProcessor()
    print(f"流式处理阈值: {processor.should_use_streaming_processing.__defaults__}")

    # 测试代码块处理器
    handler = CodeBlockHandler()
    print(f"代码块处理器初始化: {not handler.in_code_block}")

    print("流式处理器测试完成！")
