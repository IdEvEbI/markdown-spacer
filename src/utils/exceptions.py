"""
项目异常定义模块
"""


class MarkdownSpacerError(Exception):
    """markdown-spacer 基础异常类"""

    pass


class ConfigurationError(MarkdownSpacerError):
    """配置错误异常"""

    pass


class FileProcessingError(MarkdownSpacerError):
    """文件处理错误异常"""

    pass


class ValidationError(MarkdownSpacerError):
    """验证错误异常"""

    pass


class FormattingError(MarkdownSpacerError):
    """格式化错误异常"""

    pass


class ArgumentError(MarkdownSpacerError):
    """参数错误异常"""

    pass
