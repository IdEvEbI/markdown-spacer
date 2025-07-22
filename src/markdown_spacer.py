#!/usr/bin/env python3
"""
markdown-spacer - A Python command-line tool for handling spacing between Chinese,
English, and numbers in Markdown files.

Usage:
    markdown-spacer [OPTIONS] [INPUT]

Examples:
    markdown-spacer input.md
    markdown-spacer -i input.md -o output.md
    markdown-spacer -r docs/
"""

import sys
from pathlib import Path

# Add src to Python path for development
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from cli.parser import parse_arguments
    from core.formatter import MarkdownFormatter
    from utils.logger import setup_logger
except ImportError:
    # Fallback for when running as module
    from src.cli.parser import parse_arguments
    from src.core.formatter import MarkdownFormatter
    from src.utils.logger import setup_logger


def main() -> None:
    """Main entry point for the markdown-spacer tool."""
    try:
        # Parse command line arguments
        args = parse_arguments()

        # Setup logging
        # silent 模式下只输出错误，否则正常输出
        logger = setup_logger(verbose=False)
        if args.silent:
            import logging

            logger.setLevel(logging.ERROR)

        # Initialize formatter
        formatter = MarkdownFormatter(bold_quotes=args.bold_quotes)

        # Process files
        if args.input:
            import os

            from core.file_handler import (
                find_markdown_files,
                is_markdown_file,
                read_markdown_file,
                write_markdown_file,
            )

            input_path = str(args.input)
            logger.debug(f"[调试] 输入路径: {input_path}")
            logger.debug(
                f"[调试] os.path.isfile: {os.path.isfile(input_path)}, os.path.isdir: {os.path.isdir(input_path)}"
            )
            if os.path.isfile(input_path):
                # 单文件处理
                if not is_markdown_file(input_path):
                    logger.error(f"不是合法的 Markdown 文件: {args.input}")
                    raise SystemExit(1)
                try:
                    content = read_markdown_file(input_path)
                    formatted = formatter.format_content(content)
                    output_path = args.output if args.output else args.input
                    if args.backup and os.path.isfile(output_path):
                        backup_path = str(output_path) + ".bak"
                        with (
                            open(output_path, "r", encoding="utf-8") as fsrc,
                            open(backup_path, "w", encoding="utf-8") as fdst,
                        ):
                            fdst.write(fsrc.read())
                    logger.debug(f"[调试] 单文件处理前内容: {content}")
                    logger.debug(f"[调试] 单文件处理后内容: {formatted}")
                    write_markdown_file(str(output_path), formatted)
                    logger.info(f"处理成功: {args.input}")
                except Exception as e:
                    logger.error(f"处理失败: {args.input}, 错误: {e}")
                    raise SystemExit(1)
            elif os.path.isdir(input_path):
                # 目录处理
                files = find_markdown_files(input_path, recursive=args.recursive)
                success, fail = 0, 0
                for f in files:
                    try:
                        content = read_markdown_file(f)
                        formatted = formatter.format_content(content)
                        if content == formatted:
                            logger.error(f"文件未发生格式化变更: {f}")
                            fail += 1
                            continue
                        if args.backup and os.path.isfile(f):
                            backup_path = f + ".bak"
                            with (
                                open(f, "r", encoding="utf-8") as fsrc,
                                open(backup_path, "w", encoding="utf-8") as fdst,
                            ):
                                fdst.write(fsrc.read())
                        logger.debug(f"[调试] 写入格式化内容到: {os.path.abspath(f)}")
                        write_markdown_file(f, formatted)
                        success += 1
                    except Exception as e:
                        logger.error(f"处理失败: {f}, 错误: {e}")
                        fail += 1
                logger.info(f"批量处理完成，共 {len(files)} 个文件，成功 {success}，失败 {fail}")
            else:
                logger.error(f"输入既不是文件也不是目录: {args.input}")
                raise SystemExit(1)
        else:
            # Read from stdin, write to stdout
            if sys.stdin.isatty():
                logger.debug("[调试] 未指定输入且无标准输入，程序将退出")
                logger.error("未指定输入文件、目录，且无标准输入")
                raise SystemExit(1)
            content = sys.stdin.read()
            formatted_content = formatter.format_content(content)
            sys.stdout.write(formatted_content)

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except SystemExit:
        import logging

        logging.getLogger("markdown-spacer").debug("[调试] SystemExit 触发，程序退出")
        raise
    except Exception as e:
        import logging

        logging.getLogger("markdown-spacer").error(f"程序异常: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
