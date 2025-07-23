"""
性能优化功能单元测试模块。

本模块测试 markdown-spacer 工具的各种性能优化措施，
包括正则表达式缓存、列表预分配、合并替换操作等。
"""

from src.core.formatter import MarkdownFormatter
from tests.test_performance import PerformanceBenchmark


class TestFormatterOptimization:
    """格式化器优化测试类。"""

    def test_regex_pattern_caching(self) -> None:
        """测试正则表达式缓存机制。"""
        # 创建第一个实例
        formatter1 = MarkdownFormatter()
        patterns1 = formatter1._patterns

        # 创建第二个实例
        formatter2 = MarkdownFormatter()
        patterns2 = formatter2._patterns

        # 验证两个实例使用相同的缓存模式
        assert patterns1 is patterns2
        assert id(patterns1) == id(patterns2)

        # 验证缓存确实在工作
        assert MarkdownFormatter._cached_patterns is not None
        assert patterns1 is MarkdownFormatter._cached_patterns

    def test_regex_pattern_caching_performance(self) -> None:
        """测试正则表达式缓存性能提升。"""
        benchmark = PerformanceBenchmark()

        # 测试创建多个实例的性能
        def create_multiple_formatters() -> list[MarkdownFormatter]:
            formatters = []
            for _ in range(100):
                formatters.append(MarkdownFormatter())
            return formatters

        # 测量创建时间
        exec_time, formatters = benchmark.measure_execution_time(
            create_multiple_formatters
        )

        # 验证创建时间合理（应该很快，因为有缓存）
        assert exec_time < 1.0  # 100个实例创建应该在1秒内
        assert len(formatters) == 100

        # 验证所有实例使用相同的缓存
        first_patterns = formatters[0]._patterns
        for formatter in formatters:
            assert formatter._patterns is first_patterns

    def test_list_preallocation_optimization(self) -> None:
        """测试列表预分配优化。"""
        # 生成大量测试内容
        large_content = "中文English" * 10000

        formatter = MarkdownFormatter()

        # 测量格式化性能
        benchmark = PerformanceBenchmark()
        exec_time, _ = benchmark.measure_execution_time(
            formatter.format_content, large_content
        )

        # 验证处理时间合理
        assert exec_time < 5.0  # 大文件处理应该在5秒内

        # 验证结果正确
        result = formatter.format_content(large_content)
        assert "中文 English" in result

    def test_merge_replace_operations(self) -> None:
        """测试合并替换操作优化。"""
        # 测试包含多个需要替换的内容
        test_content = "中文English中文123English中文-English"

        formatter = MarkdownFormatter()

        # 测量单次替换操作的性能
        benchmark = PerformanceBenchmark()
        exec_time, result = benchmark.measure_execution_time(
            formatter.format_content, test_content
        )

        # 验证处理时间很快
        assert exec_time < 0.1

        # 验证替换结果正确
        expected_parts = ["中文 English", "中文 123", "English", "中文 - English"]
        for part in expected_parts:
            assert part in result

    def test_streaming_threshold_detection(self) -> None:
        """测试流式处理阈值检测。"""
        # 测试不同大小的内容
        small_content = "中文English" * 100
        large_content = "中文English" * 10000

        formatter = MarkdownFormatter()
        benchmark = PerformanceBenchmark()

        # 测量小文件处理时间
        small_time, _ = benchmark.measure_execution_time(
            formatter.format_content, small_content
        )

        # 测量大文件处理时间
        large_time, _ = benchmark.measure_execution_time(
            formatter.format_content, large_content
        )

        # 验证大文件处理时间合理（不应该线性增长太多）
        assert large_time < small_time * 200  # 大文件不应该比小文件慢200倍以上

    def test_large_file_processing(self) -> None:
        """测试大文件处理性能。"""
        # 创建大文件测试
        large_content = "中文English" * 50000  # 约1MB内容

        formatter = MarkdownFormatter()
        benchmark = PerformanceBenchmark()

        # 测量大文件处理性能
        memory_used, result = benchmark.measure_memory_usage(
            formatter.format_content, large_content
        )

        # 验证内存使用合理（不应该超过100MB）
        assert memory_used < 100.0

        # 验证结果正确
        result = formatter.format_content(large_content)
        assert "中文 English" in result


class TestPerformanceBenchmark:
    """性能基准测试功能验证。"""

    def test_benchmark_formatter_performance(self) -> None:
        """测试格式化器性能基准测试功能。"""
        benchmark = PerformanceBenchmark()
        content_sizes = [100, 1000, 10000]

        results = benchmark.benchmark_formatter_performance(content_sizes)

        # 验证结果结构
        assert "content_sizes" in results
        assert "execution_times" in results
        assert "memory_usages" in results

        # 验证数据完整性
        assert len(results["execution_times"]) == len(content_sizes)
        assert len(results["memory_usages"]) == len(content_sizes)

        # 验证性能数据合理
        for i, time_val in enumerate(results["execution_times"]):
            assert time_val >= 0
            assert time_val < 10.0  # 单个测试不应该超过10秒

        for memory_val in results["memory_usages"]:
            assert memory_val >= 0
            assert memory_val < 100.0  # 内存使用不应该超过100MB

    def test_analyze_performance_bottlenecks(self) -> None:
        """测试性能瓶颈分析功能。"""
        benchmark = PerformanceBenchmark()

        analysis = benchmark.analyze_performance_bottlenecks()

        # 验证分析结果结构
        assert "average_speed_chars_per_second" in analysis
        assert "performance_trend" in analysis
        assert "bottlenecks" in analysis
        assert "recommendations" in analysis

        # 验证数据类型
        assert isinstance(analysis["average_speed_chars_per_second"], (int, float))
        assert analysis["performance_trend"] in ["linear", "non_linear"]
        assert isinstance(analysis["bottlenecks"], list)
        assert isinstance(analysis["recommendations"], list)

        # 验证性能指标合理
        assert analysis["average_speed_chars_per_second"] > 0
        assert len(analysis["recommendations"]) > 0


class TestOptimizationIntegration:
    """优化功能集成测试。"""

    def test_end_to_end_optimization_effect(self) -> None:
        """测试端到端优化效果。"""
        # 创建测试内容
        test_content = "中文English中文123English中文-English" * 1000

        formatter = MarkdownFormatter()
        benchmark = PerformanceBenchmark()

        # 测量优化后的性能
        memory_used, result = benchmark.measure_memory_usage(
            formatter.format_content, test_content
        )

        # 验证性能指标
        assert memory_used < 50.0  # 内存使用应该在50MB内

        # 验证功能正确性
        result = formatter.format_content(test_content)
        assert "中文 English" in result
        assert "中文 123" in result
        assert "中文 - English" in result

    def test_optimization_with_different_content_types(self) -> None:
        """测试不同内容类型的优化效果。"""
        test_cases = [
            ("纯中文", "中文内容测试"),
            ("纯英文", "English content test"),
            ("中英混合", "中文English混合内容"),
            ("数字混合", "中文123English456"),
            ("符号混合", "中文-English+English"),
        ]

        formatter = MarkdownFormatter()
        benchmark = PerformanceBenchmark()

        for content_type, content in test_cases:
            # 测量每种内容类型的处理性能
            exec_time, _ = benchmark.measure_execution_time(
                formatter.format_content, content
            )

            # 验证处理时间合理
            assert exec_time < 0.1  # 每种类型都应该很快处理

            # 验证功能正确性
            result = formatter.format_content(content)
            assert len(result) >= len(content)  # 结果长度应该大于等于原内容

    def test_optimization_under_load(self) -> None:
        """测试负载下的优化效果。"""
        # 模拟高负载情况
        formatter = MarkdownFormatter()
        benchmark = PerformanceBenchmark()

        # 连续处理多个文件
        test_contents = [
            "中文English" * 1000,
            "中文123English" * 1000,
            "中文-English" * 1000,
        ]

        total_time = 0.0
        for content in test_contents:
            exec_time, _ = benchmark.measure_execution_time(
                formatter.format_content, content
            )
            total_time += exec_time

        # 验证总处理时间合理
        assert total_time < 3.0  # 三个文件总处理时间应该在3秒内

        # 验证缓存效果（第二个和第三个文件应该更快）
        assert formatter._patterns is MarkdownFormatter._cached_patterns


if __name__ == "__main__":
    # 运行性能优化测试
    print("开始性能优化测试...")

    # 测试正则表达式缓存
    formatter1 = MarkdownFormatter()
    formatter2 = MarkdownFormatter()
    print(f"正则表达式缓存测试: {formatter1._patterns is formatter2._patterns}")

    # 测试性能基准
    benchmark = PerformanceBenchmark()
    analysis = benchmark.analyze_performance_bottlenecks()
    print(f"性能分析结果: {analysis}")

    print("性能优化测试完成！")
