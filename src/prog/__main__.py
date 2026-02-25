"""CLI entry point: `python -m prog <file.prog>` or `python -m prog` (REPL)."""

from __future__ import annotations

import os
import sys

from .interpreter import Interpreter, run
from .lexer import LexError
from .parser import ParseError

# ANSI colour codes — disabled when not a TTY or when NO_COLOR is set
_USE_COLOR = sys.stdout.isatty() and "NO_COLOR" not in os.environ


def _c(code: str, text: str) -> str:
    """Wrap *text* in an ANSI colour escape, if colours are enabled."""
    return f"\033[{code}m{text}\033[0m" if _USE_COLOR else text


_BANNER = """\
  ____  ____  ___   ____
 |  _ \\|  _ \\/ _ \\ / ___|
 | |_) | |_) | | | | |  _
 |  __/|  _ <| |_| | |_| |
 |_|   |_| \\_\\\\___/ \\____|
"""


def _repl() -> None:
    from . import __version__
    interp = Interpreter()
    print(_c("36", _BANNER))
    print(
        _c("1", f"PROG {__version__}")
        + "  —  simple open-source programming language"
    )
    print(_c("2", "Type 'exit' or press Ctrl-D to quit.\n"))
    while True:
        try:
            line = input(_c("32;1", ">>> "))
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if line.strip() in ("exit", "quit"):
            break
        if not line.strip():
            continue
        if line.strip().startswith("run "):
            path = line.strip()[4:].strip()
            try:
                with open(path, encoding="utf-8") as fh:
                    source = fh.read()
                interp.exec(source)
            except OSError as exc:
                print(_c("31", f"Cannot open '{path}': {exc}"), file=sys.stderr)
            except (LexError, ParseError) as exc:
                print(_c("33", f"Syntax error: {exc}"), file=sys.stderr)
            except Exception as exc:  # noqa: BLE001
                print(_c("31", f"Error: {exc}"), file=sys.stderr)
            continue
        try:
            interp.exec(line)
        except (LexError, ParseError) as exc:
            print(_c("33", f"Syntax error: {exc}"), file=sys.stderr)
        except Exception as exc:  # noqa: BLE001
            print(_c("31", f"Error: {exc}"), file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        _repl()
        return 0

    path = args[0]
    try:
        with open(path, encoding="utf-8") as fh:
            source = fh.read()
    except OSError as exc:
        print(_c("31", f"Cannot open '{path}': {exc}"), file=sys.stderr)
        return 1

    try:
        run(source)
    except (LexError, ParseError) as exc:
        print(_c("33", f"Syntax error: {exc}"), file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(_c("31", f"Runtime error: {exc}"), file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
