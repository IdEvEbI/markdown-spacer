import os
import tempfile

from src.core.file_handler import (
    is_markdown_file,
    read_markdown_file,
    write_markdown_file,
)


def test_is_markdown_file() -> None:
    assert is_markdown_file("test.md")
    assert is_markdown_file("README.markdown")
    assert not is_markdown_file("test.txt")
    assert not is_markdown_file(".md")
    assert not is_markdown_file("testmd")


def test_read_and_write_markdown_file() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "demo.md")
        content = "# Hello\n这是测试内容"
        # 写入
        write_markdown_file(file_path, content)
        # 读取
        read_content = read_markdown_file(file_path)
        assert read_content == content


def test_read_nonexistent_file() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "notfound.md")
        try:
            read_markdown_file(file_path)
        except FileNotFoundError:
            pass
        else:
            assert False, "未抛出 FileNotFoundError"


def test_write_and_read_non_markdown_file() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "notmd.txt")
        content = "not markdown"
        # 写入
        write_markdown_file(file_path, content)
        # 读取
        read_content = read_markdown_file(file_path)
        assert read_content == content
