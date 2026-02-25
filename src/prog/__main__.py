"""CLI entry point: `python -m prog <file.prog>` or `python -m prog` (REPL)."""

from __future__ import annotations

import sys

from . import __version__
from .interpreter import Interpreter, run
from .lexer import LexError
from .parser import ParseError


def _repl() -> None:
    interp = Interpreter()
    print(f"PROG {__version__}  (type 'exit' or Ctrl-D to quit)")
    while True:
        try:
            line = input(">>> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if line.strip() in ("exit", "quit"):
            break
        if not line.strip():
            continue
        try:
            interp.exec(line)
        except (LexError, ParseError, Exception) as exc:
            print(f"Error: {exc}", file=sys.stderr)


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
        print(f"Cannot open '{path}': {exc}", file=sys.stderr)
        return 1

    try:
        run(source)
    except (LexError, ParseError) as exc:
        print(f"Syntax error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"Runtime error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
