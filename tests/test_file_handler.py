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
    f1.write_text("# A", encoding="utf-8")
    f2.write_text("# B", encoding="utf-8")
    f3.write_text("# C", encoding="utf-8")
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
    f1.write_text("# A", encoding="utf-8")
    f2.write_text("# B", encoding="utf-8")
    f3.write_text("# C", encoding="utf-8")
    from src.core.file_handler import find_markdown_files

    files = find_markdown_files(str(d1), recursive=False)
    found = sorted(os.path.basename(f) for f in files)
    assert found == ["a.md", "b.markdown"]


def test_read_markdown_files(tmp_path: Path) -> None:
    f1 = tmp_path / "a.md"
    f2 = tmp_path / "b.markdown"
    f3 = tmp_path / "c.txt"
    f1.write_text("# A", encoding="utf-8")
    f2.write_text("# B", encoding="utf-8")
    f3.write_text("C", encoding="utf-8")
    from src.core.file_handler import read_markdown_files

    result = read_markdown_files([str(f1), str(f2), str(f3)])
    assert result == {str(f1): "# A", str(f2): "# B"}


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


def test_read_file_permission_error(tmp_path: Path) -> None:
    f = tmp_path / "no_read.md"
    f.write_text("data", encoding="utf-8")
    f.chmod(0o000)  # 移除所有权限
    from src.core.file_handler import read_markdown_file

    try:
        read_markdown_file(str(f))
    except Exception as e:
        assert isinstance(e, PermissionError)
    else:
        assert False, "未抛出 PermissionError"
    f.chmod(0o644)  # 恢复权限，便于 pytest 清理


def test_write_file_permission_error(tmp_path: Path) -> None:
    d = tmp_path / "readonly"
    d.mkdir()
    f = d / "a.md"
    f.write_text("data", encoding="utf-8")
    d.chmod(0o400)  # 只读目录
    from src.core.file_handler import write_markdown_file

    try:
        write_markdown_file(str(f), "newdata")
    except Exception as e:
        assert isinstance(e, PermissionError)
    else:
        assert False, "未抛出 PermissionError"
    d.chmod(0o755)  # 恢复权限


def test_batch_write_partial_fail(tmp_path: Path) -> None:
    f1 = tmp_path / "a.md"
    f2 = tmp_path / "b.md"
    f1.write_text("A", encoding="utf-8")
    f2.write_text("B", encoding="utf-8")
    f2.chmod(0o400)  # 只读
    from src.core.file_handler import write_markdown_files

    file_contents = {str(f1): "Anew", str(f2): "Bnew"}
    try:
        write_markdown_files(file_contents)
    except Exception:
        pass  # 允许抛出异常
    assert f1.read_text(encoding="utf-8") == "Anew"
    f2.chmod(0o644)


def test_skip_non_markdown_content(tmp_path: Path) -> None:
    # 伪装的二进制文件
    f1 = tmp_path / "fake.md"
    f1.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00")
    # 纯文本但无 Markdown 特征
    f2 = tmp_path / "plain.md"
    f2.write_text("just some text", encoding="utf-8")
    # 空文件
    f3 = tmp_path / "empty.md"
    f3.write_text("", encoding="utf-8")
    # 合法 Markdown 文件
    f4 = tmp_path / "good.md"
    f4.write_text("# 标题\n内容", encoding="utf-8")
    f5 = tmp_path / "yaml.md"
    f5.write_text("---\ntitle: demo\n---\n正文", encoding="utf-8")
    from src.core.file_handler import is_valid_markdown_content

    assert not is_valid_markdown_content(str(f1))
    assert not is_valid_markdown_content(str(f2))
    assert not is_valid_markdown_content(str(f3))
    assert is_valid_markdown_content(str(f4))
    assert is_valid_markdown_content(str(f5))
