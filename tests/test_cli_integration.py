import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Generator

import pytest

CLI_PATH = os.path.join(os.path.dirname(__file__), "../src/markdown_spacer.py")


@pytest.fixture
def temp_md_file() -> Generator[Path, None, None]:
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "test.md"
        file_path.write_text("中文English\n", encoding="utf-8")
        yield file_path


@pytest.fixture
def temp_md_dir() -> Generator[Path, None, None]:
    with tempfile.TemporaryDirectory() as tmpdir:
        d = Path(tmpdir)
        (d / "a.md").write_text("# Title\n中文English\n", encoding="utf-8")
        (d / "b.md").write_text("# Title\nEnglish中文\n", encoding="utf-8")
        (d / "notmd.txt").write_text("should not change\n", encoding="utf-8")
        yield d


def run_cli(
    args: list[str], input_data: str | None = None
) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, CLI_PATH] + args
    # 设置 PYTHONPATH 以包含项目根目录
    env = os.environ.copy()
    project_root = os.path.dirname(os.path.dirname(__file__))
    env["PYTHONPATH"] = project_root
    result = subprocess.run(
        cmd, input=input_data, capture_output=True, text=True, env=env
    )
    return result


def test_single_file_format(temp_md_file: Path) -> None:
    result = run_cli([str(temp_md_file)])
    assert result.returncode == 0
    content = temp_md_file.read_text(encoding="utf-8")
    assert "中文 English" in content


def test_directory_recursive(temp_md_dir: Path) -> None:
    result = run_cli([str(temp_md_dir), "-r"])
    assert result.returncode == 0
    time.sleep(0.1)
    a = (temp_md_dir / "a.md").read_text(encoding="utf-8")
    b = (temp_md_dir / "b.md").read_text(encoding="utf-8")
    assert "中文 English" in a
    assert "English 中文" in b
    notmd = (temp_md_dir / "notmd.txt").read_text(encoding="utf-8")
    assert "should not change" in notmd


def test_backup_mode(temp_md_file: Path) -> None:
    result = run_cli([str(temp_md_file), "-b"])
    assert result.returncode == 0
    backup = temp_md_file.with_suffix(".md.bak")
    assert backup.exists()
    assert "中文English" in backup.read_text(encoding="utf-8")


def test_silent_mode(temp_md_file: Path) -> None:
    result = run_cli([str(temp_md_file), "-s"])
    assert result.returncode == 0
    # silent 模式下无 info 输出
    assert result.stdout.strip() == ""


def test_stdin_stdout() -> None:
    input_text = "中文English\n"
    result = run_cli([], input_data=input_text)
    assert result.returncode == 0
    assert "中文 English" in result.stdout


def test_non_markdown_file() -> None:
    with tempfile.NamedTemporaryFile(
        suffix=".txt", mode="w+", encoding="utf-8", delete=False
    ) as f:
        f.write("中文English\n")
        f.flush()
        result = run_cli([f.name])
        assert result.returncode != 0
    os.remove(f.name)
