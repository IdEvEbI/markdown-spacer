"""
Core formatting algorithm for markdown-spacer.
"""

import re
from typing import Dict


class MarkdownFormatter:
    """Core formatter for handling spacing in Markdown content."""

    def __init__(self, bold_quotes: bool = False) -> None:
        """Initialize the formatter.

        Args:
            bold_quotes: Whether to make Chinese double quotes content bold
        """
        self.bold_quotes = bold_quotes
        self._patterns = self._create_patterns()

    def _create_patterns(self) -> Dict[str, re.Pattern]:
        """Create regex patterns for formatting rules.

        Returns:
            Dictionary of compiled regex patterns
        """
        return {
            "chinese_english": re.compile(r"([一-龯])([a-zA-Z])"),
            "english_chinese": re.compile(r"([a-zA-Z])([一-龯])"),
            "chinese_number": re.compile(r"([一-龯])(\d)"),
            "number_chinese": re.compile(r"(\d)([一-龯])"),
            "math_symbols": re.compile(
                r"([\u4e00-\u9fa5a-zA-Z0-9])([+\-/*=<>])([\u4e00-\u9fa5a-zA-Z0-9])"
            ),
            "chinese_quotes": re.compile(r'"(.+?)"'),
            "chinese_hyphen": re.compile(r"([\u4e00-\u9fa5]+)-([\u4e00-\u9fa5]+)"),
        }

    def format_content(self, content: str) -> str:
        """Format the content by adding appropriate spacing.

        Args:
            content: The content to format

        Returns:
            Formatted content
        """
        lines = content.split("\n")
        formatted_lines = [self._format_line(line) for line in lines]
        return "\n".join(formatted_lines)

    def _format_line(self, line: str) -> str:
        """Format a single line of content.

        Args:
            line: The line to format

        Returns:
            Formatted line
        """
        if self._is_protected_content(line):
            return line

        formatted = line

        # Apply spacing rules
        formatted = self._patterns["chinese_english"].sub(r"\1 \2", formatted)
        formatted = self._patterns["english_chinese"].sub(r"\1 \2", formatted)
        formatted = self._patterns["chinese_number"].sub(r"\1 \2", formatted)
        formatted = self._patterns["number_chinese"].sub(r"\1 \2", formatted)

        # Math symbols
        formatted = self._patterns["math_symbols"].sub(r"\1 \2 \3", formatted)

        # Chinese quotes (optional bold)
        if self.bold_quotes:
            formatted = self._patterns["chinese_quotes"].sub(r"**\1**", formatted)

        # Chinese hyphens
        formatted = self._patterns["chinese_hyphen"].sub(r"\1 - \2", formatted)

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
