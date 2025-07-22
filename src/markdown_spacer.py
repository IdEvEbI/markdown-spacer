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

            if args.input.is_file():
                # 单文件处理
                if not is_markdown_file(str(args.input)):
                    logger.error(f"Not a markdown file: {args.input}")
                    sys.exit(1)
                try:
                    content = read_markdown_file(str(args.input))
                    formatted = formatter.format_content(content)
                    output_path = args.output if args.output else args.input
                    if args.backup and os.path.isfile(output_path):
                        backup_path = str(output_path) + ".bak"
                        with (
                            open(output_path, "r", encoding="utf-8") as fsrc,
                            open(backup_path, "w", encoding="utf-8") as fdst,
                        ):
                            fdst.write(fsrc.read())
                    write_markdown_file(str(output_path), formatted)
                    logger.info(f"Successfully processed: {args.input}")
                except Exception as e:
                    logger.error(f"Failed to process: {args.input}, error: {e}")
                    sys.exit(1)
            elif args.input.is_dir():
                # 目录处理
                files = find_markdown_files(str(args.input), recursive=args.recursive)
                success, fail = 0, 0
                for f in files:
                    try:
                        content = read_markdown_file(f)
                        formatted = formatter.format_content(content)
                        if args.backup and os.path.isfile(f):
                            backup_path = f + ".bak"
                            with (
                                open(f, "r", encoding="utf-8") as fsrc,
                                open(backup_path, "w", encoding="utf-8") as fdst,
                            ):
                                fdst.write(fsrc.read())
                        write_markdown_file(f, formatted)
                        success += 1
                    except Exception as e:
                        logger.error(f"Failed to process: {f}, error: {e}")
                        fail += 1
                logger.info(
                    f"Processed {len(files)} files, success: {success}, fail: {fail}"
                )
            else:
                logger.error(f"Input is neither file nor directory: {args.input}")
                sys.exit(1)
        else:
            # Read from stdin, write to stdout
            content = sys.stdin.read()
            formatted_content = formatter.format_content(content)
            sys.stdout.write(formatted_content)

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
