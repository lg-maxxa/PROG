"""Tests for the PROG lexer."""

import pytest
from src.prog.lexer import LexError, Token, TokenType, tokenize


def _types(source: str):
    return [t.type for t in tokenize(source) if t.type != TokenType.EOF]


def _values(source: str):
    return [(t.type, t.value) for t in tokenize(source) if t.type != TokenType.EOF]


class TestNumbers:
    def test_integer(self):
        tokens = tokenize("42")
        assert tokens[0] == Token(TokenType.NUMBER, 42, 1)

    def test_float(self):
        tokens = tokenize("3.14")
        assert tokens[0] == Token(TokenType.NUMBER, 3.14, 1)

    def test_leading_dot_float(self):
        tokens = tokenize(".5")
        assert tokens[0] == Token(TokenType.NUMBER, 0.5, 1)

    def test_trailing_dot_float(self):
        tokens = tokenize("5.")
        assert tokens[0] == Token(TokenType.NUMBER, 5.0, 1)

    def test_zero(self):
        tokens = tokenize("0")
        assert tokens[0].value == 0


class TestStrings:
    def test_simple(self):
        tokens = tokenize('"hello"')
        assert tokens[0] == Token(TokenType.STRING, "hello", 1)

    def test_empty(self):
        tokens = tokenize('""')
        assert tokens[0].value == ""

    def test_with_spaces(self):
        tokens = tokenize('"hello world"')
        assert tokens[0].value == "hello world"


class TestBoolsAndNil:
    def test_true(self):
        tokens = tokenize("true")
        assert tokens[0] == Token(TokenType.BOOL, True, 1)

    def test_false(self):
        tokens = tokenize("false")
        assert tokens[0] == Token(TokenType.BOOL, False, 1)

    def test_nil(self):
        tokens = tokenize("nil")
        assert tokens[0] == Token(TokenType.NIL, None, 1)


class TestKeywords:
    def test_all_keywords(self):
        src = "let if then else end while do func return print and or not"
        expected = [
            TokenType.LET, TokenType.IF, TokenType.THEN, TokenType.ELSE,
            TokenType.END, TokenType.WHILE, TokenType.DO, TokenType.FUNC,
            TokenType.RETURN, TokenType.PRINT, TokenType.AND, TokenType.OR,
            TokenType.NOT,
        ]
        assert _types(src) == expected


class TestOperators:
    def test_arithmetic(self):
        assert _types("+ - * / %") == [
            TokenType.PLUS, TokenType.MINUS, TokenType.STAR,
            TokenType.SLASH, TokenType.PERCENT,
        ]

    def test_comparison(self):
        assert _types("== != < <= > >=") == [
            TokenType.EQ, TokenType.NEQ,
            TokenType.LT, TokenType.LTE,
            TokenType.GT, TokenType.GTE,
        ]

    def test_assign(self):
        assert _types("=") == [TokenType.ASSIGN]


class TestDelimiters:
    def test_parens_and_comma(self):
        assert _types("(,)") == [
            TokenType.LPAREN, TokenType.COMMA, TokenType.RPAREN,
        ]

    def test_newline(self):
        assert _types("a\nb") == [
            TokenType.IDENT, TokenType.NEWLINE, TokenType.IDENT,
        ]


class TestComments:
    def test_comment_skipped(self):
        assert _types("# this is a comment") == []

    def test_comment_after_code(self):
        assert _types("42 # answer") == [TokenType.NUMBER]

    def test_comment_then_newline(self):
        types = _types("42 # comment\n99")
        assert types == [TokenType.NUMBER, TokenType.NEWLINE, TokenType.NUMBER]


class TestLineTracking:
    def test_line_numbers(self):
        tokens = tokenize("a\nb\nc")
        ident_tokens = [t for t in tokens if t.type == TokenType.IDENT]
        assert [t.line for t in ident_tokens] == [1, 2, 3]


class TestErrors:
    def test_unexpected_character(self):
        with pytest.raises(LexError):
            tokenize("@")

    def test_error_has_line(self):
        try:
            tokenize("\n\n@")
        except LexError as e:
            assert e.line == 3
