import os
import tempfile
from pathlib import Path

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


def test_find_markdown_files_recursive(tmp_path: Path) -> None:
    # 创建多层目录和不同类型文件
    d1 = tmp_path / "docs"
    d1.mkdir()
    d2 = d1 / "sub"
    d2.mkdir()
    f1 = d1 / "a.md"
    f2 = d1 / "b.markdown"
    f3 = d2 / "c.md"
    f4 = d2 / "d.txt"
    f1.write_text("A", encoding="utf-8")
    f2.write_text("B", encoding="utf-8")
    f3.write_text("C", encoding="utf-8")
    f4.write_text("D", encoding="utf-8")

    from src.core.file_handler import find_markdown_files

    files = find_markdown_files(str(tmp_path), recursive=True)
    found = sorted(os.path.basename(f) for f in files)
    assert found == ["a.md", "b.markdown", "c.md"]


def test_find_markdown_files_non_recursive(tmp_path: Path) -> None:
    d1 = tmp_path / "docs"
    d1.mkdir()
    d2 = d1 / "sub"
    d2.mkdir()
    f1 = d1 / "a.md"
    f2 = d1 / "b.markdown"
    f3 = d2 / "c.md"
    f1.write_text("A", encoding="utf-8")
    f2.write_text("B", encoding="utf-8")
    f3.write_text("C", encoding="utf-8")

    from src.core.file_handler import find_markdown_files

    files = find_markdown_files(str(d1), recursive=False)
    found = sorted(os.path.basename(f) for f in files)
    assert found == ["a.md", "b.markdown"]


def test_read_markdown_files(tmp_path: Path) -> None:
    f1 = tmp_path / "a.md"
    f2 = tmp_path / "b.markdown"
    f3 = tmp_path / "c.txt"
    f1.write_text("A", encoding="utf-8")
    f2.write_text("B", encoding="utf-8")
    f3.write_text("C", encoding="utf-8")
    from src.core.file_handler import read_markdown_files

    result = read_markdown_files([str(f1), str(f2), str(f3)])
    assert result == {str(f1): "A", str(f2): "B"}


def test_write_markdown_files_and_backup(tmp_path: Path) -> None:
    f1 = tmp_path / "a.md"
    f2 = tmp_path / "b.markdown"
    f1.write_text("oldA", encoding="utf-8")
    f2.write_text("oldB", encoding="utf-8")
    from src.core.file_handler import write_markdown_files

    file_contents = {str(f1): "Anew", str(f2): "Bnew"}
    write_markdown_files(file_contents, backup=True)
    assert f1.read_text(encoding="utf-8") == "Anew"
    assert f2.read_text(encoding="utf-8") == "Bnew"
    # 检查备份文件
    assert (tmp_path / "a.md.bak").read_text(encoding="utf-8") == "oldA"
    assert (tmp_path / "b.markdown.bak").read_text(encoding="utf-8") == "oldB"
