"""Tests for the PROG parser."""

import pytest
from src.prog.parser import (
    BinOp,
    BoolLit,
    Call,
    ExprStmt,
    FuncDef,
    Ident,
    IfStmt,
    LetStmt,
    NilLit,
    NumberLit,
    ParseError,
    PrintStmt,
    ReturnStmt,
    StringLit,
    UnaryOp,
    WhileStmt,
    parse,
)


def _stmt(source: str):
    """Parse source and return the single statement."""
    stmts = parse(source)
    assert len(stmts) == 1
    return stmts[0]


class TestLetStatement:
    def test_number(self):
        s = _stmt("let x = 42\n")
        assert isinstance(s, LetStmt)
        assert s.name == "x"
        assert isinstance(s.value, NumberLit)
        assert s.value.value == 42

    def test_string(self):
        s = _stmt('let msg = "hi"\n')
        assert s.name == "msg"
        assert isinstance(s.value, StringLit)
        assert s.value.value == "hi"

    def test_bool(self):
        s = _stmt("let flag = true\n")
        assert isinstance(s.value, BoolLit)
        assert s.value.value is True

    def test_nil(self):
        s = _stmt("let x = nil\n")
        assert isinstance(s.value, NilLit)


class TestPrintStatement:
    def test_print_number(self):
        s = _stmt("print 7\n")
        assert isinstance(s, PrintStmt)
        assert isinstance(s.value, NumberLit)


class TestReturnStatement:
    def test_return_value(self):
        s = _stmt("return 1\n")
        assert isinstance(s, ReturnStmt)
        assert isinstance(s.value, NumberLit)

    def test_return_empty(self):
        s = _stmt("return\n")
        assert isinstance(s, ReturnStmt)
        assert s.value is None


class TestIfStatement:
    def test_if_then_end(self):
        src = "if x > 0 then\n  print x\nend\n"
        s = _stmt(src)
        assert isinstance(s, IfStmt)
        assert len(s.then_body) == 1
        assert s.else_body == []

    def test_if_else_end(self):
        src = "if x > 0 then\n  print 1\nelse\n  print 0\nend\n"
        s = _stmt(src)
        assert isinstance(s, IfStmt)
        assert len(s.then_body) == 1
        assert len(s.else_body) == 1


class TestWhileStatement:
    def test_while(self):
        src = "while i < 10 do\n  print i\nend\n"
        s = _stmt(src)
        assert isinstance(s, WhileStmt)
        assert len(s.body) == 1


class TestFuncDef:
    def test_no_params(self):
        src = "func hello()\n  print \"hi\"\nend\n"
        s = _stmt(src)
        assert isinstance(s, FuncDef)
        assert s.name == "hello"
        assert s.params == []

    def test_with_params(self):
        src = "func add(a, b)\n  return a + b\nend\n"
        s = _stmt(src)
        assert isinstance(s, FuncDef)
        assert s.params == ["a", "b"]


class TestExpressions:
    def _expr(self, src: str):
        s = _stmt(src + "\n")
        assert isinstance(s, ExprStmt)
        return s.expr

    def test_binop_add(self):
        e = self._expr("1 + 2")
        assert isinstance(e, BinOp)
        assert e.op == "+"

    def test_binop_precedence(self):
        # 1 + 2 * 3  =>  1 + (2 * 3)
        e = self._expr("1 + 2 * 3")
        assert isinstance(e, BinOp) and e.op == "+"
        assert isinstance(e.right, BinOp) and e.right.op == "*"

    def test_unary_minus(self):
        e = self._expr("-x")
        assert isinstance(e, UnaryOp)
        assert e.op == "-"

    def test_not(self):
        e = self._expr("not true")
        assert isinstance(e, UnaryOp)
        assert e.op == "not"

    def test_call(self):
        e = self._expr("add(1, 2)")
        assert isinstance(e, Call)
        assert e.callee == "add"
        assert len(e.args) == 2

    def test_call_no_args(self):
        e = self._expr("noop()")
        assert isinstance(e, Call)
        assert e.args == []

    def test_grouped(self):
        e = self._expr("(1 + 2) * 3")
        assert isinstance(e, BinOp) and e.op == "*"

    def test_and_or(self):
        e = self._expr("a and b or c")
        assert isinstance(e, BinOp) and e.op == "or"


class TestErrors:
    def test_unexpected_token(self):
        with pytest.raises(ParseError):
            parse("let = 5\n")

    def test_missing_end(self):
        with pytest.raises(ParseError):
            parse("if true then\n  print 1\n")
