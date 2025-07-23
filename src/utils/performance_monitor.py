"""
性能监控模块。

本模块提供 markdown-spacer 工具的性能监控功能，
包括性能数据收集、实时监控、报告生成等。
"""

import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import psutil

try:
    from utils.logger import get_logger
except ImportError:
    from src.utils.logger import get_logger

logger = get_logger(__name__)


class PerformanceData:
    """性能数据类。"""

    def __init__(self) -> None:
        """初始化性能数据。"""
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.execution_time: float = 0.0
        self.memory_start: Optional[int] = None
        self.memory_end: Optional[int] = None
        self.memory_peak: int = 0
        self.memory_used: float = 0.0
        self.cpu_usage: List[float] = []
        self.file_size: int = 0
        self.strategy: str = ""
        self.success: bool = False
        self.error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式。"""
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "execution_time": self.execution_time,
            "memory_start": self.memory_start,
            "memory_end": self.memory_end,
            "memory_peak": self.memory_peak,
            "memory_used": self.memory_used,
            "cpu_usage": self.cpu_usage,
            "file_size": self.file_size,
            "strategy": self.strategy,
            "success": self.success,
            "error": self.error,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PerformanceData":
        """从字典创建性能数据。"""
        perf_data = cls()
        perf_data.start_time = data.get("start_time")
        perf_data.end_time = data.get("end_time")
        perf_data.execution_time = data.get("execution_time", 0.0)
        perf_data.memory_start = data.get("memory_start")
        perf_data.memory_end = data.get("memory_end")
        perf_data.memory_peak = data.get("memory_peak", 0)
        perf_data.memory_used = data.get("memory_used", 0.0)
        perf_data.cpu_usage = data.get("cpu_usage", [])
        perf_data.file_size = data.get("file_size", 0)
        perf_data.strategy = data.get("strategy", "")
        perf_data.success = data.get("success", False)
        perf_data.error = data.get("error")
        return perf_data


class PerformanceMonitor:
    """性能监控器。"""

    def __init__(self) -> None:
        """初始化性能监控器。"""
        self.process = psutil.Process()
        self.current_data: Optional[PerformanceData] = None
        self.history: List[PerformanceData] = []
        self.monitoring = False

    def start_monitoring(self, file_size: int = 0, strategy: str = "") -> None:
        """开始监控。"""
        self.current_data = PerformanceData()
        self.current_data.start_time = time.time()
        self.current_data.memory_start = self.process.memory_info().rss
        self.current_data.file_size = file_size
        self.current_data.strategy = strategy
        self.monitoring = True
        logger.info(f"开始性能监控 - 文件大小: {file_size} bytes, 策略: {strategy}")

    def update_cpu_usage(self) -> None:
        """更新 CPU 使用率。"""
        if self.current_data and self.monitoring:
            try:
                cpu_percent = self.process.cpu_percent()
                self.current_data.cpu_usage.append(cpu_percent)
            except Exception as e:
                logger.warning(f"获取 CPU 使用率失败: {e}")

    def update_memory_peak(self) -> None:
        """更新内存峰值。"""
        if self.current_data and self.monitoring:
            try:
                current_memory = self.process.memory_info().rss
                if current_memory > self.current_data.memory_peak:
                    self.current_data.memory_peak = current_memory
            except Exception as e:
                logger.warning(f"更新内存峰值失败: {e}")

    def stop_monitoring(
        self, success: bool = True, error: Optional[str] = None
    ) -> PerformanceData:
        """停止监控。"""
        if not self.current_data:
            raise RuntimeError("没有正在进行的监控")

        self.current_data.end_time = time.time()
        if self.current_data.start_time is not None:
            self.current_data.execution_time = (
                self.current_data.end_time - self.current_data.start_time
            )
        self.current_data.memory_end = self.process.memory_info().rss
        if (
            self.current_data.memory_start is not None
            and self.current_data.memory_end is not None
        ):
            self.current_data.memory_used = (
                (self.current_data.memory_end - self.current_data.memory_start)
                / 1024
                / 1024
            )
        self.current_data.success = success
        self.current_data.error = error

        # 添加到历史记录
        self.history.append(self.current_data)
        self.monitoring = False

        logger.info(
            f"性能监控结束 - 执行时间: {self.current_data.execution_time:.3f}s, "
            f"内存使用: {self.current_data.memory_used:.2f}MB, "
            f"成功: {success}"
        )

        return self.current_data

    def get_current_stats(self) -> Dict[str, Any]:
        """获取当前统计信息。"""
        if not self.current_data or not self.monitoring:
            return {}

        current_memory = self.process.memory_info().rss
        elapsed_time = 0.0
        if self.current_data.start_time is not None:
            elapsed_time = time.time() - self.current_data.start_time

        return {
            "elapsed_time": elapsed_time,
            "current_memory_mb": current_memory / 1024 / 1024,
            "memory_peak_mb": (self.current_data.memory_peak or 0) / 1024 / 1024,
            "file_size_mb": self.current_data.file_size / 1024 / 1024,
            "strategy": self.current_data.strategy,
        }

    def get_history_summary(self) -> Dict[str, Any]:
        """获取历史记录摘要。"""
        if not self.history:
            return {}

        successful_runs = [data for data in self.history if data.success]
        failed_runs = [data for data in self.history if not data.success]

        if not successful_runs:
            return {
                "total_runs": len(self.history),
                "successful_runs": 0,
                "failed_runs": len(failed_runs),
            }

        avg_execution_time = sum(data.execution_time for data in successful_runs) / len(
            successful_runs
        )
        avg_memory_used = sum(data.memory_used for data in successful_runs) / len(
            successful_runs
        )
        max_memory_peak = (
            max(data.memory_peak for data in successful_runs) / 1024 / 1024
        )

        return {
            "total_runs": len(self.history),
            "successful_runs": len(successful_runs),
            "failed_runs": len(failed_runs),
            "success_rate": len(successful_runs) / len(self.history) * 100,
            "avg_execution_time": avg_execution_time,
            "avg_memory_used": avg_memory_used,
            "max_memory_peak": max_memory_peak,
        }

    def save_history(self, filepath: str) -> None:
        """保存历史记录到文件。"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "history": [data.to_dict() for data in self.history],
            "summary": self.get_history_summary(),
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"性能历史记录已保存到: {filepath}")

    def load_history(self, filepath: str) -> None:
        """从文件加载历史记录。"""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.history = [
            PerformanceData.from_dict(item) for item in data.get("history", [])
        ]
        logger.info(f"性能历史记录已从 {filepath} 加载，共 {len(self.history)} 条记录")

    def clear_history(self) -> None:
        """清空历史记录。"""
        self.history.clear()
        logger.info("性能历史记录已清空")


class PerformanceReporter:
    """性能报告生成器。"""

    def __init__(self, monitor: PerformanceMonitor) -> None:
        """初始化性能报告生成器。"""
        self.monitor = monitor

    def generate_text_report(self) -> str:
        """生成文本格式的性能报告。"""
        summary = self.monitor.get_history_summary()
        if not summary:
            return "暂无性能数据"

        report_lines = [
            "=" * 60,
            "性能报告",
            "=" * 60,
            f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "总体统计:",
            f"  总运行次数: {summary['total_runs']}",
            f"  成功次数: {summary['successful_runs']}",
            f"  失败次数: {summary['failed_runs']}",
            f"  成功率: {summary['success_rate']:.1f}%",
            "",
            "性能指标:",
            f"  平均执行时间: {summary['avg_execution_time']:.3f} 秒",
            f"  平均内存使用: {summary['avg_memory_used']:.2f} MB",
            f"  最大内存峰值: {summary['max_memory_peak']:.2f} MB",
            "",
        ]

        # 添加最近的运行记录
        if self.monitor.history:
            report_lines.extend(
                [
                    "最近运行记录:",
                    "-" * 40,
                ]
            )

            for i, data in enumerate(self.monitor.history[-5:], 1):
                status = "成功" if data.success else "失败"
                report_lines.extend(
                    [
                        f"{i}. 策略: {data.strategy}",
                        f"   执行时间: {data.execution_time:.3f}s",
                        f"   内存使用: {data.memory_used:.2f}MB",
                        f"   状态: {status}",
                        "",
                    ]
                )

        return "\n".join(report_lines)

    def generate_json_report(self) -> str:
        """生成 JSON 格式的性能报告。"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "summary": self.monitor.get_history_summary(),
            "recent_runs": [data.to_dict() for data in self.monitor.history[-10:]],
        }
        return json.dumps(data, indent=2, ensure_ascii=False)

    def save_report(self, filepath: str, format_type: str = "text") -> None:
        """保存性能报告到文件。"""
        if format_type == "json":
            content = self.generate_json_report()
        else:
            content = self.generate_text_report()

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"性能报告已保存到: {filepath}")


# 全局性能监控器实例
_global_monitor = PerformanceMonitor()


def get_performance_monitor() -> PerformanceMonitor:
    """获取全局性能监控器。"""
    return _global_monitor


def start_performance_monitoring(file_size: int = 0, strategy: str = "") -> None:
    """开始性能监控。"""
    _global_monitor.start_monitoring(file_size, strategy)


def stop_performance_monitoring(
    success: bool = True, error: Optional[str] = None
) -> PerformanceData:
    """停止性能监控。"""
    return _global_monitor.stop_monitoring(success, error)


def get_performance_stats() -> Dict[str, Any]:
    """获取性能统计信息。"""
    return _global_monitor.get_current_stats()


def generate_performance_report(
    output_file: Optional[str] = None, format_type: str = "text"
) -> str:
    """生成性能报告。"""
    reporter = PerformanceReporter(_global_monitor)

    if output_file:
        reporter.save_report(output_file, format_type)
        return f"报告已保存到: {output_file}"
    else:
        return reporter.generate_text_report()
