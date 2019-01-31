# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 Patrick Michl <patrick.michl@gmail.com>
# Copyright (c) 2014-2019 AxiaCore S.A.S.
#
# §1 This file is part of nemoa
#
#  Author: Patrick Michl <patrick.michl@gmail.com>, https://frootlab.github.io
#
#  nemoa is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  nemoa is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with
#  nemoa. If not, see <http://www.gnu.org/licenses/>.
#
# §2 This file is forked from py-expression-eval, 0.3.6
#
#  Author: AxiaCore S.A.S., http://axiacore.com
#
#  py-expression-eval is free software: you can redistribute it and/or modify it
#  under the terms of the MIT License as published by the Massachusetts
#  Institute of Technology.
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
#
#  py-expression-eval is based on js-expression-eval by: Matthew Crumley
#  <email@matthewcrumley.com>, http://silentmatt.com/
#
#  py-expression-eval is ported to Python and modified by: Vera Mazhuga
#  <ctrl-alt-delete@live.com>, http://vero4ka.info/
#
"""Expression Parser."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import builtins
import collections
import dataclasses
import itertools
import math
import operator
import random
import re
from typing import Any, Callable, Dict, List, Match, Optional, Union
from nemoa.base import env, stype
from nemoa.types import AnyOp

UNARY = 0
BINARY = 1
FUNCTION = 2
CONSTANT = 3
VARIABLE = 4

#
# Symbols and Grammars
#

@dataclasses.dataclass(frozen=True)
class Symbol:
    """Data Class for Symbols."""
    type: int
    key: str
    value: Any
    priority: int = 0
    builtin: bool = False

class Grammar(set):
    """Base Class for Parser Grammars."""

    def get(self, tid: int) -> Dict[str, Symbol]:
        """Get symbols of given type.

        Args:
            tid: Integer parameter representing the type of symbols. Meaningfull
                types are given by module contants.

        Returns:
            OrderedDict containing Symbols in reverse lexical order to
            prioritize symbols with greater lenght.

        """
        symbols = iter((sym.key, sym) for sym in self if sym.type == tid)
        return collections.OrderedDict(sorted(symbols, reverse=True))

class PyCore(Grammar):
    """Python Expression Symbols.

    https://docs.python.org/3/reference/expressions.html

    """

    def __init__(self) -> None:
        super().__init__()

        bool_and: AnyOp = lambda a, b: a and b
        bool_or: AnyOp = lambda a, b: a or b
        bind: AnyOp = lambda a, b: a + [b] if isinstance(a, list) else [a, b]

        self.update([
            Symbol(BINARY, ',', bind, 13), # Sequence binding

            # Unary Operators
            Symbol(UNARY, '+', operator.pos, 11), # Positive (Arithmetic)
            Symbol(UNARY, '-', operator.neg, 11), # Negation (Arithmetic)
            Symbol(UNARY, '~', operator.invert, 11), # Bitwise Inversion

            # Binary Arithmetic Operators
            Symbol(BINARY, '**', operator.pow, 10), # Exponentiation
            Symbol(BINARY, '@', operator.matmul, 9), # Matrix Product
            Symbol(BINARY, '/', operator.truediv, 9), # Division
            Symbol(BINARY, '//', operator.floordiv, 9), # Floor Division
            Symbol(BINARY, '%', operator.mod, 9), # Remainder
            Symbol(BINARY, '*', operator.mul, 9), # Multiplication
            Symbol(BINARY, '+', operator.add, 8), # Addition
            Symbol(BINARY, '-', operator.sub, 8), # Subtraction

            # Binary Bitwise Operators
            Symbol(BINARY, '>>', operator.rshift, 7), # Bitwise Right Shift
            Symbol(BINARY, '<<', operator.lshift, 7), # Bitwise Left Shift
            Symbol(BINARY, '&', operator.and_, 6), # Bitwise AND
            Symbol(BINARY, '^', operator.xor, 5), # Bitwise XOR
            Symbol(BINARY, '|', operator.or_, 4), # Bitwise OR

            # Binary Ordering Operators
            Symbol(BINARY, '==', operator.eq, 3), # Equality
            Symbol(BINARY, '!=', operator.ne, 3), # Inequality
            Symbol(BINARY, '>', operator.gt, 3), # Greater
            Symbol(BINARY, '<', operator.lt, 3), # Lower
            Symbol(BINARY, '>=', operator.ge, 3), # Greater or Equal
            Symbol(BINARY, '<=', operator.le, 3), # Lower or Equal
            Symbol(BINARY, 'is', operator.is_, 3), # Identity
            Symbol(BINARY, 'in', operator.contains, 3), # Containment Test

            # Boolean Operators
            Symbol(UNARY, 'not', operator.not_, 2), # Boolean NOT
            Symbol(BINARY, 'and', bool_and, 1), # Boolean AND
            Symbol(BINARY, 'or', bool_or, 0)]) # Boolean OR

class PyBuiltins(PyCore):
    """Python Expression and Builtin Symbols."""

    def __init__(self) -> None:
        super().__init__()

        builtin = []
        for name in dir(builtins):
            # Filter protected Attributes
            if name.startswith('_'):
                continue

            # If the Attribute is callable, defined within builtins and not an
            # exception, append it as a function symbol to the grammar.
            obj = getattr(builtins, name)
            if callable(obj):
                if not hasattr(obj, '__module__'):
                    continue
                if not obj.__module__ == builtins.__name__:
                    continue
                if isinstance(obj, type) and issubclass(obj, BaseException):
                    continue
                builtin.append(Symbol(FUNCTION, name, obj, 12))
                continue

            # Append non-callable Attributes as constant symbols to the grammar.
            builtin.append(Symbol(CONSTANT, name, obj))

        self.update(builtin)

class Standard(Grammar):

    def __init__(self) -> None:
        super().__init__()

        rnd: AnyOp = lambda x: random.uniform(0., x)
        iif: AnyOp = lambda a, b, c: b if a else c
        concat: AnyOp = lambda *args: ''.join(map(str, args))
        iand: AnyOp = lambda a, b: a and b
        ior: AnyOp = lambda a, b: a or b
        append: AnyOp = lambda a, b: a + [b] if isinstance(a, list) else [a, b]

        self.update([
            Symbol(UNARY, '-', operator.neg, 0, True),
            Symbol(BINARY, '+', operator.add, 2, True),
            Symbol(BINARY, '-', operator.sub, 2, True),
            Symbol(BINARY, '*', operator.mul, 3, True),
            Symbol(BINARY, '/', operator.truediv, 4, True),
            Symbol(BINARY, '%', operator.mod, 4, True),
            Symbol(BINARY, '^', math.pow, 6, False), # nope
            Symbol(BINARY, '||', concat, 1, False), # nope
            Symbol(BINARY, '==', operator.eq, 1, True),
            Symbol(BINARY, '!=', operator.ne, 1, True),
            Symbol(BINARY, '>', operator.gt, 1, True),
            Symbol(BINARY, '<', operator.lt, 1, True),
            Symbol(BINARY, '>=', operator.ge, 1, True),
            Symbol(BINARY, '<=', operator.le, 1, True),
            Symbol(BINARY, ',', append, 0, True),
            Symbol(BINARY, 'and', iand, 0, True),
            Symbol(BINARY, 'or', ior, 0, True),
            Symbol(FUNCTION, 'abs', abs, 0, True),
            Symbol(FUNCTION, 'round', round, 0, True),
            Symbol(FUNCTION, 'min', min, 0, True),
            Symbol(FUNCTION, 'max', max, 0, True),
            Symbol(FUNCTION, 'sin', math.sin, 0, False),
            Symbol(FUNCTION, 'cos', math.cos, 0, False),
            Symbol(FUNCTION, 'tan', math.tan, 0, False),
            Symbol(FUNCTION, 'asin', math.asin, 0, False),
            Symbol(FUNCTION, 'acos', math.acos, 0, False),
            Symbol(FUNCTION, 'atan', math.atan, 0, False),
            Symbol(FUNCTION, 'sqrt', math.sqrt, 0, False),
            Symbol(FUNCTION, 'log', math.log, 0, False),
            Symbol(FUNCTION, 'ceil', math.ceil, 0, False),
            Symbol(FUNCTION, 'floor', math.floor, 0, False),
            Symbol(FUNCTION, 'exp', math.exp, 0, False),
            Symbol(FUNCTION, 'random', rnd, 0, False),
            Symbol(FUNCTION, 'fac', math.factorial, 0, False),
            Symbol(FUNCTION, 'pow', math.pow, 0, False),
            Symbol(FUNCTION, 'atan2', math.atan2, 0, False), # nope
            Symbol(FUNCTION, 'concat', concat, 0, False), # nope
            Symbol(FUNCTION, 'iif', iif, 0, False), # nope
            Symbol(CONSTANT, 'E', math.e, 0, False), # nope
            Symbol(CONSTANT, 'PI', math.pi, 0, False)]) # nope

#
# Tokens
#

@dataclasses.dataclass(frozen=True)
class Token:
    type: int
    key: Union[str, int] = 0
    priority: int = 0
    value: Any = 0

    def __str__(self) -> str:
        if self.type in [UNARY, BINARY, VARIABLE]:
            return str(self.key)
        if self.type == CONSTANT:
            return self.value
        if self.type == FUNCTION:
            return getattr(self.key, '__name__', 'CALL')
        return 'Invalid Token'

#
# Expressions
#

Unary = Dict[str, Callable[[Any], Any]]
Binary = Dict[str, Callable[[Any, Any], Any]]
Functions = Dict[str, Callable[..., Any]]

class Expression:
    tokens: List[Token]
    grammar: Grammar

    def __init__(
            self, expression: Optional[str] = None,
            tokens: Optional[List[Token]] = None,
            grammar: Optional[Grammar] = None) -> None:
        if expression:
            expr = Parser().parse(expression)
            self.tokens = expr.tokens
            self.grammar = expr.grammar
        elif tokens and grammar:
            self.tokens = tokens
            self.grammar = grammar

    def __call__(self, *args: Any) -> Any:
        return self.eval(*args)

    def __repr__(self) -> str:
        return f'{type(self).__name__}({repr(self.to_string())})'

    def __str__(self) -> str:
        return self.to_string()

    def simplify(self, values: Optional[dict] = None) -> 'Expression':
        values = values or {}
        stack = []
        tokens = []
        unary = self.grammar.get(UNARY)
        binary = self.grammar.get(BINARY)
        for tok in self.tokens:
            if tok.type == CONSTANT:
                stack.append(tok)
            elif tok.type == VARIABLE and tok.key in values:
                value = values[tok.key]
                stack.append(Token(CONSTANT, 0, 0, value))
            elif tok.type == BINARY and len(stack) > 1:
                if not isinstance(tok.key, str):
                    raise ValueError() #TODO
                b, a = stack.pop(), stack.pop()
                value = binary[tok.key].value(a.value, b.value)
                stack.append(Token(CONSTANT, 0, 0, value))
            elif tok.type == UNARY and stack:
                if not isinstance(tok.key, str):
                    raise ValueError() # TODO
                a = stack.pop()
                value = unary[tok.key].value(a.value)
                stack.append(Token(CONSTANT, 0, 0, value))
            else:
                while stack:
                    tokens.append(stack.pop(0))
                tokens.append(tok)
        while stack:
            tokens.append(stack.pop(0))
        return Expression(tokens=tokens, grammar=self.grammar)

    def subst(
            self, variable: str,
            expr: Union['Expression', str]) -> 'Expression':
        """Substitute variable in expression."""
        if not isinstance(expr, Expression):
            expr = Parser().parse(str(expr))
        tokens = []
        for tok in self.tokens:
            if tok.type != VARIABLE:
                tokens.append(tok)
                continue
            if tok.key != variable:
                tokens.append(tok)
                continue
            for etok in expr.tokens:
                repl = Token(etok.type, etok.key, etok.priority, etok.value)
                tokens.append(repl)
        return Expression(tokens=tokens, grammar=self.grammar)

    def eval(self, values: Optional[dict] = None) -> Any:
        values = values or {}
        stack = []
        unary = self.grammar.get(UNARY)
        binary = self.grammar.get(BINARY)
        functions = self.grammar.get(FUNCTION)
        for tok in self.tokens:
            if tok.type == CONSTANT:
                stack.append(tok.value)
            elif tok.type == BINARY and isinstance(tok.key, str):
                b, a = stack.pop(), stack.pop()
                stack.append(binary[tok.key].value(a, b))
            elif tok.type == VARIABLE and isinstance(tok.key, str):
                if tok.key in values:
                    stack.append(values[tok.key])
                elif tok.key in functions:
                    stack.append(functions[tok.key].value)
                else:
                    raise Exception(f"undefined variable '{tok.key}'")
            elif tok.type == UNARY and isinstance(tok.key, str):
                a = stack.pop()
                stack.append(unary[tok.key].value(a))
            elif tok.type == FUNCTION:
                a = stack.pop()
                func = stack.pop()
                if not callable(func):
                    raise Exception(f'{func} is not callable')
                if isinstance(a, list):
                    stack.append(func(*a))
                else:
                    stack.append(func(a))
            else:
                raise Exception('invalid expression')

        if len(stack) > 1:
            raise Exception('invalid expression (parity)')

        return stack[0]

    def to_string(self, python: bool = False) -> str:
        stack = []
        for tok in self.tokens:
            if tok.type == CONSTANT:
                if isinstance(tok.value, str):
                    stack.append(repr(tok.value))
                else:
                    stack.append(tok.value)
            elif tok.type == BINARY:
                b = stack.pop()
                a = stack.pop()
                f = tok.key
                if f == '^' and python:
                    stack.append(f'{a}**{b}')
                elif f == ',':
                    stack.append(f'{a}, {b}')
                else:
                    stack.append(f'({a}{f}{b})')
            elif tok.type == VARIABLE and isinstance(tok.key, str):
                stack.append(tok.key)
            elif tok.type == UNARY:
                a = stack.pop()
                f = tok.key
                if f == '-':
                    stack.append(f'(-{a})')
                else:
                    stack.append(f'{f}({a})')
            elif tok.type == FUNCTION:
                a = stack.pop()
                f = stack.pop()
                stack.append(f'{f}({a})')
            else:
                raise Exception('invalid expression')

        if len(stack) > 1:
            raise Exception('invalid expression (parity)')

        # Remove unnecessary parantheses
        rexpr = stack[0]
        if rexpr.startswith('(') and rexpr.endswith(')'):
            return rexpr[1:-1]

        return rexpr

    @property
    def symbols(self) -> List[str]:
        symlist: List[str] = []
        for tok in self.tokens:
            if tok.type != VARIABLE:
                continue
            if tok.key in symlist:
                continue
            if not isinstance(tok.key, str):
                raise ValueError() # TODO
            symlist.append(tok.key)
        return symlist

    @property
    def variables(self) -> List[str]:
        functions = self.grammar.get(FUNCTION)
        return [sym for sym in self.symbols if sym not in functions]

class Parser:
    PRIMARY = 1
    OPERATOR = 2
    FUNCTION = 4
    LPAREN = 8
    RPAREN = 16
    COMMA = 32
    SIGN = 64
    CALL = 128
    NULLARY = 256

    grammar: Grammar

    _expression: str
    _success: bool
    _errormsg: str
    _pos: int
    _cur_value: Union[str, float, int]
    _cur_priority: int
    _cur_name: Union[str, int]
    _tmp_priority: int

    def __init__(self, grammar: Optional[Grammar] = None) -> None:
        self.grammar = grammar or Standard()

        self._expression = ''
        self._success = False
        self._error = ''
        self._pos = 0
        self._cur_name = 0
        self._cur_value = 0
        self._cur_priority = 0
        self._tmp_priority = 0

    def __repr__(self) -> str:
        return f'{type(self).__name__}()'

    @property
    def success(self) -> bool:
        return self._success

    @property
    def expression(self) -> str:
        return self._expression

    def parse(self, expression: str) -> Expression:
        self._expression = expression
        self._error = ''
        self._success = True
        self._tmp_priority = 0
        self._pos = 0

        operators: List[Token] = []
        tokens: List[Token] = []
        expect = self.PRIMARY | self.LPAREN | self.FUNCTION | self.SIGN
        noperators = 0

        while self._pos < len(self._expression):
            if self._is_operator():
                if self._is_sign() and expect & self.SIGN:
                    if self._is_minus():
                        self._cur_priority = 5
                        self._cur_name = '-'
                        noperators += 1
                        self._add_operator(tokens, operators, UNARY)
                    expect = \
                        self.PRIMARY | self.LPAREN | self.FUNCTION | self.SIGN
                elif self._is_comment():
                    pass
                else:
                    if expect and self.OPERATOR == 0:
                        self._raise_error(self._pos, 'unexpect operator')
                    noperators += 2
                    self._add_operator(tokens, operators, BINARY)
                    expect = \
                        self.PRIMARY | self.LPAREN | self.FUNCTION | self.SIGN
            elif self._is_number():
                if expect and self.PRIMARY == 0:
                    self._raise_error(self._pos, 'unexpect number')
                tokens.append(Token(CONSTANT, 0, 0, self._cur_value))
                expect = self.OPERATOR | self.RPAREN | self.COMMA
            elif self._is_string():
                if (expect & self.PRIMARY) == 0:
                    self._raise_error(self._pos, 'unexpect string')
                tokens.append(Token(CONSTANT, 0, 0, self._cur_value))
                expect = self.OPERATOR | self.RPAREN | self.COMMA
            elif self._is_left_parenth():
                if (expect & self.LPAREN) == 0:
                    self._raise_error(self._pos, 'unexpect \"(\"')
                if expect & self.CALL:
                    noperators += 2
                    self._cur_priority = -2
                    self._cur_name = -1
                    self._add_operator(tokens, operators, FUNCTION)
                expect = \
                    self.PRIMARY | self.LPAREN | self.FUNCTION | \
                    self.SIGN | self.NULLARY
            elif self._is_right_parenth():
                if expect & self.NULLARY:
                    tok = Token(CONSTANT, 0, 0, [])
                    tokens.append(tok)
                elif (expect & self.RPAREN) == 0:
                    self._raise_error(self._pos, 'unexpect \")\"')
                expect = \
                    self.OPERATOR | self.RPAREN | self.COMMA | \
                    self.LPAREN | self.CALL
            elif self._is_comma():
                if (expect & self.COMMA) == 0:
                    self._raise_error(self._pos, 'unexpect \",\"')
                self._add_operator(tokens, operators, BINARY)
                noperators += 2
                expect = \
                    self.PRIMARY | self.LPAREN | self.FUNCTION | self.SIGN
            elif self._is_constant():
                if (expect & self.PRIMARY) == 0:
                    self._raise_error(self._pos, 'unexpect constant')
                tok = Token(CONSTANT, 0, 0, self._cur_value)
                tokens.append(tok)
                expect = self.OPERATOR | self.RPAREN | self.COMMA
            elif self._is_binary_operator():
                if (expect & self.FUNCTION) == 0:
                    self._raise_error(self._pos, 'unexpect function')
                self._add_operator(tokens, operators, BINARY)
                noperators += 2
                expect = self.LPAREN
            elif self._is_unary_operator():
                if (expect & self.FUNCTION) == 0:
                    self._raise_error(self._pos, 'unexpect function')
                self._add_operator(tokens, operators, UNARY)
                noperators += 1
                expect = self.LPAREN
            elif self._is_variable():
                if (expect & self.PRIMARY) == 0:
                    self._raise_error(
                        self._pos, f"unexpect variable '{self._cur_name}'")
                tokens.append(Token(VARIABLE, self._cur_name, 0, 0))
                expect = self.OPERATOR | self.RPAREN | self.COMMA \
                    | self.LPAREN | self.CALL
            elif self._is_space():
                pass
            else:
                if self._error == '':
                    self._raise_error(
                        self._pos, f"unknown character '{self._cur}'")
                else:
                    self._raise_error(self._pos, self._error)
        if self._tmp_priority < 0 or self._tmp_priority >= 10:
            self._raise_error(self._pos, 'unmatched \"()\"')
        while operators:
            tokens.append(operators.pop())
        if noperators + 1 != len(tokens):
            self._raise_error(self._pos, 'parity')

        return Expression(tokens=tokens, grammar=self.grammar)

    def eval(self, expression: str, variables: Optional[dict] = None) -> Any:
        return self.parse(expression).eval(variables)

    def _add_operator(
            self, tokens: List[Token], operators: List[Token],
            typeid: int) -> None:
        name = self._cur_name
        priority = self._cur_priority + self._tmp_priority
        tok = Token(typeid, name, priority, 0)
        while operators:
            if tok.priority > operators[-1].priority:
                break
            tokens.append(operators.pop())
        operators.append(tok)

    @property
    def _cur(self) -> str:
        return self._expression[self._pos]

    @property
    def _prev(self) -> str:
        return self._expression[self._pos - 1]

    def _is_number(self) -> bool:
        r = False
        string = ''
        while self._pos < len(self._expression):
            code = self._cur
            if code.isdecimal() or code == '.':
                if not string and code == '.':
                    string = '0'
                string += code
                self._pos += 1
                try:
                    self._cur_value = int(string)
                except ValueError:
                    self._cur_value = float(string)
                r = True
            else:
                break
        return r

    def _is_string(self) -> bool:
        r = False
        string = ''
        startpos = self._pos
        if self._pos < len(self._expression) and self._cur == "'":
            self._pos += 1
            while self._pos < len(self._expression):
                code = self._cur
                if code != '\'' or (string != '' and string[-1] == '\\'):
                    string += self._cur
                    self._pos += 1
                else:
                    self._pos += 1
                    self._cur_value = self._unescape(string, startpos)
                    r = True
                    break
        return r

    def _is_constant(self) -> bool:
        expr = self._expression
        constants = self.grammar.get(CONSTANT)
        for sym, const in constants.items():
            start = self._pos
            end = start + len(sym)
            if sym != expr[start:end]:
                continue
            if len(expr) <= end:
                self._cur_value = const.value
                self._pos = end
                return True
            if not expr[end].isalnum() and expr[end] != "_":
                self._cur_value = const.value
                self._pos = end
                return True
        return False

    def _is_operator(self) -> bool:
        for name, op in self.grammar.get(BINARY).items():
            if not self._expression.startswith(name, self._pos):
                continue
            self._cur_priority = op.priority
            self._cur_name = name
            self._pos += len(name)
            return True
        return False

    def _is_sign(self) -> bool:
        return self._prev in ['+', '-']

    def _is_plus(self) -> bool:
        return self._prev == '+'

    def _is_minus(self) -> bool:
        return self._prev == '-'

    def _is_left_parenth(self) -> bool:
        if self._cur != '(':
            return False
        self._pos += 1
        self._tmp_priority += 10
        return True

    def _is_right_parenth(self) -> bool:
        if self._cur != ')':
            return False
        self._pos += 1
        self._tmp_priority -= 10
        return True

    def _is_comma(self) -> bool:
        if self._cur != ',':
            return False
        self._pos += 1
        self._cur_priority = -1
        self._cur_name = ','
        return True

    def _is_space(self) -> bool:
        if not self._cur.isspace():
            return False
        self._pos += 1
        return True

    def _is_unary_operator(self) -> bool:
        string = ''
        for i, c in enumerate(self._expression[self._pos:]):
            if c.upper() == c.lower():
                if i == self._pos:
                    break
                if c != '_' and (c < '0' or c > '9'):
                    break
            string += c
        if string and string in self.grammar.get(UNARY):
            self._cur_name = string
            self._cur_priority = 7
            self._pos += len(string)
            return True
        return False

    def _is_binary_operator(self) -> bool:
        string = ''
        for i, c in enumerate(self._expression[self._pos:]):
            if c.upper() == c.lower():
                if i == self._pos:
                    break
                if c != '_' and (c < '0' or c > '9'):
                    break
            string += c
        if string and string in self.grammar.get(BINARY):
            self._cur_name = string
            self._cur_priority = 7
            self._pos += len(string)
            return True
        return False

    def _is_variable(self) -> bool:
        string = ''
        quoted = False
        for i in range(self._pos, len(self._expression)):
            c = self._expression[i]
            if not quoted and (c.lower() == c.upper()):
                if (c not in '_."') and (c < '0' or c > '9'):
                    break
                if i == self._pos and c != '"':
                    break
            if c == '"':
                quoted = not quoted
            string += c
        if string:
            self._cur_name = string
            self._cur_priority = 4
            self._pos += len(string)
            return True
        return False

    def _is_comment(self) -> bool: # TODO: DO NOT USE COMMENTS
        if self._prev == '/' and self._cur == '*':
            self._pos = self._expression.index('*/', self._pos) + 2
            if self._pos == 1:
                self._pos = len(self._expression)
            return True
        return False

    def _raise_error(self, column: int, msg: str) -> None:
        self._success = False
        self._error = f'parse error [column {column}]: {msg}'
        raise ValueError(self._error)

    def _unescape(self, string: str, pos: int) -> str:
        encoding = env.get_var('encoding') or 'UTF-8'
        return string.encode(encoding).decode('unicode_escape')

#
# Workarounds
#

OptVars = Optional[stype.Frame]

def parse(expr: str, variables: OptVars = None) -> Expression:
    if variables:
        vmap = get_var_mapping(expr, variables)
        expr = subst(expr, vmap)

    return Parser().parse(expr).simplify({})

def get_var_mapping(expr: str, variables: OptVars = None) -> dict:
    if not variables:
        return {}

    # Create an operator that checks, if a given variable name <var> is
    # already occupied by the expression. Thereby ignore appearances within
    # quoted (single or double) terms.
    quoted = "\"[^\"]+\"|'[^']+'" # RegEx for quoted terms
    raw = quoted + "|(?P<var>{var})" # Unformated RegEx for matches
    fmt: AnyOp = lambda var: raw.format(var=re.escape(var))
    matches: AnyOp = lambda var: re.finditer(fmt(var), expr)
    hit: AnyOp = lambda obj: obj.group('var') # Test if match is a var
    occupied: AnyOp = lambda var: any(map(hit, matches(var)))

    # Use the operator to create a field mapping from the set of field IDs
    # in the frame to valid variable names.
    fields = set(variables)
    mapping: Dict[stype.FieldID, str] = {}
    var_counter = itertools.count()
    next_var: AnyOp = lambda: 'X{i}'.format(i=next(var_counter))
    for field in fields:
        if isinstance(field, str) and field.isidentifier():
            mapping[field] = field
            continue
        var_name = next_var()
        while occupied(var_name):
            var_name = next_var()
        mapping[field] = var_name

    # Create and return variable mapping
    get_var: AnyOp = lambda field: mapping.get(field, '')
    return dict(zip(variables, map(get_var, variables)))

def subst(expr: str, mapping: dict) -> str:
    # Declare replacement function
    def repl(mo: Match) -> str:
        if mo.group('var'):
            return mapping.get(mo.group('var'), mo.group('var'))
        if mo.group('str2'):
            return mo.group('str2')
        return mo.group('str1')

    # Build operator that creates an regex pattern for a given field ID
    re_str1 = "(?P<str1>\"[^\"]+\")" # RegEx for double quoted terms
    re_str2 = "(?P<str2>'[^']+')" # RegEx for single quoted terms
    re_var = "(?P<var>{var})" # Unformated RegEx for variable
    raw = '|'.join([re_str1, re_str2, re_var]) # Unformated RegEx
    pattern: AnyOp = lambda var: raw.format(var=re.escape(var))

    # Iterate all field ids and succesively replace invalid variable names
    new_expr = expr
    for field, var in mapping.items():
        if field == var:
            continue
        new_expr = re.sub(pattern(field), repl, new_expr)

    return new_expr
