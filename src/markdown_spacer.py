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
    from core.file_handler import FileHandler
    from core.formatter import MarkdownFormatter
    from utils.logger import setup_logger
except ImportError:
    # Fallback for when running as module
    from src.cli.parser import parse_arguments
    from src.core.file_handler import FileHandler
    from src.core.formatter import MarkdownFormatter
    from src.utils.logger import setup_logger


def main() -> None:
    """Main entry point for the markdown-spacer tool."""
    try:
        # Parse command line arguments
        args = parse_arguments()

        # Setup logging
        logger = setup_logger(args.verbose)

        # Initialize formatter and file handler
        formatter = MarkdownFormatter(bold_quotes=args.bold_quotes)
        file_handler = FileHandler()

        # Process files
        if args.input:
            if args.input.is_file():
                # Single file processing
                result = file_handler.process_single_file(
                    args.input, args.output, formatter, args.backup
                )
                if result:
                    logger.info(f"Successfully processed: {args.input}")
                else:
                    logger.error(f"Failed to process: {args.input}")
                    sys.exit(1)
            else:
                # Directory processing
                processed_count = file_handler.process_directory(
                    args.input, formatter, args.backup, args.recursive
                )
                logger.info(f"Processed {processed_count} files")
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
