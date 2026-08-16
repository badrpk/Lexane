"""Lexane deterministic language kernel with HuobzLang compatibility terminology.

This module intentionally implements a small, dependency-free language core:
- integer literals and variables
- let bindings
- arithmetic expressions with +, -, *, /
- deterministic diagnostics
- canonical intermediate representation (IR)
- execution and compilation receipts

It does not attempt to replace any external/full HuobzLang compiler implementation.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
import json
import re
from typing import Iterable


TOKEN_RE = re.compile(
    r"(?P<WS>\s+)|(?P<INT>\d+)|(?P<ID>[A-Za-z_][A-Za-z0-9_]*)|"
    r"(?P<EQ>=)|(?P<SEMI>;)|(?P<LPAREN>\()|(?P<RPAREN>\))|"
    r"(?P<PLUS>\+)|(?P<MINUS>-)|(?P<STAR>\*)|(?P<SLASH>/)|(?P<MISMATCH>.)"
)


class LexaneError(ValueError):
    """Deterministic language diagnostic."""

    def __init__(self, code: str, message: str, position: int | None = None):
        self.code = code
        self.position = position
        suffix = "" if position is None else f" at {position}"
        super().__init__(f"{code}: {message}{suffix}")


@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    position: int


@dataclass(frozen=True)
class IntNode:
    value: int


@dataclass(frozen=True)
class VarNode:
    name: str


@dataclass(frozen=True)
class BinaryNode:
    op: str
    left: object
    right: object


@dataclass(frozen=True)
class LetNode:
    name: str
    expr: object


@dataclass(frozen=True)
class ExprStmtNode:
    expr: object


def tokenize(source: str) -> tuple[Token, ...]:
    if not isinstance(source, str):
        raise TypeError("source must be str")
    tokens: list[Token] = []
    for match in TOKEN_RE.finditer(source):
        kind = match.lastgroup or "MISMATCH"
        value = match.group()
        pos = match.start()
        if kind == "WS":
            continue
        if kind == "MISMATCH":
            raise LexaneError("LEX001", f"unexpected character {value!r}", pos)
        tokens.append(Token(kind, value, pos))
    tokens.append(Token("EOF", "", len(source)))
    return tuple(tokens)


class Parser:
    def __init__(self, tokens: Iterable[Token]):
        self.tokens = tuple(tokens)
        self.i = 0

    @property
    def current(self) -> Token:
        return self.tokens[self.i]

    def take(self, kind: str) -> Token:
        tok = self.current
        if tok.kind != kind:
            raise LexaneError("PAR001", f"expected {kind}, got {tok.kind}", tok.position)
        self.i += 1
        return tok

    def parse_program(self) -> tuple[object, ...]:
        statements: list[object] = []
        while self.current.kind != "EOF":
            statements.append(self.parse_statement())
            if self.current.kind == "SEMI":
                self.take("SEMI")
            elif self.current.kind != "EOF":
                raise LexaneError("PAR002", "expected ';' between statements", self.current.position)
        return tuple(statements)

    def parse_statement(self) -> object:
        if self.current.kind == "ID" and self.current.value == "let":
            self.take("ID")
            name = self.take("ID").value
            self.take("EQ")
            return LetNode(name, self.parse_expr())
        return ExprStmtNode(self.parse_expr())

    def parse_expr(self) -> object:
        node = self.parse_term()
        while self.current.kind in {"PLUS", "MINUS"}:
            op = self.current.value
            self.i += 1
            node = BinaryNode(op, node, self.parse_term())
        return node

    def parse_term(self) -> object:
        node = self.parse_factor()
        while self.current.kind in {"STAR", "SLASH"}:
            op = self.current.value
            self.i += 1
            node = BinaryNode(op, node, self.parse_factor())
        return node

    def parse_factor(self) -> object:
        tok = self.current
        if tok.kind == "INT":
            self.i += 1
            return IntNode(int(tok.value))
        if tok.kind == "ID":
            self.i += 1
            return VarNode(tok.value)
        if tok.kind == "MINUS":
            self.i += 1
            return BinaryNode("-", IntNode(0), self.parse_factor())
        if tok.kind == "LPAREN":
            self.i += 1
            node = self.parse_expr()
            self.take("RPAREN")
            return node
        raise LexaneError("PAR003", f"expected expression, got {tok.kind}", tok.position)


def parse(source: str) -> tuple[object, ...]:
    return Parser(tokenize(source)).parse_program()


def _eval(node: object, env: dict[str, int]) -> int:
    if isinstance(node, IntNode):
        return node.value
    if isinstance(node, VarNode):
        if node.name not in env:
            raise LexaneError("SEM001", f"undefined variable {node.name!r}")
        return env[node.name]
    if isinstance(node, BinaryNode):
        left = _eval(node.left, env)
        right = _eval(node.right, env)
        if node.op == "+":
            return left + right
        if node.op == "-":
            return left - right
        if node.op == "*":
            return left * right
        if node.op == "/":
            if right == 0:
                raise LexaneError("RUN001", "division by zero")
            return int(left / right)
        raise LexaneError("SEM002", f"unsupported operator {node.op!r}")
    raise LexaneError("SEM003", f"unsupported node {type(node).__name__}")


def execute(source: str) -> dict[str, object]:
    env: dict[str, int] = {}
    last: int | None = None
    for stmt in parse(source):
        if isinstance(stmt, LetNode):
            value = _eval(stmt.expr, env)
            env[stmt.name] = value
            last = value
        elif isinstance(stmt, ExprStmtNode):
            last = _eval(stmt.expr, env)
        else:
            raise LexaneError("SEM004", "unknown statement")
    return {"result": last, "variables": dict(sorted(env.items()))}


def _node_ir(node: object) -> dict[str, object]:
    if isinstance(node, IntNode):
        return {"kind": "int", "value": node.value}
    if isinstance(node, VarNode):
        return {"kind": "var", "name": node.name}
    if isinstance(node, BinaryNode):
        return {"kind": "binary", "op": node.op, "left": _node_ir(node.left), "right": _node_ir(node.right)}
    if isinstance(node, LetNode):
        return {"kind": "let", "name": node.name, "expr": _node_ir(node.expr)}
    if isinstance(node, ExprStmtNode):
        return {"kind": "expr", "expr": _node_ir(node.expr)}
    raise TypeError(type(node).__name__)


def compile_ir(source: str) -> dict[str, object]:
    return {
        "language": "Lexane",
        "compatibility": "HuobzLang",
        "version": 1,
        "statements": [_node_ir(stmt) for stmt in parse(source)],
    }


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def compile_receipt(source: str) -> dict[str, object]:
    ir = compile_ir(source)
    result = execute(source)
    source_hash = sha256(source.encode("utf-8")).hexdigest()
    ir_hash = sha256(canonical_json(ir).encode("utf-8")).hexdigest()
    receipt = {
        "source_sha256": source_hash,
        "ir_sha256": ir_hash,
        "result": result,
        "language": "Lexane",
        "compatibility": "HuobzLang",
    }
    receipt["receipt_sha256"] = sha256(canonical_json(receipt).encode("utf-8")).hexdigest()
    return receipt


__all__ = [
    "LexaneError",
    "Token",
    "tokenize",
    "parse",
    "execute",
    "compile_ir",
    "compile_receipt",
    "canonical_json",
]
