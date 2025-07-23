"""
性能基准测试模块。

本模块提供 markdown-spacer 工具的性能测试功能，
包括执行时间测量、内存使用监控、性能趋势分析等。
"""

import time
from typing import Any, Callable, Dict, List, Tuple

import psutil

from src.core.file_handler import read_markdown_file, write_markdown_file
from src.core.formatter import MarkdownFormatter


class PerformanceBenchmark:
    """性能基准测试类。

    提供执行时间测量、内存使用监控、性能趋势分析等功能。
    """

    def __init__(self) -> None:
        """初始化性能基准测试器。"""
        self.process = psutil.Process()

    def measure_execution_time(
        self, func: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> Tuple[float, Any]:
        """测量函数执行时间。

        Args:
            func: 要测试的函数
            *args: 函数参数
            **kwargs: 函数关键字参数

        Returns:
            (执行时间秒数, 函数返回值) 的元组
        """
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        return end_time - start_time, result

    def measure_memory_usage(
        self, func: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> Tuple[float, Any]:
        """测量函数内存使用情况。

        Args:
            func: 要测试的函数
            *args: 函数参数
            **kwargs: 函数关键字参数

        Returns:
            (内存使用MB, 函数返回值) 的元组
        """
        start_memory = self.process.memory_info().rss
        result = func(*args, **kwargs)
        end_memory = self.process.memory_info().rss
        memory_used = (end_memory - start_memory) / 1024 / 1024
        return memory_used, result

    def benchmark_formatter_performance(
        self, content_sizes: List[int]
    ) -> Dict[str, Any]:
        """基准测试格式化器性能。

        Args:
            content_sizes: 要测试的内容大小列表（字符数）

        Returns:
            包含执行时间和内存使用的字典
        """
        formatter = MarkdownFormatter()
        execution_times = []
        memory_usages = []

        for size in content_sizes:
            # 生成测试内容
            test_content = self._generate_test_content(size)

            # 测量执行时间
            exec_time, _ = self.measure_execution_time(
                formatter.format_content, test_content
            )
            execution_times.append(exec_time)

            # 测量内存使用
            memory_used, _ = self.measure_memory_usage(
                formatter.format_content, test_content
            )
            memory_usages.append(memory_used)

        return {
            "content_sizes": content_sizes,
            "execution_times": execution_times,
            "memory_usages": memory_usages,
        }

    def benchmark_file_handler_performance(
        self, file_sizes: List[int]
    ) -> Dict[str, Any]:
        """基准测试文件处理器性能。

        Args:
            file_sizes: 要测试的文件大小列表（字符数）

        Returns:
            包含执行时间和内存使用的字典
        """
        execution_times = []
        memory_usages = []

        for size in file_sizes:
            # 创建临时测试文件
            test_file = f"test_performance_{size}.md"
            test_content = self._generate_test_content(size)

            try:
                # 写入测试文件
                write_markdown_file(test_file, test_content)

                # 测量读取时间
                exec_time, _ = self.measure_execution_time(
                    read_markdown_file, test_file
                )
                execution_times.append(exec_time)

                # 测量内存使用
                memory_used, _ = self.measure_memory_usage(
                    read_markdown_file, test_file
                )
                memory_usages.append(memory_used)

            finally:
                # 清理测试文件
                import os

                if os.path.exists(test_file):
                    os.remove(test_file)

        return {
            "file_sizes": file_sizes,
            "execution_times": execution_times,
            "memory_usages": memory_usages,
        }

    def analyze_performance_bottlenecks(self) -> Dict[str, Any]:
        """分析性能瓶颈。

        Returns:
            性能分析结果字典
        """
        # 测试不同大小的内容
        content_sizes = [100, 1000, 10000, 50000]
        formatter_results = self.benchmark_formatter_performance(content_sizes)

        # 分析性能趋势
        times = formatter_results["execution_times"]
        sizes = formatter_results["content_sizes"]

        # 计算平均处理速度（字符/秒）
        avg_speed = sum(
            size / time for size, time in zip(sizes, times) if time > 0
        ) / len(times)

        # 识别性能瓶颈
        bottlenecks = []
        if times[-1] > times[0] * 10:  # 如果大文件处理时间超过小文件的10倍
            bottlenecks.append("大文件处理性能下降")

        if any(memory > 100 for memory in formatter_results["memory_usages"]):
            bottlenecks.append("内存使用过高")

        return {
            "average_speed_chars_per_second": avg_speed,
            "performance_trend": "linear" if len(set(times)) <= 2 else "non_linear",
            "bottlenecks": bottlenecks,
            "recommendations": self._generate_recommendations(bottlenecks),
        }

    def _generate_test_content(self, size: int) -> str:
        """生成测试内容。

        Args:
            size: 内容大小（字符数）

        Returns:
            生成的测试内容
        """
        # 生成包含中英文混合的测试内容
        chinese_chars = "中文测试内容"
        english_chars = "English test content"
        numbers = "1234567890"

        content = ""
        while len(content) < size:
            content += f"{chinese_chars}{english_chars}{numbers}\n"

        return content[:size]

    def _generate_recommendations(self, bottlenecks: List[str]) -> List[str]:
        """根据瓶颈生成优化建议。

        Args:
            bottlenecks: 性能瓶颈列表

        Returns:
            优化建议列表
        """
        recommendations = []

        if "大文件处理性能下降" in bottlenecks:
            recommendations.append("考虑实现流式处理")
            recommendations.append("优化正则表达式性能")

        if "内存使用过高" in bottlenecks:
            recommendations.append("实现内存池管理")
            recommendations.append("优化字符串操作")

        if not bottlenecks:
            recommendations.append("当前性能表现良好")

        return recommendations


# 测试用例
class TestPerformanceBenchmark:
    """性能基准测试用例。"""

    def test_measure_execution_time(self) -> None:
        """测试执行时间测量功能。"""
        benchmark = PerformanceBenchmark()

        def test_func() -> str:
            time.sleep(0.1)
            return "test"

        exec_time, result = benchmark.measure_execution_time(test_func)

        assert exec_time >= 0.1
        assert result == "test"

    def test_measure_memory_usage(self) -> None:
        """测试内存使用测量功能。"""
        benchmark = PerformanceBenchmark()

        def test_func() -> List[int]:
            return [i for i in range(1000)]

        memory_used, result = benchmark.measure_memory_usage(test_func)

        assert memory_used >= 0
        assert len(result) == 1000

    def test_benchmark_formatter_performance(self) -> None:
        """测试格式化器性能基准测试。"""
        benchmark = PerformanceBenchmark()
        content_sizes = [100, 1000]

        results = benchmark.benchmark_formatter_performance(content_sizes)

        assert "content_sizes" in results
        assert "execution_times" in results
        assert "memory_usages" in results
        assert len(results["execution_times"]) == len(content_sizes)
        assert len(results["memory_usages"]) == len(content_sizes)

    def test_analyze_performance_bottlenecks(self) -> None:
        """测试性能瓶颈分析。"""
        benchmark = PerformanceBenchmark()

        analysis = benchmark.analyze_performance_bottlenecks()

        assert "average_speed_chars_per_second" in analysis
        assert "performance_trend" in analysis
        assert "bottlenecks" in analysis
        assert "recommendations" in analysis
        assert isinstance(analysis["bottlenecks"], list)
        assert isinstance(analysis["recommendations"], list)

    def test_generate_test_content(self) -> None:
        """测试测试内容生成。"""
        benchmark = PerformanceBenchmark()

        content = benchmark._generate_test_content(100)

        assert len(content) <= 100
        assert "中文" in content
        assert "English" in content
        assert "123" in content


if __name__ == "__main__":
    # 运行性能基准测试
    benchmark = PerformanceBenchmark()
    print("开始性能基准测试...")

    # 测试格式化器性能
    formatter_results = benchmark.benchmark_formatter_performance([100, 1000, 10000])
    print(f"格式化器性能测试结果: {formatter_results}")

    # 分析性能瓶颈
    analysis = benchmark.analyze_performance_bottlenecks()
    print(f"性能分析结果: {analysis}")

    print("性能基准测试完成！")
