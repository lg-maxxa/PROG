"""Tests for the PROG interpreter."""

import pytest
from src.prog.interpreter import Interpreter, RuntimeError, run


def _run(source: str) -> list[str]:
    """Run *source* and return captured output lines."""
    output: list[str] = []
    Interpreter(output=output.append).exec(source)
    return output


class TestLiterals:
    def test_print_number(self):
        assert _run("print 42\n") == ["42"]

    def test_print_float(self):
        assert _run("print 3.14\n") == ["3.14"]

    def test_print_string(self):
        assert _run('print "hello"\n') == ["hello"]

    def test_print_bool_true(self):
        assert _run("print true\n") == ["true"]

    def test_print_bool_false(self):
        assert _run("print false\n") == ["false"]

    def test_print_nil(self):
        assert _run("print nil\n") == ["nil"]


class TestArithmetic:
    def test_addition(self):
        assert _run("print 2 + 3\n") == ["5"]

    def test_subtraction(self):
        assert _run("print 10 - 4\n") == ["6"]

    def test_multiplication(self):
        assert _run("print 3 * 4\n") == ["12"]

    def test_division(self):
        assert _run("print 10 / 4\n") == ["2.5"]

    def test_modulo(self):
        assert _run("print 10 % 3\n") == ["1"]

    def test_unary_minus(self):
        assert _run("print -5\n") == ["-5"]

    def test_string_concat(self):
        assert _run('print "hi" + " there"\n') == ["hi there"]

    def test_precedence(self):
        assert _run("print 2 + 3 * 4\n") == ["14"]

    def test_grouping(self):
        assert _run("print (2 + 3) * 4\n") == ["20"]

    def test_division_by_zero(self):
        with pytest.raises(Exception, match="[Zz]ero"):
            _run("print 1 / 0\n")


class TestVariables:
    def test_let_and_print(self):
        assert _run("let x = 10\nprint x\n") == ["10"]

    def test_reassign(self):
        assert _run("let x = 1\nlet x = 2\nprint x\n") == ["2"]

    def test_undefined(self):
        with pytest.raises(Exception, match="[Uu]ndefined"):
            _run("print y\n")


class TestComparisons:
    def test_eq_true(self):
        assert _run("print 1 == 1\n") == ["true"]

    def test_eq_false(self):
        assert _run("print 1 == 2\n") == ["false"]

    def test_neq(self):
        assert _run("print 1 != 2\n") == ["true"]

    def test_lt(self):
        assert _run("print 3 < 5\n") == ["true"]

    def test_gt(self):
        assert _run("print 5 > 3\n") == ["true"]

    def test_lte(self):
        assert _run("print 3 <= 3\n") == ["true"]

    def test_gte(self):
        assert _run("print 5 >= 6\n") == ["false"]


class TestLogical:
    def test_and_true(self):
        assert _run("print true and true\n") == ["true"]

    def test_and_false(self):
        assert _run("print true and false\n") == ["false"]

    def test_or_true(self):
        assert _run("print false or true\n") == ["true"]

    def test_or_false(self):
        assert _run("print false or false\n") == ["false"]

    def test_not_true(self):
        assert _run("print not false\n") == ["true"]

    def test_not_false(self):
        assert _run("print not true\n") == ["false"]

    def test_short_circuit_and(self):
        # If left is false, right is never evaluated; no undefined error.
        assert _run("print false and undef\n") == ["false"]

    def test_short_circuit_or(self):
        assert _run("print true or undef\n") == ["true"]


class TestIf:
    def test_then_branch(self):
        src = "if 1 < 2 then\n  print \"yes\"\nend\n"
        assert _run(src) == ["yes"]

    def test_else_branch(self):
        src = "if 1 > 2 then\n  print \"yes\"\nelse\n  print \"no\"\nend\n"
        assert _run(src) == ["no"]

    def test_no_else(self):
        src = "if false then\n  print \"oops\"\nend\n"
        assert _run(src) == []


class TestWhile:
    def test_count_down(self):
        src = "let n = 3\nwhile n > 0 do\n  print n\n  let n = n - 1\nend\n"
        assert _run(src) == ["3", "2", "1"]

    def test_zero_iterations(self):
        src = "while false do\n  print \"oops\"\nend\n"
        assert _run(src) == []


class TestFunctions:
    def test_basic_call(self):
        src = (
            "func double(x)\n"
            "  return x * 2\n"
            "end\n"
            "print double(5)\n"
        )
        assert _run(src) == ["10"]

    def test_no_return_value(self):
        src = (
            "func greet(name)\n"
            '  print "Hello, " + name\n'
            "end\n"
            'greet("World")\n'
        )
        assert _run(src) == ["Hello, World"]

    def test_recursion(self):
        src = (
            "func fact(n)\n"
            "  if n <= 1 then\n"
            "    return 1\n"
            "  end\n"
            "  return n * fact(n - 1)\n"
            "end\n"
            "print fact(5)\n"
        )
        assert _run(src) == ["120"]

    def test_closure(self):
        src = (
            "let x = 10\n"
            "func addx(n)\n"
            "  return n + x\n"
            "end\n"
            "print addx(5)\n"
        )
        assert _run(src) == ["15"]

    def test_wrong_arg_count(self):
        src = "func f(a, b)\n  return a\nend\nf(1)\n"
        with pytest.raises(Exception, match="argument"):
            _run(src)

    def test_call_non_function(self):
        src = "let x = 42\nx(1)\n"
        with pytest.raises(Exception, match="not a function"):
            _run(src)


class TestExamples:
    """Smoke-test the example programs shipped with the repo."""

    def _load(self, name: str) -> str:
        import os
        path = os.path.join(
            os.path.dirname(__file__), "..", "examples", name
        )
        with open(path, encoding="utf-8") as fh:
            return fh.read()

    def test_hello(self):
        assert _run(self._load("hello.prog")) == ["Hello, World!"]

    def test_fibonacci(self):
        result = _run(self._load("fibonacci.prog"))
        assert result == ["0", "1", "1", "2", "3", "5", "8", "13", "21", "34"]

    def test_fizzbuzz(self):
        result = _run(self._load("fizzbuzz.prog"))
        assert result[0] == "1"
        assert result[2] == "Fizz"   # 3
        assert result[4] == "Buzz"   # 5
        assert result[14] == "FizzBuzz"  # 15

    def test_functions(self):
        result = _run(self._load("functions.prog"))
        assert "Hello, Alice!" in result
        assert "Hello, Bob!" in result
        assert any("720" in r for r in result)
