"""
文件处理模块集成测试。

测试智能处理器与文件处理模块的集成功能。
"""

import os
import tempfile

from src.core.file_handler import (
    batch_process_markdown_files_smart,
    get_file_processing_info_handler,
    process_markdown_file_smart_handler,
    process_markdown_file_smart_to_string_handler,
)


class TestSmartProcessorIntegration:
    """智能处理器集成测试类。"""

    def test_process_markdown_file_smart_handler(self) -> None:
        """测试智能处理文件处理模块接口。"""
        test_content = "# 集成测试\n\n中文English\n中文123English"

        with (
            tempfile.NamedTemporaryFile(mode="w", delete=False) as input_file,
            tempfile.NamedTemporaryFile(mode="w", delete=False) as output_file,
        ):
            input_file.write(test_content)
            input_file.flush()

            try:
                result = process_markdown_file_smart_handler(
                    input_file.name, output_file.name
                )

                # 验证处理结果
                assert result["success"] is True
                assert result["strategy"] == "normal"
                assert result["file_size_mb"] > 0
                assert result["error"] is None

                # 验证输出文件
                with open(output_file.name, "r", encoding="utf-8") as f:
                    output_content = f.read()

                assert "# 集成测试" in output_content
                assert "中文 English" in output_content
                assert "中文 123" in output_content
            finally:
                os.unlink(input_file.name)
                os.unlink(output_file.name)

    def test_process_markdown_file_smart_to_string_handler(self) -> None:
        """测试智能处理到字符串接口。"""
        test_content = "# 字符串集成测试\n\n中文English\n中文123English"

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
            f.write(test_content)
            temp_file = f.name

        try:
            result = process_markdown_file_smart_to_string_handler(temp_file)

            # 验证处理结果
            assert "# 字符串集成测试" in result
            assert "中文 English" in result
            assert "中文 123" in result
        finally:
            os.unlink(temp_file)

    def test_get_file_processing_info_handler(self) -> None:
        """测试获取文件处理信息接口。"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("测试内容")
            temp_file = f.name

        try:
            info = get_file_processing_info_handler(temp_file)

            # 验证信息结构
            assert "filepath" in info
            assert "file_size_mb" in info
            assert "strategy" in info
            assert "thresholds" in info
            assert "description" in info
        finally:
            os.unlink(temp_file)

    def test_batch_process_markdown_files_smart(self) -> None:
        """测试批量智能处理。"""
        test_contents = [
            "# 批量测试1\n\n中文English",
            "# 批量测试2\n\n中文123English",
            "# 批量测试3\n\n中文-English",
        ]

        temp_files = []
        try:
            # 创建测试文件
            for i, content in enumerate(test_contents):
                with tempfile.NamedTemporaryFile(
                    mode="w", delete=False, suffix=".md"
                ) as f:
                    f.write(content)
                    temp_files.append(f.name)

            # 创建输出目录
            with tempfile.TemporaryDirectory() as output_dir:
                results = batch_process_markdown_files_smart(
                    temp_files, output_dir=output_dir
                )

                # 验证处理结果
                assert len(results) == 3
                for filepath, result in results.items():
                    assert result["success"] is True
                    assert result["strategy"] == "normal"
                    assert result["file_size_mb"] > 0
                    assert result["error"] is None

                # 验证输出文件
                for filepath in temp_files:
                    filename = os.path.basename(filepath)
                    output_path = os.path.join(output_dir, filename)
                    assert os.path.exists(output_path)

                    with open(output_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        # 检查是否包含格式化后的内容
                        assert (
                            "中文 English" in content
                            or "中文 123" in content
                            or "中文 - English" in content
                        )

        finally:
            # 清理临时文件
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)

    def test_batch_process_markdown_files_smart_overwrite(self) -> None:
        """测试批量智能处理覆盖原文件。"""
        test_content = "# 覆盖测试\n\n中文English"

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
            f.write(test_content)
            temp_file = f.name

        try:
            results = batch_process_markdown_files_smart([temp_file])

            # 验证处理结果
            assert len(results) == 1
            result = results[temp_file]
            assert result["success"] is True
            assert result["strategy"] == "normal"

            # 验证文件被覆盖
            with open(temp_file, "r", encoding="utf-8") as f:
                content = f.read()
                assert "# 覆盖测试" in content
                assert "中文 English" in content
        finally:
            os.unlink(temp_file)

    def test_batch_process_markdown_files_smart_with_backup(self) -> None:
        """测试批量智能处理带备份。"""
        test_content = "# 备份测试\n\n中文English"

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
            f.write(test_content)
            temp_file = f.name

        try:
            results = batch_process_markdown_files_smart([temp_file], backup=True)

            # 验证处理结果
            assert len(results) == 1
            result = results[temp_file]
            assert result["success"] is True

            # 验证备份文件存在
            backup_file = temp_file + ".bak"
            assert os.path.exists(backup_file)

            # 验证备份文件内容
            with open(backup_file, "r", encoding="utf-8") as f:
                backup_content = f.read()
                assert "# 备份测试" in backup_content
                assert "中文 English" in backup_content  # 备份的是处理后的内容

            # 验证原文件被处理
            with open(temp_file, "r", encoding="utf-8") as f:
                content = f.read()
                assert "# 备份测试" in content
                assert "中文 English" in content  # 处理后的内容

        finally:
            os.unlink(temp_file)
            backup_file = temp_file + ".bak"
            if os.path.exists(backup_file):
                os.unlink(backup_file)

    def test_batch_process_markdown_files_smart_invalid_file(self) -> None:
        """测试批量智能处理无效文件。"""
        # 创建非 Markdown 文件
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("这不是 Markdown 文件")
            invalid_file = f.name

        try:
            results = batch_process_markdown_files_smart([invalid_file])

            # 验证处理结果
            assert len(results) == 1
            result = results[invalid_file]
            assert result["success"] is False
            assert result["error"] == "不是有效的 Markdown 文件"
            assert result["strategy"] is None
            assert result["file_size_mb"] == 0

        finally:
            os.unlink(invalid_file)

    def test_batch_process_markdown_files_smart_mixed_files(self) -> None:
        """测试批量智能处理混合文件（有效和无效）。"""
        # 创建有效文件
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".md") as f:
            f.write("# 有效文件\n\n中文English")
            valid_file = f.name

        # 创建无效文件
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("无效文件")
            invalid_file = f.name

        try:
            results = batch_process_markdown_files_smart([valid_file, invalid_file])

            # 验证处理结果
            assert len(results) == 2

            # 有效文件应该成功
            valid_result = results[valid_file]
            assert valid_result["success"] is True
            assert valid_result["strategy"] == "normal"

            # 无效文件应该失败
            invalid_result = results[invalid_file]
            assert invalid_result["success"] is False
            assert invalid_result["error"] == "不是有效的 Markdown 文件"

        finally:
            os.unlink(valid_file)
            os.unlink(invalid_file)


if __name__ == "__main__":
    # 运行集成测试
    print("开始文件处理模块集成测试...")

    # 测试智能处理接口
    print("测试智能处理器集成功能...")

    print("文件处理模块集成测试完成！")
