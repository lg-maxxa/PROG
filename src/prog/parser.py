"""Parser for the PROG programming language.

Produces an Abstract Syntax Tree (AST) from a token list.

Grammar (simplified):
    program     = statement* EOF
    statement   = let_stmt
                | print_stmt
                | return_stmt
                | if_stmt
                | while_stmt
                | func_def
                | expr_stmt
    let_stmt    = "let" IDENT "=" expr NEWLINE
    print_stmt  = "print" expr NEWLINE
    return_stmt = "return" expr? NEWLINE
    if_stmt     = "if" expr "then" NEWLINE
                      statement*
                  ("else" NEWLINE statement*)?
                  "end" NEWLINE
    while_stmt  = "while" expr "do" NEWLINE
                      statement*
                  "end" NEWLINE
    func_def    = "func" IDENT "(" params ")" NEWLINE
                      statement*
                  "end" NEWLINE
    params      = (IDENT ("," IDENT)*)?
    expr_stmt   = expr NEWLINE
    expr        = or_expr
    or_expr     = and_expr ("or" and_expr)*
    and_expr    = not_expr ("and" not_expr)*
    not_expr    = "not" not_expr | compare
    compare     = add (("==" | "!=" | "<" | "<=" | ">" | ">=") add)?
    add         = mul (("+" | "-") mul)*
    mul         = unary (("*" | "/" | "%") unary)*
    unary       = "-" unary | call
    call        = primary ("(" args ")")?
    primary     = NUMBER | STRING | BOOL | NIL | IDENT | "(" expr ")"
    args        = (expr ("," expr)*)?
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .lexer import Token, TokenType, tokenize


# ---------------------------------------------------------------------------
# AST nodes
# ---------------------------------------------------------------------------


@dataclass
class NumberLit:
    value: float | int
    line: int


@dataclass
class StringLit:
    value: str
    line: int


@dataclass
class BoolLit:
    value: bool
    line: int


@dataclass
class NilLit:
    line: int


@dataclass
class Ident:
    name: str
    line: int


@dataclass
class BinOp:
    op: str
    left: "Expr"
    right: "Expr"
    line: int


@dataclass
class UnaryOp:
    op: str
    operand: "Expr"
    line: int


@dataclass
class Call:
    callee: str
    args: List["Expr"]
    line: int


# Statement nodes

@dataclass
class LetStmt:
    name: str
    value: "Expr"
    line: int


@dataclass
class PrintStmt:
    value: "Expr"
    line: int


@dataclass
class ReturnStmt:
    value: Optional["Expr"]
    line: int


@dataclass
class IfStmt:
    condition: "Expr"
    then_body: List["Stmt"]
    else_body: List["Stmt"]
    line: int


@dataclass
class WhileStmt:
    condition: "Expr"
    body: List["Stmt"]
    line: int


@dataclass
class FuncDef:
    name: str
    params: List[str]
    body: List["Stmt"]
    line: int


@dataclass
class ExprStmt:
    expr: "Expr"
    line: int


Expr = (
    NumberLit | StringLit | BoolLit | NilLit | Ident | BinOp | UnaryOp | Call
)
Stmt = LetStmt | PrintStmt | ReturnStmt | IfStmt | WhileStmt | FuncDef | ExprStmt


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------


class ParseError(Exception):
    def __init__(self, message: str, line: int) -> None:
        super().__init__(message)
        self.line = line


class Parser:
    def __init__(self, tokens: List[Token]) -> None:
        self._tokens = tokens
        self._pos = 0

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _peek(self) -> Token:
        return self._tokens[self._pos]

    def _advance(self) -> Token:
        tok = self._tokens[self._pos]
        self._pos += 1
        return tok

    def _check(self, *types: TokenType) -> bool:
        return self._peek().type in types

    def _match(self, *types: TokenType) -> Optional[Token]:
        if self._check(*types):
            return self._advance()
        return None

    def _expect(self, tt: TokenType) -> Token:
        tok = self._peek()
        if tok.type != tt:
            raise ParseError(
                f"Expected {tt.name} but got {tok.type.name} ({tok.value!r})",
                tok.line,
            )
        return self._advance()

    def _skip_newlines(self) -> None:
        while self._check(TokenType.NEWLINE):
            self._advance()

    def _expect_newline(self) -> None:
        if self._check(TokenType.EOF):
            return
        if not self._match(TokenType.NEWLINE):
            tok = self._peek()
            raise ParseError(
                f"Expected newline after statement, got {tok.type.name}",
                tok.line,
            )
        while self._match(TokenType.NEWLINE):
            pass

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------

    def parse(self) -> List[Stmt]:
        self._skip_newlines()
        stmts: List[Stmt] = []
        while not self._check(TokenType.EOF):
            stmts.append(self._statement())
            self._skip_newlines()
        return stmts

    # ------------------------------------------------------------------
    # Statements
    # ------------------------------------------------------------------

    def _statement(self) -> Stmt:
        tok = self._peek()

        if tok.type == TokenType.LET:
            return self._let_stmt()
        if tok.type == TokenType.PRINT:
            return self._print_stmt()
        if tok.type == TokenType.RETURN:
            return self._return_stmt()
        if tok.type == TokenType.IF:
            return self._if_stmt()
        if tok.type == TokenType.WHILE:
            return self._while_stmt()
        if tok.type == TokenType.FUNC:
            return self._func_def()
        return self._expr_stmt()

    def _let_stmt(self) -> LetStmt:
        tok = self._expect(TokenType.LET)
        name_tok = self._expect(TokenType.IDENT)
        self._expect(TokenType.ASSIGN)
        value = self._expr()
        self._expect_newline()
        return LetStmt(name_tok.value, value, tok.line)

    def _print_stmt(self) -> PrintStmt:
        tok = self._expect(TokenType.PRINT)
        value = self._expr()
        self._expect_newline()
        return PrintStmt(value, tok.line)

    def _return_stmt(self) -> ReturnStmt:
        tok = self._expect(TokenType.RETURN)
        if self._check(TokenType.NEWLINE, TokenType.EOF):
            self._expect_newline()
            return ReturnStmt(None, tok.line)
        value = self._expr()
        self._expect_newline()
        return ReturnStmt(value, tok.line)

    def _if_stmt(self) -> IfStmt:
        tok = self._expect(TokenType.IF)
        cond = self._expr()
        self._expect(TokenType.THEN)
        self._expect_newline()
        self._skip_newlines()

        then_body: List[Stmt] = []
        while not self._check(TokenType.ELSE, TokenType.END, TokenType.EOF):
            then_body.append(self._statement())
            self._skip_newlines()

        else_body: List[Stmt] = []
        if self._match(TokenType.ELSE):
            self._expect_newline()
            self._skip_newlines()
            while not self._check(TokenType.END, TokenType.EOF):
                else_body.append(self._statement())
                self._skip_newlines()

        self._expect(TokenType.END)
        self._expect_newline()
        return IfStmt(cond, then_body, else_body, tok.line)

    def _while_stmt(self) -> WhileStmt:
        tok = self._expect(TokenType.WHILE)
        cond = self._expr()
        self._expect(TokenType.DO)
        self._expect_newline()
        self._skip_newlines()

        body: List[Stmt] = []
        while not self._check(TokenType.END, TokenType.EOF):
            body.append(self._statement())
            self._skip_newlines()

        self._expect(TokenType.END)
        self._expect_newline()
        return WhileStmt(cond, body, tok.line)

    def _func_def(self) -> FuncDef:
        tok = self._expect(TokenType.FUNC)
        name_tok = self._expect(TokenType.IDENT)
        self._expect(TokenType.LPAREN)
        params: List[str] = []
        if not self._check(TokenType.RPAREN):
            params.append(self._expect(TokenType.IDENT).value)
            while self._match(TokenType.COMMA):
                params.append(self._expect(TokenType.IDENT).value)
        self._expect(TokenType.RPAREN)
        self._expect_newline()
        self._skip_newlines()

        body: List[Stmt] = []
        while not self._check(TokenType.END, TokenType.EOF):
            body.append(self._statement())
            self._skip_newlines()

        self._expect(TokenType.END)
        self._expect_newline()
        return FuncDef(name_tok.value, params, body, tok.line)

    def _expr_stmt(self) -> ExprStmt:
        tok = self._peek()
        expr = self._expr()
        self._expect_newline()
        return ExprStmt(expr, tok.line)

    # ------------------------------------------------------------------
    # Expressions  (recursive descent, lowest to highest precedence)
    # ------------------------------------------------------------------

    def _expr(self) -> Expr:
        return self._or_expr()

    def _or_expr(self) -> Expr:
        left = self._and_expr()
        while self._check(TokenType.OR):
            op_tok = self._advance()
            right = self._and_expr()
            left = BinOp("or", left, right, op_tok.line)
        return left

    def _and_expr(self) -> Expr:
        left = self._not_expr()
        while self._check(TokenType.AND):
            op_tok = self._advance()
            right = self._not_expr()
            left = BinOp("and", left, right, op_tok.line)
        return left

    def _not_expr(self) -> Expr:
        if self._check(TokenType.NOT):
            op_tok = self._advance()
            operand = self._not_expr()
            return UnaryOp("not", operand, op_tok.line)
        return self._compare()

    def _compare(self) -> Expr:
        left = self._add()
        cmp_ops = (
            TokenType.EQ, TokenType.NEQ,
            TokenType.LT, TokenType.LTE,
            TokenType.GT, TokenType.GTE,
        )
        if self._check(*cmp_ops):
            op_tok = self._advance()
            right = self._add()
            return BinOp(op_tok.value, left, right, op_tok.line)
        return left

    def _add(self) -> Expr:
        left = self._mul()
        while self._check(TokenType.PLUS, TokenType.MINUS):
            op_tok = self._advance()
            right = self._mul()
            left = BinOp(op_tok.value, left, right, op_tok.line)
        return left

    def _mul(self) -> Expr:
        left = self._unary()
        while self._check(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op_tok = self._advance()
            right = self._unary()
            left = BinOp(op_tok.value, left, right, op_tok.line)
        return left

    def _unary(self) -> Expr:
        if self._check(TokenType.MINUS):
            op_tok = self._advance()
            operand = self._unary()
            return UnaryOp("-", operand, op_tok.line)
        return self._call()

    def _call(self) -> Expr:
        primary = self._primary()
        if isinstance(primary, Ident) and self._check(TokenType.LPAREN):
            self._advance()
            args: List[Expr] = []
            if not self._check(TokenType.RPAREN):
                args.append(self._expr())
                while self._match(TokenType.COMMA):
                    args.append(self._expr())
            self._expect(TokenType.RPAREN)
            return Call(primary.name, args, primary.line)
        return primary

    def _primary(self) -> Expr:
        tok = self._peek()

        if tok.type == TokenType.NUMBER:
            self._advance()
            return NumberLit(tok.value, tok.line)

        if tok.type == TokenType.STRING:
            self._advance()
            return StringLit(tok.value, tok.line)

        if tok.type == TokenType.BOOL:
            self._advance()
            return BoolLit(tok.value, tok.line)

        if tok.type == TokenType.NIL:
            self._advance()
            return NilLit(tok.line)

        if tok.type == TokenType.IDENT:
            self._advance()
            return Ident(tok.value, tok.line)

        if tok.type == TokenType.LPAREN:
            self._advance()
            expr = self._expr()
            self._expect(TokenType.RPAREN)
            return expr

        raise ParseError(
            f"Unexpected token {tok.type.name} ({tok.value!r})", tok.line
        )


# ---------------------------------------------------------------------------
# Convenience
# ---------------------------------------------------------------------------


def parse(source: str) -> List[Stmt]:
    """Tokenize and parse *source*, returning a list of top-level statements."""
    tokens = tokenize(source)
    return Parser(tokens).parse()
