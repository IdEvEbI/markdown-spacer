"""
File handling module for markdown-spacer.
"""

import shutil
from pathlib import Path
from typing import Optional

from .formatter import MarkdownFormatter


class FileHandler:
    """Handle file operations for markdown-spacer."""

    def __init__(self):
        """Initialize the file handler."""
        self.markdown_extensions = {".md", ".markdown"}

    def process_single_file(
        self,
        input_path: Path,
        output_path: Optional[Path] = None,
        formatter: Optional[MarkdownFormatter] = None,
        backup: bool = False,
    ) -> bool:
        """Process a single markdown file.

        Args:
            input_path: Path to input file
            output_path: Path to output file (optional)
            formatter: Formatter instance (optional)
            backup: Whether to create backup

        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate input file
            if not input_path.exists():
                print(f"Error: File not found: {input_path}")
                return False

            if not self._is_markdown_file(input_path):
                print(f"Error: Not a markdown file: {input_path}")
                return False

            # Create formatter if not provided
            if formatter is None:
                formatter = MarkdownFormatter()

            # Read input file
            content = self._read_file(input_path)
            if content is None:
                return False

            # Create backup if requested
            if backup:
                self._create_backup(input_path)

            # Format content
            formatted_content = formatter.format_content(content)

            # Determine output path
            if output_path is None:
                output_path = input_path

            # Write output file
            return self._write_file(output_path, formatted_content)

        except Exception as e:
            print(f"Error processing file {input_path}: {e}")
            return False

    def process_directory(
        self,
        directory_path: Path,
        formatter: Optional[MarkdownFormatter] = None,
        backup: bool = False,
        recursive: bool = False,
    ) -> int:
        """Process all markdown files in a directory.

        Args:
            directory_path: Path to directory
            formatter: Formatter instance (optional)
            backup: Whether to create backups
            recursive: Whether to process subdirectories

        Returns:
            Number of files processed
        """
        if not directory_path.exists():
            print(f"Error: Directory not found: {directory_path}")
            return 0

        if not directory_path.is_dir():
            print(f"Error: Not a directory: {directory_path}")
            return 0

        # Create formatter if not provided
        if formatter is None:
            formatter = MarkdownFormatter()

        processed_count = 0

        # Find markdown files
        if recursive:
            markdown_files = list(directory_path.rglob("*.md")) + list(
                directory_path.rglob("*.markdown")
            )
        else:
            markdown_files = [
                f for f in directory_path.iterdir() if self._is_markdown_file(f)
            ]

        # Process each file
        for file_path in markdown_files:
            if self.process_single_file(file_path, None, formatter, backup):
                processed_count += 1

        return processed_count

    def _is_markdown_file(self, file_path: Path) -> bool:
        """Check if file is a markdown file.

        Args:
            file_path: Path to file

        Returns:
            True if markdown file
        """
        return (
            file_path.is_file() and file_path.suffix.lower() in self.markdown_extensions
        )

    def _read_file(self, file_path: Path) -> Optional[str]:
        """Read file content with UTF-8 encoding.

        Args:
            file_path: Path to file

        Returns:
            File content or None if error
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None

    def _write_file(self, file_path: Path, content: str) -> bool:
        """Write content to file with UTF-8 encoding.

        Args:
            file_path: Path to file
            content: Content to write

        Returns:
            True if successful
        """
        try:
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error writing file {file_path}: {e}")
            return False

    def _create_backup(self, file_path: Path) -> bool:
        """Create backup of file.

        Args:
            file_path: Path to file

        Returns:
            True if successful
        """
        try:
            backup_path = file_path.with_suffix(file_path.suffix + ".bak")
            shutil.copy2(file_path, backup_path)
            return True
        except Exception as e:
            print(f"Error creating backup for {file_path}: {e}")
            return False
