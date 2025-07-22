"""
Core formatting algorithm for markdown-spacer.
"""

import re


class MarkdownFormatter:
    """Core formatter for handling spacing in Markdown content."""

    def __init__(self, bold_quotes: bool = False):
        """Initialize the formatter.

        Args:
            bold_quotes: Whether to make Chinese double quotes content bold
        """
        self.bold_quotes = bold_quotes
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile regex patterns for better performance."""
        # Core spacing patterns
        self.patterns = {
            "chinese_english": re.compile(r"([一-龯])([a-zA-Z])"),
            "english_chinese": re.compile(r"([a-zA-Z])([一-龯])"),
            "chinese_number": re.compile(r"([一-龯])(\d)"),
            "number_chinese": re.compile(r"(\d)([一-龯])"),
            "math_symbols": re.compile(
                r"([\u4e00-\u9fa5a-zA-Z0-9])([+\-/*=<>])([\u4e00-\u9fa5a-zA-Z0-9])"
            ),
            "chinese_quotes": re.compile(r'"(.+?)"'),
            "chinese_version": re.compile(r"v\d+\.\d+\.\d+"),
            "chinese_parentheses": re.compile(
                r"（[a-zA-Z]+）|[a-zA-Z]+（[\u4e00-\u9fa5]+）"
            ),
            "english_hyphen": re.compile(r"([a-zA-Z]+)-([a-zA-Z]+)"),
            "chinese_hyphen": re.compile(r"([\u4e00-\u9fa5]+)-([\u4e00-\u9fa5]+)"),
        }

        # Date patterns (no space)
        self.date_patterns = [
            re.compile(r"\d{4}-\d{1,2}-\d{1,2}"),  # 2025-07-20
            re.compile(r"\d{1,2}-\d{1,2}"),  # 7-20
            re.compile(r"\d{1,2}月\d{1,2}[日号]?"),  # 7月20日
            re.compile(r"\d{4}年\d{1,2}月\d{1,2}[日号]?"),  # 2025年7月20日
        ]

    def format_content(self, content: str) -> str:
        """Format the content by adding appropriate spacing.

        Args:
            content: The content to format

        Returns:
            Formatted content
        """
        # Split content into lines for processing
        lines = content.split("\n")
        formatted_lines = []

        for line in lines:
            formatted_line = self._format_line(line)
            formatted_lines.append(formatted_line)

        return "\n".join(formatted_lines)

    def _format_line(self, line: str) -> str:
        """Format a single line of content.

        Args:
            line: The line to format

        Returns:
            Formatted line
        """
        # Skip if line is in code block or other protected content
        if self._is_protected_content(line):
            return line

        # Apply formatting rules
        formatted = line

        # Basic spacing rules
        formatted = self.patterns["chinese_english"].sub(r"\1 \2", formatted)
        formatted = self.patterns["english_chinese"].sub(r"\1 \2", formatted)
        formatted = self.patterns["chinese_number"].sub(r"\1 \2", formatted)
        formatted = self.patterns["number_chinese"].sub(r"\1 \2", formatted)

        # Math symbols
        formatted = self.patterns["math_symbols"].sub(r"\1 \2 \3", formatted)

        # Chinese quotes (optional bold)
        if self.bold_quotes:
            formatted = self.patterns["chinese_quotes"].sub(r"**\1**", formatted)

        # Chinese hyphens
        formatted = self.patterns["chinese_hyphen"].sub(r"\1 - \2", formatted)

        return formatted

    def _is_protected_content(self, line: str) -> bool:
        """Check if line contains protected content that should not be formatted.

        Args:
            line: The line to check

        Returns:
            True if line contains protected content
        """
        # Code blocks
        if line.startswith("```") or line.startswith("`"):
            return True

        # HTML tags
        if re.search(r"<[^>]+>", line):
            return True

        # Links and images
        if re.search(r"\[.*\]\(.*\)", line) or re.search(r"!\[.*\]\(.*\)", line):
            return True

        # Math blocks
        if re.search(r"\$\$.*\$\$", line) or re.search(r"\$.*\$", line):
            return True

        return False
