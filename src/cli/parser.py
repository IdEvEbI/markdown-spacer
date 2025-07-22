"""
Command line argument parser for markdown-spacer.
"""

import argparse
from pathlib import Path


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
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
        """,
    )

    # Input/Output arguments
    parser.add_argument(
        "input", nargs="?", type=Path, help="Input file or directory (default: stdin)"
    )
    parser.add_argument("-i", "--input", type=Path, help="Input file or directory")
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

    # General options
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )
    parser.add_argument("--version", action="version", version="markdown-spacer 0.1.0")

    args = parser.parse_args()

    # Handle input argument conflicts
    if args.input and parser.get_default("input"):
        parser.error("Cannot specify input file twice")

    # Use positional argument if no -i specified
    if not args.input and parser.get_default("input"):
        args.input = parser.get_default("input")

    return args
