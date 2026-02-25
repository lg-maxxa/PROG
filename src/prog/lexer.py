"""Lexer for the PROG programming language.

Converts source text into a flat list of Token objects.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import List


class TokenType(Enum):
    # Literals
    NUMBER = auto()
    STRING = auto()
    BOOL = auto()
    NIL = auto()

    # Identifiers & keywords
    IDENT = auto()
    LET = auto()
    IF = auto()
    THEN = auto()
    ELSE = auto()
    END = auto()
    WHILE = auto()
    DO = auto()
    FUNC = auto()
    RETURN = auto()
    PRINT = auto()
    AND = auto()
    OR = auto()
    NOT = auto()

    # Operators
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()
    EQ = auto()        # ==
    NEQ = auto()       # !=
    LT = auto()        # <
    LTE = auto()       # <=
    GT = auto()        # >
    GTE = auto()       # >=
    ASSIGN = auto()    # =

    # Delimiters
    LPAREN = auto()
    RPAREN = auto()
    COMMA = auto()
    NEWLINE = auto()
    EOF = auto()


@dataclass
class Token:
    type: TokenType
    value: object
    line: int

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, line={self.line})"


_KEYWORDS: dict[str, TokenType] = {
    "let": TokenType.LET,
    "if": TokenType.IF,
    "then": TokenType.THEN,
    "else": TokenType.ELSE,
    "end": TokenType.END,
    "while": TokenType.WHILE,
    "do": TokenType.DO,
    "func": TokenType.FUNC,
    "return": TokenType.RETURN,
    "print": TokenType.PRINT,
    "and": TokenType.AND,
    "or": TokenType.OR,
    "not": TokenType.NOT,
    "true": TokenType.BOOL,
    "false": TokenType.BOOL,
    "nil": TokenType.NIL,
}

_TOKEN_PATTERNS: list[tuple[str, TokenType | None]] = [
    (r"[ \t]+", None),                          # whitespace — skip
    (r"#[^\n]*", None),                         # comment — skip
    (r"\n", TokenType.NEWLINE),
    (r"\d+(?:\.\d+)?", TokenType.NUMBER),
    (r'"[^"]*"', TokenType.STRING),
    (r"==", TokenType.EQ),
    (r"!=", TokenType.NEQ),
    (r"<=", TokenType.LTE),
    (r">=", TokenType.GTE),
    (r"<", TokenType.LT),
    (r">", TokenType.GT),
    (r"=", TokenType.ASSIGN),
    (r"\+", TokenType.PLUS),
    (r"-", TokenType.MINUS),
    (r"\*", TokenType.STAR),
    (r"/", TokenType.SLASH),
    (r"%", TokenType.PERCENT),
    (r"\(", TokenType.LPAREN),
    (r"\)", TokenType.RPAREN),
    (r",", TokenType.COMMA),
    (r"[A-Za-z_][A-Za-z0-9_]*", TokenType.IDENT),
]

_MASTER = re.compile(
    "|".join(f"(?P<g{i}>{pat})" for i, (pat, _) in enumerate(_TOKEN_PATTERNS))
)
_TYPES_BY_GROUP = {f"g{i}": tt for i, (_, tt) in enumerate(_TOKEN_PATTERNS)}


class LexError(Exception):
    def __init__(self, message: str, line: int) -> None:
        super().__init__(message)
        self.line = line


def tokenize(source: str) -> List[Token]:
    """Return the token list for *source*, ending with an EOF token."""
    tokens: List[Token] = []
    line = 1

    pos = 0
    while pos < len(source):
        m = _MASTER.match(source, pos)
        if not m:
            raise LexError(
                f"Unexpected character {source[pos]!r} at line {line}", line
            )
        pos = m.end()
        group = m.lastgroup
        tt = _TYPES_BY_GROUP[group]
        if tt is None:
            # Skip whitespace / comments; still count newlines inside comments.
            continue

        raw = m.group()

        if tt == TokenType.NEWLINE:
            tokens.append(Token(TokenType.NEWLINE, "\n", line))
            line += 1
            continue

        # Resolve identifiers vs keywords
        if tt == TokenType.IDENT:
            tt = _KEYWORDS.get(raw, TokenType.IDENT)

        # Convert literal values
        if tt == TokenType.NUMBER:
            value: object = float(raw) if "." in raw else int(raw)
        elif tt == TokenType.STRING:
            value = raw[1:-1]  # strip quotes
        elif tt == TokenType.BOOL:
            value = raw == "true"
        elif tt == TokenType.NIL:
            value = None
        else:
            value = raw

        tokens.append(Token(tt, value, line))

    tokens.append(Token(TokenType.EOF, None, line))
    return tokens
