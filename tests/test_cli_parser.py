# 动态导入 parser
import importlib.util
import os
import sys
from pathlib import Path
from types import ModuleType

import pytest
from _pytest.monkeypatch import MonkeyPatch

spec = importlib.util.spec_from_file_location(
    "parser", os.path.join(os.path.dirname(__file__), "../src/cli/parser.py")
)
assert spec is not None and spec.loader is not None, "Failed to load parser.py spec"
parser_mod: ModuleType = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parser_mod)  # type: ignore
parse_arguments = parser_mod.parse_arguments


def test_input_positional_and_flag_mutually_exclusive(monkeypatch: MonkeyPatch) -> None:
    test_args = ["prog", "file1.md", "-i", "file2.md"]
    monkeypatch.setattr(sys, "argv", test_args)
    with pytest.raises(SystemExit):
        parse_arguments()


def test_input_positional(monkeypatch: MonkeyPatch) -> None:
    test_args = ["prog", "file1.md"]
    monkeypatch.setattr(sys, "argv", test_args)
    args = parse_arguments()
    assert args.input == Path("file1.md")


def test_input_flag(monkeypatch: MonkeyPatch) -> None:
    test_args = ["prog", "-i", "file2.md"]
    monkeypatch.setattr(sys, "argv", test_args)
    args = parse_arguments()
    assert args.input == Path("file2.md")


def test_output(monkeypatch: MonkeyPatch) -> None:
    test_args = ["prog", "file1.md", "-o", "out.md"]
    monkeypatch.setattr(sys, "argv", test_args)
    args = parse_arguments()
    assert args.output == Path("out.md")


def test_recursive(monkeypatch: MonkeyPatch) -> None:
    test_args = ["prog", "file1.md", "-r"]
    monkeypatch.setattr(sys, "argv", test_args)
    args = parse_arguments()
    assert args.recursive is True


def test_backup(monkeypatch: MonkeyPatch) -> None:
    test_args = ["prog", "file1.md", "-b"]
    monkeypatch.setattr(sys, "argv", test_args)
    args = parse_arguments()
    assert args.backup is True


def test_bold_quotes(monkeypatch: MonkeyPatch) -> None:
    test_args = ["prog", "file1.md", "-q"]
    monkeypatch.setattr(sys, "argv", test_args)
    args = parse_arguments()
    assert args.bold_quotes is True


def test_silent(monkeypatch: MonkeyPatch) -> None:
    test_args = ["prog", "file1.md", "-s"]
    monkeypatch.setattr(sys, "argv", test_args)
    args = parse_arguments()
    assert args.silent is True


def test_output_only_for_file(monkeypatch: MonkeyPatch) -> None:
    test_args = ["prog", "-o", "out.md"]
    monkeypatch.setattr(sys, "argv", test_args)
    with pytest.raises(SystemExit):
        parse_arguments()


def test_no_input_and_no_stdin(monkeypatch: MonkeyPatch) -> None:
    test_args = ["prog"]
    monkeypatch.setattr(sys, "argv", test_args)
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    with pytest.raises(SystemExit):
        parse_arguments()
