"""
异常定义模块测试
"""

from src.utils.exceptions import (
    ArgumentError,
    ConfigurationError,
    FileProcessingError,
    FormattingError,
    MarkdownSpacerError,
    ValidationError,
)


class TestExceptions:
    """异常类测试"""

    def test_markdown_spacer_error_inheritance(self) -> None:
        """测试基础异常类继承关系"""
        error = MarkdownSpacerError("测试错误")
        assert isinstance(error, Exception)
        assert str(error) == "测试错误"

    def test_configuration_error_inheritance(self) -> None:
        """测试配置错误异常继承关系"""
        error = ConfigurationError("配置错误")
        assert isinstance(error, MarkdownSpacerError)
        assert str(error) == "配置错误"

    def test_file_processing_error_inheritance(self) -> None:
        """测试文件处理错误异常继承关系"""
        error = FileProcessingError("文件处理错误")
        assert isinstance(error, MarkdownSpacerError)
        assert str(error) == "文件处理错误"

    def test_validation_error_inheritance(self) -> None:
        """测试验证错误异常继承关系"""
        error = ValidationError("验证错误")
        assert isinstance(error, MarkdownSpacerError)
        assert str(error) == "验证错误"

    def test_formatting_error_inheritance(self) -> None:
        """测试格式化错误异常继承关系"""
        error = FormattingError("格式化错误")
        assert isinstance(error, MarkdownSpacerError)
        assert str(error) == "格式化错误"

    def test_argument_error_inheritance(self) -> None:
        """测试参数错误异常继承关系"""
        error = ArgumentError("参数错误")
        assert isinstance(error, MarkdownSpacerError)
        assert str(error) == "参数错误"

    def test_exception_hierarchy(self) -> None:
        """测试异常层次结构"""
        # 验证所有异常都是 MarkdownSpacerError 的子类
        exceptions = [
            ConfigurationError,
            FileProcessingError,
            ValidationError,
            FormattingError,
            ArgumentError,
        ]

        for exception_class in exceptions:
            error = exception_class("测试")
            assert isinstance(error, MarkdownSpacerError)
            assert isinstance(error, Exception)

    def test_exception_with_details(self) -> None:
        """测试异常包含详细信息"""
        error = FileProcessingError("文件不存在", "test.md")
        assert "文件不存在" in str(error)
