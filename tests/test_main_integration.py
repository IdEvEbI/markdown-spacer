"""
主程序集成测试 - 覆盖 markdown_spacer.py 中的未覆盖代码路径
"""

import os
import tempfile
from unittest.mock import patch

import pytest

from src.markdown_spacer import main


class TestMainIntegration:
    """主程序集成测试"""

    def test_main_with_non_markdown_file(self) -> None:
        """测试处理非 Markdown 文件"""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            non_md_file = f.name
            f.write(b"This is not a markdown file")

        try:
            with patch("sys.argv", ["markdown_spacer", non_md_file]):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 1
        finally:
            os.unlink(non_md_file)

    def test_main_with_nonexistent_path(self) -> None:
        """测试处理不存在的路径"""
        with patch("sys.argv", ["markdown_spacer", "/nonexistent/path"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    def test_main_with_invalid_input_type(self) -> None:
        """测试处理既不是文件也不是目录的输入"""
        # 创建一个文件，然后删除它，但保留路径
        with tempfile.NamedTemporaryFile(delete=False) as f:
            invalid_path = f.name
        os.unlink(invalid_path)

        with patch("sys.argv", ["markdown_spacer", invalid_path]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    def test_main_with_no_input_and_no_stdin(self) -> None:
        """测试无输入且无标准输入的情况"""
        with patch("sys.argv", ["markdown_spacer"]):
            with patch("sys.stdin.isatty", return_value=True):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 2  # argparse 返回 2 表示参数错误

    def test_main_with_stdin_input(self) -> None:
        """测试从标准输入读取内容"""
        test_content = "中文English\n"
        expected_output = "中文 English\n"

        with patch("sys.argv", ["markdown_spacer"]):
            with patch("sys.stdin.isatty", return_value=False):
                with patch("sys.stdin.read", return_value=test_content):
                    with patch("sys.stdout.write") as mock_write:
                        main()
                        mock_write.assert_called_once_with(expected_output)

    def test_main_with_keyboard_interrupt(self) -> None:
        """测试键盘中断处理"""
        with patch("sys.argv", ["markdown_spacer", "test.md"]):
            with patch("src.cli.parser.parse_arguments", side_effect=KeyboardInterrupt):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 1

    def test_main_with_general_exception(self) -> None:
        """测试一般异常处理"""
        with patch("sys.argv", ["markdown_spacer", "test.md"]):
            with patch(
                "src.cli.parser.parse_arguments", side_effect=Exception("Test error")
            ):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 1

    def test_main_with_silent_mode(self) -> None:
        """测试静默模式"""
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
            md_file = f.name
            f.write("中文English\n".encode("utf-8"))

        try:
            with patch("sys.argv", ["markdown_spacer", "-s", md_file]):
                main()  # 应该成功执行，无输出
        finally:
            os.unlink(md_file)

    def test_main_with_backup_mode(self) -> None:
        """测试备份模式"""
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
            md_file = f.name
            f.write("中文English\n".encode("utf-8"))

        try:
            with patch("sys.argv", ["markdown_spacer", "-b", md_file]):
                main()
                # 检查备份文件是否创建
                backup_file = md_file + ".bak"
                assert os.path.exists(backup_file)
                os.unlink(backup_file)
        finally:
            os.unlink(md_file)

    def test_main_with_directory_and_recursive(self) -> None:
        """测试目录递归处理"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建测试目录结构
            sub_dir = os.path.join(temp_dir, "subdir")
            os.makedirs(sub_dir)

            # 创建测试文件
            file1 = os.path.join(temp_dir, "test1.md")
            file2 = os.path.join(sub_dir, "test2.md")

            with open(file1, "w", encoding="utf-8") as f:
                f.write("中文English\n")
            with open(file2, "w", encoding="utf-8") as f:
                f.write("中文English\n")

            with patch("sys.argv", ["markdown_spacer", "-r", temp_dir]):
                main()

    def test_main_with_output_specified(self) -> None:
        """测试指定输出文件"""
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as input_file:
            input_file.write("中文English\n".encode("utf-8"))
            input_path = input_file.name

        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as output_file:
            output_path = output_file.name
            os.unlink(output_path)  # 删除文件，让程序创建

        try:
            with patch("sys.argv", ["markdown_spacer", input_path, "-o", output_path]):
                main()
                assert os.path.exists(output_path)
        finally:
            os.unlink(input_path)
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_main_with_bold_quotes_option(self) -> None:
        """测试双引号加粗选项"""
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
            md_file = f.name
            # 第一行必须是有效的 YAML 或标题，否则会被跳过
            f.write("# 测试文档\n\n“重要内容”\n".encode("utf-8"))

        try:
            with patch("sys.argv", ["markdown_spacer", "-q", md_file]):
                main()
                # 检查文件是否被修改
                with open(md_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    assert "**重要内容**" in content
        finally:
            os.unlink(md_file)
