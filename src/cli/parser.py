"""
markdown-spacer 命令行参数解析模块。

本模块负责解析和处理命令行参数，提供用户友好的参数验证和帮助信息。
"""

import argparse
import sys
from pathlib import Path


def parse_arguments() -> argparse.Namespace:
    """解析命令行参数。

    Returns:
        解析后的参数命名空间对象

    Raises:
        SystemExit: 参数错误或用户请求帮助/版本信息时退出程序

    Note:
        支持位置参数和标志参数两种输入方式，
        提供详细的帮助信息和用法示例。
    """
    parser = argparse.ArgumentParser(
        description="A Python command-line tool for handling spacing between Chinese, "
        "English, and numbers in Markdown files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  markdown-spacer input.md
  markdown-spacer -i input.md -o output.md
  markdown-spacer -r docs/
  markdown-spacer -b -q input.md
  markdown-spacer -s input.md
        """,
    )

    # Input/Output arguments (互斥组: 位置参数 input 与 -i/--input)
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument(
        "input", nargs="?", type=Path, help="Input file or directory (default: stdin)"
    )
    input_group.add_argument(
        "-i", "--input", dest="input_opt", type=Path, help="Input file or directory"
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output file (only for single file processing)",
    )

    # Processing options
    parser.add_argument(
        "-r", "--recursive", action="store_true", help="Process directories recursively"
    )
    parser.add_argument(
        "-b",
        "--backup",
        action="store_true",
        help="Create backup files before processing",
    )
    parser.add_argument(
        "-q",
        "--bold-quotes",
        action="store_true",
        help="Make Chinese double quotes content bold",
    )
    parser.add_argument(
        "-s",
        "--silent",
        action="store_true",
        help="Silent mode (suppress normal output, only show errors)",
    )
    parser.add_argument(
        "--performance-report",
        action="store_true",
        help="Generate performance report",
    )
    parser.add_argument(
        "--performance-output",
        type=str,
        help="Performance report output file path",
    )
    parser.add_argument(
        "--performance-format",
        choices=["text", "json"],
        default="text",
        help="Performance report format (default: text)",
    )

    # General options
    parser.add_argument(
        "-v", "--version", action="version", version="markdown-spacer 0.1.0"
    )
    # argparse 默认已支持 -h/--help

    args = parser.parse_args()

    # 参数整合与冲突处理
    # 优先使用 -i/--input，其次位置参数 input
    if getattr(args, "input_opt", None):
        args.input = args.input_opt
    delattr(args, "input_opt")

    # input 必须指定（文件、目录或 stdin），否则报错
    if args.input is None and sys.stdin.isatty():
        parser.error("No input file, directory, or stdin provided.")

    # output 仅支持单文件处理
    if args.output and (not args.input or (args.input and args.input.is_dir())):
        parser.error("--output is only valid when processing a single input file.")

    return args
