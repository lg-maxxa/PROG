"""Tests for the PROG CLI entry point (REPL run command)."""

from __future__ import annotations

import io
import os
import sys
from unittest.mock import patch

import pytest

from src.prog.__main__ import main


class TestMainFile:
    """Tests for running .prog files via the CLI."""

    def _examples(self, name: str) -> str:
        return os.path.join(os.path.dirname(__file__), "..", "examples", name)

    def test_run_hello(self, capsys):
        ret = main([self._examples("hello.prog")])
        assert ret == 0
        assert "Hello, World!" in capsys.readouterr().out

    def test_run_missing_file(self, capsys):
        ret = main(["nonexistent.prog"])
        assert ret == 1
        assert "Cannot open" in capsys.readouterr().err


class TestReplRunCommand:
    """Tests for the REPL 'run <filename>' command."""

    def _examples(self, name: str) -> str:
        return os.path.join(os.path.dirname(__file__), "..", "examples", name)

    def test_run_command_executes_file(self, capsys):
        inputs = iter([f"run {self._examples('hello.prog')}", "exit"])
        with patch("builtins.input", side_effect=inputs):
            main([])
        assert "Hello, World!" in capsys.readouterr().out

    def test_run_command_missing_file(self, capsys):
        inputs = iter(["run nonexistent.prog", "exit"])
        with patch("builtins.input", side_effect=inputs):
            main([])
        assert "Cannot open" in capsys.readouterr().err

    def test_run_command_preserves_state(self, capsys):
        inputs = iter([
            "let x = 42",
            f"run {self._examples('hello.prog')}",
            "print x",
            "exit",
        ])
        with patch("builtins.input", side_effect=inputs):
            main([])
        out = capsys.readouterr().out
        assert "Hello, World!" in out
        assert "42" in out
