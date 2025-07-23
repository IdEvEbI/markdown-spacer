"""
性能监控装饰器模块。

本模块提供性能监控装饰器，方便在函数上添加性能监控功能。
"""

import functools
import os
from typing import Any, Callable

from src.utils.performance_monitor import (
    get_performance_monitor,
    start_performance_monitoring,
    stop_performance_monitoring,
)


def monitor_performance(strategy: str = "unknown") -> Callable:
    """性能监控装饰器。

    Args:
        strategy: 处理策略名称

    Returns:
        装饰器函数
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # 获取文件大小（如果第一个参数是文件路径）
            file_size = 0
            if args and isinstance(args[0], str) and os.path.exists(args[0]):
                try:
                    file_size = os.path.getsize(args[0])
                except OSError:
                    pass

            # 开始监控
            start_performance_monitoring(file_size, strategy)

            try:
                # 执行原函数
                result = func(*args, **kwargs)
                # 停止监控（成功）
                stop_performance_monitoring(success=True)
                return result
            except Exception as e:
                # 停止监控（失败）
                stop_performance_monitoring(success=False, error=str(e))
                raise

        return wrapper

    return decorator


def monitor_file_processing(func: Callable[..., Any]) -> Callable[..., Any]:
    """文件处理性能监控装饰器。

    自动检测文件大小并使用合适的策略名称。
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # 获取文件大小
        file_size = 0
        filepath = None

        # 查找文件路径参数
        for arg in args:
            if isinstance(arg, str) and os.path.exists(arg):
                filepath = arg
                break

        if not filepath:
            for value in kwargs.values():
                if isinstance(value, str) and os.path.exists(value):
                    filepath = value
                    break

        if filepath:
            try:
                file_size = os.path.getsize(filepath)
            except OSError:
                pass

        # 根据文件大小确定策略
        if file_size < 1024 * 1024:  # < 1MB
            strategy = "normal"
        elif file_size < 10 * 1024 * 1024:  # < 10MB
            strategy = "chunked"
        else:  # >= 10MB
            strategy = "streaming"

        # 开始监控
        start_performance_monitoring(file_size, strategy)

        try:
            # 执行原函数
            result = func(*args, **kwargs)
            # 停止监控（成功）
            stop_performance_monitoring(success=True)
            return result
        except Exception as e:
            # 停止监控（失败）
            stop_performance_monitoring(success=False, error=str(e))
            raise

    return wrapper


def monitor_batch_processing(func: Callable[..., Any]) -> Callable[..., Any]:
    """批量处理性能监控装饰器。"""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # 获取文件列表
        filepaths = []
        for arg in args:
            if isinstance(arg, list):
                filepaths = arg
                break

        if not filepaths:
            for value in kwargs.values():
                if isinstance(value, list):
                    filepaths = value
                    break

        # 计算总文件大小
        total_size = 0
        for filepath in filepaths:
            if isinstance(filepath, str) and os.path.exists(filepath):
                try:
                    total_size += os.path.getsize(filepath)
                except OSError:
                    pass

        # 开始监控
        start_performance_monitoring(total_size, "batch")

        try:
            # 执行原函数
            result = func(*args, **kwargs)
            # 停止监控（成功）
            stop_performance_monitoring(success=True)
            return result
        except Exception as e:
            # 停止监控（失败）
            stop_performance_monitoring(success=False, error=str(e))
            raise

    return wrapper


class PerformanceContext:
    """性能监控上下文管理器。"""

    def __init__(self, strategy: str = "manual"):
        self.strategy = strategy
        self.monitor = get_performance_monitor()

    def __enter__(self) -> Any:
        self.monitor.start_monitoring(strategy=self.strategy)
        return self.monitor

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        success = exc_type is None
        error = str(exc_val) if exc_val else None
        self.monitor.stop_monitoring(success=success, error=error)


def with_performance_monitoring(strategy: str = "manual") -> PerformanceContext:
    """性能监控上下文管理器。"""
    return PerformanceContext(strategy)
