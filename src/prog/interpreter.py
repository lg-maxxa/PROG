"""Interpreter (tree-walking evaluator) for the PROG programming language."""

from __future__ import annotations

import sys
from typing import Any, Dict, List, Optional

from .parser import (
    BinOp,
    BoolLit,
    Call,
    ExprStmt,
    FuncDef,
    Ident,
    IfStmt,
    IndexExpr,
    LetStmt,
    ListLit,
    NilLit,
    NumberLit,
    PrintStmt,
    ReturnStmt,
    StringLit,
    UnaryOp,
    WhileStmt,
    parse,
)


# ---------------------------------------------------------------------------
# Runtime values
# ---------------------------------------------------------------------------

Value = int | float | str | bool | list | None


class _ReturnSignal(Exception):
    """Internal signal used to unwind the call stack on `return`."""

    def __init__(self, value: Value) -> None:
        self.value = value


class _Function:
    """A user-defined PROG function."""

    def __init__(self, name: str, params: List[str], body, env: "Environment") -> None:
        self.name = name
        self.params = params
        self.body = body
        self.closure = env  # captured environment

    def __repr__(self) -> str:
        return f"<func {self.name}>"


class _Builtin:
    """A built-in PROG function implemented in Python."""

    def __init__(self, name: str, fn) -> None:
        self.name = name
        self.fn = fn

    def __repr__(self) -> str:
        return f"<builtin {self.name}>"


# ---------------------------------------------------------------------------
# Environment (scoping)
# ---------------------------------------------------------------------------


class Environment:
    """A single scope frame; delegates missing names to the enclosing frame."""

    def __init__(self, parent: Optional["Environment"] = None) -> None:
        self._vars: Dict[str, Any] = {}
        self._parent = parent

    def get(self, name: str, line: int) -> Any:
        if name in self._vars:
            return self._vars[name]
        if self._parent is not None:
            return self._parent.get(name, line)
        raise RuntimeError(f"Undefined variable '{name}' at line {line}")

    def set(self, name: str, value: Any) -> None:
        """Bind *name* in the current (innermost) scope."""
        self._vars[name] = value

    def assign(self, name: str, value: Any, line: int) -> None:
        """Re-bind an existing variable, walking up the scope chain."""
        if name in self._vars:
            self._vars[name] = value
        elif self._parent is not None:
            self._parent.assign(name, value, line)
        else:
            # Treat as a new global binding (convenient for top-level `let`).
            self._vars[name] = value


# ---------------------------------------------------------------------------
# Interpreter
# ---------------------------------------------------------------------------


class RuntimeError(Exception):  # noqa: A001  (shadows builtin intentionally)
    def __init__(self, message: str) -> None:
        super().__init__(message)


class Interpreter:
    """Tree-walking interpreter for PROG programs."""

    def __init__(self, output=None) -> None:
        self._output = output  # callable(str) — defaults to print
        self._globals = Environment()
        self._register_builtins()

    def _register_builtins(self) -> None:
        """Register standard built-in functions in the global scope."""

        def _len(args, line):
            if len(args) != 1:
                raise RuntimeError(f"len() takes 1 argument at line {line}")
            v = args[0]
            if isinstance(v, (str, list)):
                return len(v)
            raise RuntimeError(
                f"len() requires a string or list, got {type(v).__name__} at line {line}"
            )

        def _type(args, line):
            if len(args) != 1:
                raise RuntimeError(f"type() takes 1 argument at line {line}")
            v = args[0]
            if v is None:
                return "nil"
            if isinstance(v, bool):
                return "bool"
            if isinstance(v, int):
                return "int"
            if isinstance(v, float):
                return "float"
            if isinstance(v, str):
                return "string"
            if isinstance(v, list):
                return "list"
            return type(v).__name__

        def _str(args, line):
            if len(args) != 1:
                raise RuntimeError(f"str() takes 1 argument at line {line}")
            return self._to_str(args[0])

        def _int(args, line):
            if len(args) != 1:
                raise RuntimeError(f"int() takes 1 argument at line {line}")
            v = args[0]
            try:
                if isinstance(v, bool):
                    raise RuntimeError(
                        f"int() cannot convert bool at line {line}"
                    )
                return int(v)
            except (ValueError, TypeError):
                raise RuntimeError(
                    f"int() cannot convert {type(v).__name__!r} at line {line}"
                )

        def _float(args, line):
            if len(args) != 1:
                raise RuntimeError(f"float() takes 1 argument at line {line}")
            v = args[0]
            try:
                if isinstance(v, bool):
                    raise RuntimeError(
                        f"float() cannot convert bool at line {line}"
                    )
                return float(v)
            except (ValueError, TypeError):
                raise RuntimeError(
                    f"float() cannot convert {type(v).__name__!r} at line {line}"
                )

        def _abs(args, line):
            if len(args) != 1:
                raise RuntimeError(f"abs() takes 1 argument at line {line}")
            return abs(self._num(args[0], line))

        def _max(args, line):
            if len(args) == 1 and isinstance(args[0], list):
                items = args[0]
            else:
                items = args
            if not items:
                raise RuntimeError(f"max() called with no values at line {line}")
            return max(self._num(v, line) for v in items)

        def _min(args, line):
            if len(args) == 1 and isinstance(args[0], list):
                items = args[0]
            else:
                items = args
            if not items:
                raise RuntimeError(f"min() called with no values at line {line}")
            return min(self._num(v, line) for v in items)

        def _append(args, line):
            if len(args) != 2:
                raise RuntimeError(f"append() takes 2 arguments at line {line}")
            lst, val = args
            if not isinstance(lst, list):
                raise RuntimeError(
                    f"append() requires a list as first argument at line {line}"
                )
            lst.append(val)
            return lst

        def _pop(args, line):
            if len(args) not in (1, 2):
                raise RuntimeError(
                    f"pop() takes 1 or 2 arguments at line {line}"
                )
            lst = args[0]
            if not isinstance(lst, list):
                raise RuntimeError(
                    f"pop() requires a list as first argument at line {line}"
                )
            if len(args) == 2:
                idx = int(self._num(args[1], line))
                if idx < 0 or idx >= len(lst):
                    raise RuntimeError(
                        f"pop() index out of range at line {line}"
                    )
                return lst.pop(idx)
            if not lst:
                raise RuntimeError(f"pop() from empty list at line {line}")
            return lst.pop()

        def _input(args, line):
            if len(args) > 1:
                raise RuntimeError(f"input() takes 0 or 1 argument at line {line}")
            prompt = self._to_str(args[0]) if args else ""
            try:
                return input(prompt)
            except EOFError:
                return ""

        for name, fn in [
            ("len", _len),
            ("type", _type),
            ("str", _str),
            ("int", _int),
            ("float", _float),
            ("abs", _abs),
            ("max", _max),
            ("min", _min),
            ("append", _append),
            ("pop", _pop),
            ("input", _input),
        ]:
            self._globals.set(name, _Builtin(name, fn))

    def _emit(self, text: str) -> None:
        if self._output is not None:
            self._output(text)
        else:
            print(text)  # noqa: T201

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def exec(self, source: str) -> None:
        """Parse and execute *source* in the global environment."""
        stmts = parse(source)
        self._exec_block(stmts, self._globals)

    # ------------------------------------------------------------------
    # Statement execution
    # ------------------------------------------------------------------

    def _exec_block(self, stmts, env: Environment) -> None:
        for stmt in stmts:
            self._exec_stmt(stmt, env)

    def _exec_stmt(self, stmt, env: Environment) -> None:
        if isinstance(stmt, LetStmt):
            value = self._eval(stmt.value, env)
            env.assign(stmt.name, value, stmt.line)

        elif isinstance(stmt, PrintStmt):
            value = self._eval(stmt.value, env)
            self._emit(self._to_str(value))

        elif isinstance(stmt, ReturnStmt):
            value = self._eval(stmt.value, env) if stmt.value is not None else None
            raise _ReturnSignal(value)

        elif isinstance(stmt, IfStmt):
            cond = self._eval(stmt.condition, env)
            if self._is_truthy(cond):
                child = Environment(env)
                self._exec_block(stmt.then_body, child)
            elif stmt.else_body:
                child = Environment(env)
                self._exec_block(stmt.else_body, child)

        elif isinstance(stmt, WhileStmt):
            while self._is_truthy(self._eval(stmt.condition, env)):
                child = Environment(env)
                self._exec_block(stmt.body, child)

        elif isinstance(stmt, FuncDef):
            fn = _Function(stmt.name, stmt.params, stmt.body, env)
            env.set(stmt.name, fn)

        elif isinstance(stmt, ExprStmt):
            self._eval(stmt.expr, env)

        else:
            raise RuntimeError(f"Unknown statement type: {type(stmt).__name__}")

    # ------------------------------------------------------------------
    # Expression evaluation
    # ------------------------------------------------------------------

    def _eval(self, node, env: Environment) -> Value:
        if isinstance(node, NumberLit):
            return node.value

        if isinstance(node, StringLit):
            return node.value

        if isinstance(node, BoolLit):
            return node.value

        if isinstance(node, NilLit):
            return None

        if isinstance(node, ListLit):
            return [self._eval(e, env) for e in node.elements]

        if isinstance(node, Ident):
            return env.get(node.name, node.line)

        if isinstance(node, IndexExpr):
            collection = self._eval(node.collection, env)
            index = self._eval(node.index, env)
            if not isinstance(collection, (list, str)):
                raise RuntimeError(
                    f"Index operator requires a list or string at line {node.line}"
                )
            if not isinstance(index, (int, float)) or isinstance(index, bool):
                raise RuntimeError(
                    f"Index must be a number at line {node.line}"
                )
            idx = int(index)
            if idx < 0 or idx >= len(collection):
                raise RuntimeError(
                    f"Index {idx} out of range (length {len(collection)}) "
                    f"at line {node.line}"
                )
            return collection[idx]

        if isinstance(node, UnaryOp):
            operand = self._eval(node.operand, env)
            if node.op == "-":
                if not isinstance(operand, (int, float)):
                    raise RuntimeError(
                        f"Unary '-' requires a number, got {type(operand).__name__} "
                        f"at line {node.line}"
                    )
                return -operand
            if node.op == "not":
                return not self._is_truthy(operand)
            raise RuntimeError(f"Unknown unary op '{node.op}'")

        if isinstance(node, BinOp):
            return self._eval_binop(node, env)

        if isinstance(node, Call):
            return self._eval_call(node, env)

        raise RuntimeError(f"Unknown expression type: {type(node).__name__}")

    def _eval_binop(self, node: BinOp, env: Environment) -> Value:
        op = node.op
        line = node.line

        # Short-circuit logical operators
        if op == "and":
            left = self._eval(node.left, env)
            return left if not self._is_truthy(left) else self._eval(node.right, env)
        if op == "or":
            left = self._eval(node.left, env)
            return left if self._is_truthy(left) else self._eval(node.right, env)

        left = self._eval(node.left, env)
        right = self._eval(node.right, env)

        if op == "+":
            if isinstance(left, str) or isinstance(right, str):
                return self._to_str(left) + self._to_str(right)
            return self._num(left, line) + self._num(right, line)
        if op == "-":
            return self._num(left, line) - self._num(right, line)
        if op == "*":
            return self._num(left, line) * self._num(right, line)
        if op == "/":
            r = self._num(right, line)
            if r == 0:
                raise RuntimeError(f"Division by zero at line {line}")
            return self._num(left, line) / r
        if op == "%":
            r = self._num(right, line)
            if r == 0:
                raise RuntimeError(f"Modulo by zero at line {line}")
            return self._num(left, line) % r

        if op == "==":
            return left == right
        if op == "!=":
            return left != right
        if op == "<":
            return self._num(left, line) < self._num(right, line)
        if op == "<=":
            return self._num(left, line) <= self._num(right, line)
        if op == ">":
            return self._num(left, line) > self._num(right, line)
        if op == ">=":
            return self._num(left, line) >= self._num(right, line)

        raise RuntimeError(f"Unknown binary operator '{op}' at line {line}")

    def _eval_call(self, node: Call, env: Environment) -> Value:
        callee = env.get(node.callee, node.line)
        if isinstance(callee, _Builtin):
            args = [self._eval(a, env) for a in node.args]
            return callee.fn(args, node.line)
        if not isinstance(callee, _Function):
            raise RuntimeError(
                f"'{node.callee}' is not a function at line {node.line}"
            )
        if len(node.args) != len(callee.params):
            raise RuntimeError(
                f"'{node.callee}' expects {len(callee.params)} argument(s), "
                f"got {len(node.args)} at line {node.line}"
            )
        args = [self._eval(a, env) for a in node.args]
        call_env = Environment(callee.closure)
        for param, arg in zip(callee.params, args):
            call_env.set(param, arg)
        try:
            self._exec_block(callee.body, call_env)
        except _ReturnSignal as sig:
            return sig.value
        return None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _is_truthy(value: Value) -> bool:
        if value is None or value is False:
            return False
        if isinstance(value, (int, float)) and value == 0:
            return False
        return True

    @staticmethod
    def _num(value: Value, line: int) -> int | float:
        if isinstance(value, bool):
            raise RuntimeError(
                f"Expected a number, got bool at line {line}"
            )
        if not isinstance(value, (int, float)):
            raise RuntimeError(
                f"Expected a number, got {type(value).__name__} at line {line}"
            )
        return value

    @staticmethod
    def _to_str(value: Value) -> str:
        if value is None:
            return "nil"
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, list):
            return "[" + ", ".join(Interpreter._to_str(v) for v in value) + "]"
        if isinstance(value, float) and value == int(value):
            return str(int(value))
        return str(value)


# ---------------------------------------------------------------------------
# Convenience
# ---------------------------------------------------------------------------


def run(source: str, output=None) -> None:
    """Parse and execute *source*, writing output via *output* (defaults to print)."""
    Interpreter(output=output).exec(source)
