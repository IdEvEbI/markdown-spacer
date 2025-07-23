"""
性能报告系统单元测试模块。

测试性能监控、数据收集、报告生成等功能。
"""

import json
import tempfile
import time
from pathlib import Path

from src.utils.performance_decorator import (
    monitor_file_processing,
    monitor_performance,
    with_performance_monitoring,
)
from src.utils.performance_monitor import (
    PerformanceData,
    PerformanceMonitor,
    PerformanceReporter,
    generate_performance_report,
    get_performance_monitor,
    get_performance_stats,
    start_performance_monitoring,
    stop_performance_monitoring,
)


class TestPerformanceData:
    """性能数据测试类。"""

    def test_init(self) -> None:
        """测试初始化。"""
        data = PerformanceData()
        assert data.start_time is None
        assert data.end_time is None
        assert data.execution_time == 0.0
        assert data.memory_start is None
        assert data.memory_end is None
        assert data.memory_peak == 0
        assert data.memory_used == 0.0
        assert data.cpu_usage == []
        assert data.file_size == 0
        assert data.strategy == ""
        assert data.success is False
        assert data.error is None

    def test_to_dict(self) -> None:
        """测试转换为字典。"""
        data = PerformanceData()
        data.start_time = 1000.0
        data.end_time = 1001.0
        data.execution_time = 1.0
        data.memory_used = 10.5
        data.strategy = "test"
        data.success = True

        result = data.to_dict()
        assert result["start_time"] == 1000.0
        assert result["end_time"] == 1001.0
        assert result["execution_time"] == 1.0
        assert result["memory_used"] == 10.5
        assert result["strategy"] == "test"
        assert result["success"] is True

    def test_from_dict(self) -> None:
        """测试从字典创建。"""
        data_dict = {
            "start_time": 1000.0,
            "end_time": 1001.0,
            "execution_time": 1.0,
            "memory_used": 10.5,
            "strategy": "test",
            "success": True,
        }

        data = PerformanceData.from_dict(data_dict)
        assert data.start_time == 1000.0
        assert data.end_time == 1001.0
        assert data.execution_time == 1.0
        assert data.memory_used == 10.5
        assert data.strategy == "test"
        assert data.success is True


class TestPerformanceMonitor:
    """性能监控器测试类。"""

    def test_init(self) -> None:
        """测试初始化。"""
        monitor = PerformanceMonitor()
        assert monitor.current_data is None
        assert monitor.history == []
        assert not monitor.monitoring

    def test_start_monitoring(self) -> None:
        """测试开始监控。"""
        monitor = PerformanceMonitor()
        monitor.start_monitoring(1024, "test")

        assert monitor.monitoring is True
        assert monitor.current_data is not None
        assert monitor.current_data.file_size == 1024
        assert monitor.current_data.strategy == "test"
        assert monitor.current_data.start_time is not None
        assert monitor.current_data.memory_start is not None

    def test_stop_monitoring(self) -> None:
        """测试停止监控。"""
        monitor = PerformanceMonitor()
        monitor.start_monitoring(1024, "test")
        time.sleep(0.1)  # 确保有时间差

        result = monitor.stop_monitoring(success=True)

        assert not monitor.monitoring
        assert result.success is True
        assert result.execution_time > 0
        assert result.memory_used >= 0
        assert len(monitor.history) == 1

    def test_stop_monitoring_with_error(self) -> None:
        """测试停止监控（带错误）。"""
        monitor = PerformanceMonitor()
        monitor.start_monitoring(1024, "test")

        result = monitor.stop_monitoring(success=False, error="test error")

        assert result.success is False
        assert result.error == "test error"

    def test_get_current_stats(self) -> None:
        """测试获取当前统计信息。"""
        monitor = PerformanceMonitor()
        monitor.start_monitoring(1024, "test")

        stats = monitor.get_current_stats()

        assert "elapsed_time" in stats
        assert "current_memory_mb" in stats
        assert "memory_peak_mb" in stats
        assert "file_size_mb" in stats
        assert "strategy" in stats
        assert stats["strategy"] == "test"

    def test_get_history_summary(self) -> None:
        """测试获取历史记录摘要。"""
        monitor = PerformanceMonitor()

        # 添加一些测试数据
        monitor.start_monitoring(1024, "test1")
        monitor.stop_monitoring(success=True)

        monitor.start_monitoring(2048, "test2")
        monitor.stop_monitoring(success=False, error="test error")

        summary = monitor.get_history_summary()

        assert summary["total_runs"] == 2
        assert summary["successful_runs"] == 1
        assert summary["failed_runs"] == 1
        assert summary["success_rate"] == 50.0
        assert summary["avg_execution_time"] > 0

    def test_save_and_load_history(self) -> None:
        """测试保存和加载历史记录。"""
        monitor = PerformanceMonitor()

        # 添加测试数据
        monitor.start_monitoring(1024, "test")
        monitor.stop_monitoring(success=True)

        # 保存历史记录
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            temp_file = f.name

        try:
            monitor.save_history(temp_file)

            # 创建新的监控器并加载历史记录
            new_monitor = PerformanceMonitor()
            new_monitor.load_history(temp_file)

            assert len(new_monitor.history) == 1
            assert new_monitor.history[0].strategy == "test"
            assert new_monitor.history[0].success is True
        finally:
            Path(temp_file).unlink(missing_ok=True)

    def test_clear_history(self) -> None:
        """测试清空历史记录。"""
        monitor = PerformanceMonitor()

        # 添加测试数据
        monitor.start_monitoring(1024, "test")
        monitor.stop_monitoring(success=True)

        assert len(monitor.history) == 1

        monitor.clear_history()
        assert len(monitor.history) == 0


class TestPerformanceReporter:
    """性能报告生成器测试类。"""

    def test_generate_text_report(self) -> None:
        """测试生成文本报告。"""
        monitor = PerformanceMonitor()

        # 添加测试数据
        monitor.start_monitoring(1024, "test1")
        monitor.stop_monitoring(success=True)

        monitor.start_monitoring(2048, "test2")
        monitor.stop_monitoring(success=False, error="test error")

        reporter = PerformanceReporter(monitor)
        report = reporter.generate_text_report()

        assert "性能报告" in report
        assert "总体统计" in report
        assert "性能指标" in report
        assert "最近运行记录" in report
        assert "test1" in report
        assert "test2" in report

    def test_generate_json_report(self) -> None:
        """测试生成 JSON 报告。"""
        monitor = PerformanceMonitor()

        # 添加测试数据
        monitor.start_monitoring(1024, "test")
        monitor.stop_monitoring(success=True)

        reporter = PerformanceReporter(monitor)
        report = reporter.generate_json_report()

        data = json.loads(report)
        assert "timestamp" in data
        assert "summary" in data
        assert "recent_runs" in data
        assert len(data["recent_runs"]) == 1

    def test_save_report(self) -> None:
        """测试保存报告。"""
        monitor = PerformanceMonitor()

        # 添加测试数据
        monitor.start_monitoring(1024, "test")
        monitor.stop_monitoring(success=True)

        reporter = PerformanceReporter(monitor)

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            temp_file = f.name

        try:
            reporter.save_report(temp_file, "text")

            with open(temp_file, "r", encoding="utf-8") as f:
                content = f.read()

            assert "性能报告" in content
            assert "test" in content
        finally:
            Path(temp_file).unlink(missing_ok=True)


class TestPerformanceDecorators:
    """性能监控装饰器测试类。"""

    def test_monitor_performance(self) -> None:
        """测试性能监控装饰器。"""
        # 清空历史记录
        monitor = get_performance_monitor()
        monitor.clear_history()

        @monitor_performance("test_strategy")
        def test_func() -> str:
            time.sleep(0.1)
            return "test"

        result = test_func()
        assert result == "test"

        # 检查监控数据
        assert len(monitor.history) == 1
        assert monitor.history[0].strategy == "test_strategy"
        assert monitor.history[0].success is True

    def test_monitor_file_processing(self) -> None:
        """测试文件处理监控装饰器。"""

        @monitor_file_processing
        def test_file_func(filepath: str) -> str:
            return "processed"

        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test content")
            temp_file = f.name

        try:
            result = test_file_func(temp_file)
            assert result == "processed"

            # 检查监控数据
            monitor = get_performance_monitor()
            assert len(monitor.history) >= 1
            latest = monitor.history[-1]
            assert latest.file_size > 0
            assert latest.strategy in ["normal", "chunked", "streaming"]
        finally:
            Path(temp_file).unlink(missing_ok=True)

    def test_with_performance_monitoring(self) -> None:
        """测试性能监控上下文管理器。"""
        with with_performance_monitoring("context_test") as monitor:
            time.sleep(0.1)
            assert monitor.monitoring is True

        # 检查监控数据
        global_monitor = get_performance_monitor()
        assert len(global_monitor.history) >= 1
        latest = global_monitor.history[-1]
        assert latest.strategy == "context_test"
        assert latest.success is True


class TestGlobalFunctions:
    """全局函数测试类。"""

    def test_start_stop_monitoring(self) -> None:
        """测试开始和停止监控。"""
        start_performance_monitoring(1024, "test")
        time.sleep(0.1)
        result = stop_performance_monitoring(success=True)

        assert result.success is True
        assert result.file_size == 1024
        assert result.strategy == "test"

    def test_get_performance_stats(self) -> None:
        """测试获取性能统计信息。"""
        start_performance_monitoring(1024, "test")
        stats = get_performance_stats()
        stop_performance_monitoring()

        assert "elapsed_time" in stats
        assert "current_memory_mb" in stats
        assert "strategy" in stats

    def test_generate_performance_report(self) -> None:
        """测试生成性能报告。"""
        # 添加测试数据
        start_performance_monitoring(1024, "test")
        stop_performance_monitoring(success=True)

        # 生成文本报告
        text_report = generate_performance_report()
        assert "性能报告" in text_report

        # 生成 JSON 报告
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            temp_file = f.name

        try:
            result = generate_performance_report(temp_file, "json")
            assert "报告已保存到" in result

            with open(temp_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            assert "timestamp" in data
            assert "summary" in data
        finally:
            Path(temp_file).unlink(missing_ok=True)


if __name__ == "__main__":
    # 运行测试
    print("开始性能报告系统测试...")

    # 测试性能监控
    monitor = PerformanceMonitor()
    monitor.start_monitoring(1024, "test")
    time.sleep(0.1)
    result = monitor.stop_monitoring(success=True)
    print(f"性能监控测试: 执行时间 {result.execution_time:.3f}s")

    # 测试报告生成
    reporter = PerformanceReporter(monitor)
    report = reporter.generate_text_report()
    print("性能报告生成测试完成")

    print("性能报告系统测试完成！")
