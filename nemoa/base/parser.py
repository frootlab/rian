# -*- coding: utf-8 -*-
# Copyright (c) 2019 Patrick Michl
# Copyright (c) 2014-2019 AxiaCore S.A.S.
#
# §1 This file is part of nemoa, https://frootlab.github.io
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
# §2 Parts of this file are based on py-expression-eval, 0.3.6
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
"""Generic Expression Parser."""

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
from typing import Any, Callable, Dict, List, Match, Optional, Tuple, Union
from nemoa.base import check, env, stype
from nemoa.types import AnyOp

OptVars = Optional[stype.Frame]

UNARY = 0
BINARY = 1
FUNCTION = 2
CONSTANT = 3
VARIABLE = 4

class _Pack(list):
    """Protected Class for packed arguments."""

class _Null:
    """Protected Sentinel Class for no arguments."""

def _pack(a: Any, b: Any) -> _Pack:
    if isinstance(a, list):
        return _Pack(a + [b])
    return _Pack([a, b])

#
# Symbols and Vocabularies
#

@dataclasses.dataclass(frozen=True)
class Symbol:
    """Data Class for Symbols."""
    type: int
    key: str
    value: Any
    priority: int = 0
    builtin: bool = False

    def __post_init__(self) -> None:
        check.has_type('type', self.type, int)
        check.has_type('key', self.key, str)
        if not self.type in [CONSTANT, VARIABLE]:
            check.is_callable('value', self.value)
        check.has_type('priority', self.priority, int)
        check.has_type('builtin', self.builtin, bool)

class Vocabulary(set):
    """Base Class for Parser Vocabularies."""

    def get(
            self, sid: int,
            builtin: Optional[bool] = None) -> Dict[str, Symbol]:
        """Get symbols of given type.

        Args:
            sid: Integer parameter representing the type of symbols. Meaningfull
                types are given by module contants.
            builtin: Boolean parameter, which determines if ...

        Returns:
            OrderedDict containing Symbols in reverse lexical order to
            prioritize symbols with greater lenght.

        """
        # Filter by type
        key: AnyOp = lambda sym: sym.type == sid
        symbols = filter(key, self)

        # Optionally filter by builtin
        if builtin is not None:
            key = lambda sym: sym.builtin == builtin
            symbols = filter(key, symbols)

        # Create and return OrderedDict in reverse sort order to prioritize
        # longer sombols
        items = iter((sym.key, sym) for sym in symbols)
        return collections.OrderedDict(sorted(items, reverse=True))

class PyOperators(Vocabulary):
    """Python3 Operators.

    This vocabulary is based on
    https://docs.python.org/3/reference/expressions.html

    Hint:
        In difference to standard Python interpreter, some expressions are not
        valid: Invalid: x + -y -> Valid: x + (-y)

    """

    def __init__(self) -> None:
        super().__init__()

        bool_and: AnyOp = lambda a, b: a and b
        bool_or: AnyOp = lambda a, b: a or b
        is_in: AnyOp = lambda a, b: operator.contains(b, a)

        self.update([
            # Binding Operators
            Symbol(BINARY, ',', _pack, 13), # Sequence packing

            # Arithmetic Operators
            Symbol(UNARY, '+', operator.pos, 11), # Unary Plus
            Symbol(UNARY, '-', operator.neg, 11), # Negation
            Symbol(BINARY, '**', operator.pow, 10), # Exponentiation
            Symbol(BINARY, '@', operator.matmul, 9), # Matrix Product
            Symbol(BINARY, '/', operator.truediv, 9), # Division
            Symbol(BINARY, '//', operator.floordiv, 9), # Floor Division
            Symbol(BINARY, '%', operator.mod, 9), # Remainder
            Symbol(BINARY, '*', operator.mul, 9), # Multiplication
            Symbol(BINARY, '+', operator.add, 8), # Addition
            Symbol(BINARY, '-', operator.sub, 8), # Subtraction

            # Bitwise Operators
            Symbol(UNARY, '~', operator.invert, 11), # Bitwise Inversion
            Symbol(BINARY, '>>', operator.rshift, 7), # Bitwise Right Shift
            Symbol(BINARY, '<<', operator.lshift, 7), # Bitwise Left Shift
            Symbol(BINARY, '&', operator.and_, 6), # Bitwise AND
            Symbol(BINARY, '^', operator.xor, 5), # Bitwise XOR
            Symbol(BINARY, '|', operator.or_, 4), # Bitwise OR

            # Comparison Operators
            Symbol(BINARY, '==', operator.eq, 3), # Equality
            Symbol(BINARY, '!=', operator.ne, 3), # Inequality
            Symbol(BINARY, '>', operator.gt, 3), # Greater
            Symbol(BINARY, '<', operator.lt, 3), # Lower
            Symbol(BINARY, '>=', operator.ge, 3), # Greater or Equal
            Symbol(BINARY, '<=', operator.le, 3), # Lower or Equal
            Symbol(BINARY, 'is', operator.is_, 3), # Identity
            Symbol(BINARY, 'in', is_in, 3), # Containment

            # Logical Operators
            Symbol(UNARY, 'not', operator.not_, 2), # Boolean NOT
            Symbol(BINARY, 'and', bool_and, 1), # Boolean AND
            Symbol(BINARY, 'or', bool_or, 0)]) # Boolean OR

class PyBuiltin(PyOperators):
    """Python3 Operators and Builtins."""

    def __init__(self) -> None:
        super().__init__()

        builtin = []
        for name in dir(builtins):
            # Filter protected Attributes
            if name.startswith('_'):
                continue

            # If the Attribute is callable, defined within builtins and not an
            # exception, append it as a function symbol to the vocabulary.
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

            # Append non-callable Attributes as constant symbols to the
            # vocabulary.
            builtin.append(Symbol(CONSTANT, name, obj))

        self.update(builtin)

class PyExprEval(Vocabulary):
    """Symbols used by py-expression-eval."""

    def __init__(self) -> None:
        super().__init__()

        rnd: AnyOp = lambda x: random.uniform(0., x)
        iif: AnyOp = lambda a, b, c: b if a else c
        concat: AnyOp = lambda *args: ''.join(map(str, args))
        iand: AnyOp = lambda a, b: a and b
        ior: AnyOp = lambda a, b: a or b

        self.update([
            # Sequence Operators
            Symbol(BINARY, ',', _pack, 0, True),
            Symbol(BINARY, '||', concat, 1, False),

            # Arithmetic Operators
            Symbol(UNARY, '-', operator.neg, 0, True),
            Symbol(BINARY, '+', operator.add, 2, True),
            Symbol(BINARY, '-', operator.sub, 2, True),
            Symbol(BINARY, '*', operator.mul, 3, True),
            Symbol(BINARY, '/', operator.truediv, 4, True),
            Symbol(BINARY, '%', operator.mod, 4, True),
            Symbol(BINARY, '^', math.pow, 6, False),

            # Ordering Operators
            Symbol(BINARY, '==', operator.eq, 1, True),
            Symbol(BINARY, '!=', operator.ne, 1, True),
            Symbol(BINARY, '>', operator.gt, 1, True),
            Symbol(BINARY, '<', operator.lt, 1, True),
            Symbol(BINARY, '>=', operator.ge, 1, True),
            Symbol(BINARY, '<=', operator.le, 1, True),

            # Boolean Operators
            Symbol(BINARY, 'and', iand, 0, True),
            Symbol(BINARY, 'or', ior, 0, True),

            # Functions
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
            Symbol(FUNCTION, 'atan2', math.atan2, 0, False),
            Symbol(FUNCTION, 'if', iif, 0, False),
            Symbol(FUNCTION, 'concat', concat, 0, False),

            # Constants
            Symbol(CONSTANT, 'E', math.e, 0, False),
            Symbol(CONSTANT, 'PI', math.pi, 0, False)])

#
# Tokens
#

@dataclasses.dataclass(frozen=True)
class Token:
    type: int
    id: Union[str, int] = 0
    priority: int = 0
    value: Any = 0
    key: str = ''

    def __str__(self) -> str:
        if self.type in [UNARY, BINARY, VARIABLE]:
            return self.key or str(self.id)
        if self.type == FUNCTION:
            return self.key or getattr(self.id, '__name__', 'CALL')
        if self.type == CONSTANT:
            return self.key
        return 'Invalid Token'

#
# Expressions
#

class Expression:
    tokens: List[Token]
    vocabulary: Vocabulary
    mapping: dict

    _symbols: Tuple[str, ...]
    _variables: Tuple[str, ...]
    _origin: Tuple[str, ...]

    def __init__(
            self, expression: Optional[str] = None,
            tokens: Optional[List[Token]] = None,
            vocabulary: Optional[Vocabulary] = None,
            mapping: Optional[dict] = None) -> None:
        self._symbols = tuple()
        self._variables = tuple()
        self._origin = tuple()

        if expression:
            expr = Parser(vocabulary).parse(expression)
            self.tokens = expr.tokens
            self.vocabulary = expr.vocabulary
            self.mapping = expr.mapping
        elif tokens and vocabulary:
            self.tokens = tokens
            self.vocabulary = vocabulary
            self.mapping = mapping or {}

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.eval(*args, **kwds)

    def __repr__(self) -> str:
        return f'{type(self).__name__}({repr(self.as_string())})'

    def __str__(self) -> str:
        return self.as_string()

    def simplify(self, values: Optional[dict] = None) -> 'Expression':
        values = values or {}
        stack = []
        tokens = []

        unary = self.vocabulary.get(UNARY)
        binary = self.vocabulary.get(BINARY)

        for tok in self.tokens:
            if tok.type == CONSTANT:
                stack.append(tok)
            elif tok.type == VARIABLE and tok.id in values:
                value = values[tok.id]
                stack.append(Token(CONSTANT, 0, 0, value, tok.key))
            elif tok.type == BINARY and len(stack) > 1:
                if not isinstance(tok.id, str):
                    raise ValueError() #TODO
                b, a = stack.pop(), stack.pop()
                value = binary[tok.id].value(a.value, b.value)
                stack.append(Token(CONSTANT, 0, 0, value, tok.key))
            elif tok.type == UNARY and stack:
                if not isinstance(tok.id, str):
                    raise ValueError() # TODO
                a = stack.pop()
                value = unary[tok.id].value(a.value)
                stack.append(Token(CONSTANT, 0, 0, value, tok.key))
            else:
                while stack:
                    tokens.append(stack.pop(0))
                tokens.append(tok)
        while stack:
            tokens.append(stack.pop(0))
        return Expression(
            tokens=tokens, vocabulary=self.vocabulary, mapping=self.mapping)

    def subst(self, key: str, expr: Union['Expression', str]) -> 'Expression':
        """Substitute variable in expression."""
        if not isinstance(expr, Expression):
            expr = Parser().parse(str(expr))
        tokens = []
        copy: AnyOp = lambda obj: dataclasses.replace(obj)
        for tok in self.tokens:
            if tok.type != VARIABLE or tok.key != key:
                tokens.append(tok)
                continue
            for etok in expr.tokens:
                tokens.append(copy(etok))
        return Expression(
            tokens=tokens, vocabulary=self.vocabulary, mapping=self.mapping)

    def eval(self, *args: Any, **kwds: Any) -> Any:
        values = dict(zip(self.variables, args))
        values.update(kwds)
        stack = []
        unary = self.vocabulary.get(UNARY)
        binary = self.vocabulary.get(BINARY)
        functions = self.vocabulary.get(FUNCTION)
        for tok in self.tokens:
            if tok.type == CONSTANT:
                stack.append(tok.value)
            elif tok.type == BINARY and isinstance(tok.id, str):
                b, a = stack.pop(), stack.pop()
                stack.append(binary[tok.id].value(a, b))
            elif tok.type == VARIABLE and isinstance(tok.id, str):
                if tok.id in values:
                    stack.append(values[tok.id])
                elif tok.id in functions:
                    stack.append(functions[tok.id].value)
                else:
                    raise Exception(f"undefined variable '{tok.id}'")
            elif tok.type == UNARY and isinstance(tok.id, str):
                a = stack.pop()
                stack.append(unary[tok.id].value(a))
            elif tok.type == FUNCTION:
                a = stack.pop()
                func = stack.pop()
                if not callable(func):
                    raise Exception(f'{func} is not callable')
                if isinstance(a, _Pack):
                    stack.append(func(*a))
                elif isinstance(a, _Null):
                    stack.append(func())
                else:
                    stack.append(func(a))
            else:
                raise Exception('invalid expression')

        if len(stack) > 1:
            raise Exception('invalid expression (parity)')

        return stack[0]

    def as_func(self, compile: bool = True) -> Callable:
        """ """
        if not compile:
            return self.eval

        vocabulary = self.vocabulary

        # Get a string representation of the expression, which replaces all not
        # builtin operators by surrogate functions.
        translate = self._get_surrogates()
        string = self.as_string(translate=translate)

        # Create globals dictionary, which includes all functions, that are
        # found in the vocabulary and surrogate functions for not builtin
        # operators and constants
        glob = {'__builtins__': None}
        symbols = vocabulary.get(FUNCTION)
        for key, sym in symbols.items():
            glob[key] = sym.value
        for sid in [UNARY, BINARY, CONSTANT]:
            symbols = vocabulary.get(sid, builtin=False)
            for key, sur in translate[sid].items():
                glob[sur] = symbols[key].value

        # Create lambda term
        term = f"lambda {','.join(self.variables)}:{string}"
        return eval(term, glob) # pylint: disable=W0123

    def as_string(self, translate: Optional[dict] = None) -> str:
        """ """
        voc = translate or {}
        voc_constant = voc.get(CONSTANT, {})
        voc_binary = voc.get(BINARY, {})
        voc_unary = voc.get(UNARY, {})
        voc_function = voc.get(FUNCTION, {})

        stack = []
        for tok in self.tokens:
            if tok.type == CONSTANT:
                if tok.key in voc_constant:
                    stack.append(f'{voc_constant[tok.key]}')
                else:
                    stack.append(tok.key)
            elif tok.type == BINARY:
                b = stack.pop()
                a = stack.pop()
                f = tok.id
                if f == ',':
                    stack.append(f'{a}, {b}')
                elif f in voc_binary:
                    stack.append(f'{voc_binary[f]}({a}, {b})')
                else:
                    stack.append(f'({a} {f} {b})')
            elif tok.type == VARIABLE and isinstance(tok.id, str):
                stack.append(tok.id)
            elif tok.type == UNARY:
                a = stack.pop()
                f = tok.id
                if f == '-':
                    stack.append(f'(-{a})')
                elif f in voc_unary:
                    stack.append(f'{voc_unary[f]}({a})')
                else:
                    stack.append(f'{f}({a})')
            elif tok.type == FUNCTION:
                a = stack.pop()
                f = stack.pop()
                if f in voc_function:
                    stack.append(f'{voc_function[f]}({a})')
                else:
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
    def symbols(self) -> Tuple[str, ...]:
        if self._symbols:
            return self._symbols

        symlist: List[str] = []
        for tok in self.tokens:
            if tok.type != VARIABLE:
                continue
            if tok.id in symlist:
                continue
            if not isinstance(tok.id, str):
                raise ValueError() # TODO
            symlist.append(tok.id)
        self._symbols = tuple(symlist)
        return self._symbols

    @property
    def variables(self) -> Tuple[str, ...]:
        if self._variables:
            return self._variables

        funcs = self.vocabulary.get(FUNCTION)
        self._variables = tuple(sym for sym in self.symbols if sym not in funcs)
        return self._variables

    @property
    def origin(self) -> Tuple[str, ...]:
        if self._origin:
            return self._origin

        invert = dict((v, f) for f, v in self.mapping.items())
        self._origin = tuple(invert.get(v, v) for v in self.variables)
        return self._origin

    def _get_surrogates(self) -> dict:
        # Search vocabulary for non-builtin symbols
        vocabulary = self.vocabulary
        occupied = set(sym.key for sym in vocabulary).union(self.symbols)
        translation: Dict[int, Dict[str, str]] = {}
        nextkey: Callable[[], str]

        # Create surrogates for unary operators
        counter = itertools.count()
        nextkey = lambda: 'u{i}'.format(i=next(counter))
        translation[UNARY] = {}
        for key in vocabulary.get(UNARY, builtin=False):
            newkey = nextkey()
            while newkey in occupied:
                newkey = nextkey()
            translation[UNARY][key] = newkey

        # Create surrogates for binary operators
        counter = itertools.count()
        nextkey = lambda: 'b{i}'.format(i=next(counter))
        translation[BINARY] = {}
        for key in vocabulary.get(BINARY, builtin=False):
            newkey = nextkey()
            while newkey in occupied:
                newkey = nextkey()
            translation[BINARY][key] = newkey

        # Create surrogates for constants
        counter = itertools.count()
        nextkey = lambda: 'C{i}'.format(i=next(counter))
        translation[CONSTANT] = {}
        for key in vocabulary.get(CONSTANT, builtin=False):
            newkey = nextkey()
            while newkey in occupied:
                newkey = nextkey()
            translation[CONSTANT][key] = newkey

        return translation

class Parser:
    PRIM = 1
    OPER = 2
    FUNC = 4
    LEFT = 8
    RIGHT = 16
    COMMA = 32
    SIGN = 64
    CALL = 128
    NULL = 256

    vocabulary: Vocabulary
    _unary: dict
    _binary: dict

    _expression: str
    _mapping: dict
    _success: bool
    _errormsg: str
    _cur_pos: int
    _cur_id: Union[int, str]
    _cur_key: str
    _cur_val: Any
    _cur_priority: int
    _tmp_priority: int

    def __init__(self, vocabulary: Optional[Vocabulary] = None) -> None:
        self.vocabulary = vocabulary or PyOperators()

        self._expression = ''
        self._mapping = {}
        self._success = False
        self._error = ''
        self._cur_pos = 0
        self._cur_id = 0
        self._cur_key = ''
        self._cur_val = 0
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

    def parse(self, expression: str, variables: OptVars = None) -> Expression:
        # The given variables are not required to be valid variable names to the
        # parser. In such a case all unquoted variables are exchanged by
        # surrogates
        if variables:
            mapping = self._get_mapping(expression, variables)
            expression = self._replace_vars(expression, mapping)
        else:
            mapping = {}

        self._expression = expression
        self._error = ''
        self._success = True
        self._cur_pos = 0
        self._cur_val = 0
        self._cur_priority = 0
        self._tmp_priority = 0

        # Update dictionaries with unary and binary operators
        self._unary = self.vocabulary.get(UNARY)
        self._binary = self.vocabulary.get(BINARY)

        operators: List[Token] = []
        tokens: List[Token] = []
        expect = self.PRIM | self.LEFT | self.FUNC | self.SIGN
        nops = 0

        while self._cur_pos < len(self._expression):
            if self._is_operator():
                if self._is_sign() and expect & self.SIGN:
                    if self._is_minus():
                        self._cur_priority = 5
                        self._cur_id = '-'
                        self._cur_key = '-'
                        nops += 1
                        self._add_operator(tokens, operators, UNARY)
                    expect = self.PRIM | self.LEFT | self.FUNC | self.SIGN
                else:
                    if expect and self.OPER == 0:
                        self._raise_error('unexpect operator')
                    nops += 2
                    self._add_operator(tokens, operators, BINARY)
                    expect = self.PRIM | self.LEFT | self.FUNC | self.SIGN
            elif self._is_unary_sign():
                key = self._cur_key
                if not expect & self.SIGN:
                    self._raise_error(f"unexpected unary operator '{key}'")
                nops += 1
                self._add_operator(tokens, operators, UNARY)
                expect = self.PRIM | self.LEFT | self.FUNC | self.SIGN
            elif self._is_number():
                if not expect & self.PRIM:
                    self._raise_error('unexpected number')
                key, val = self._cur_key, self._cur_val
                tokens.append(Token(CONSTANT, 0, 0, val, key))
                expect = self.OPER | self.RIGHT | self.COMMA
            elif self._is_string():
                if not expect & self.PRIM:
                    self._raise_error('unexpected string')
                key, val = self._cur_key, self._cur_val
                tokens.append(Token(CONSTANT, 0, 0, val, key))
                expect = self.OPER | self.RIGHT | self.COMMA
            elif self._is_left():
                if not expect & self.LEFT:
                    self._raise_error('unexpected \"(\"')
                if expect & self.CALL:
                    nops += 2
                    self._cur_priority = -2
                    self._cur_id = -1
                    self._add_operator(tokens, operators, FUNCTION)
                expect = \
                    self.PRIM | self.LEFT | self.FUNC | \
                    self.SIGN | self.NULL
            elif self._is_right():
                if expect & self.NULL:
                    tokens.append(Token(CONSTANT, 0, 0, _Null(), ''))
                elif not expect & self.RIGHT:
                    self._raise_error('unexpected \")\"')
                expect = \
                    self.OPER | self.RIGHT | self.COMMA | \
                    self.LEFT | self.CALL
            elif self._is_comma():
                if not expect & self.COMMA:
                    self._raise_error('unexpected \",\"')
                self._add_operator(tokens, operators, BINARY)
                nops += 2
                expect = self.PRIM | self.LEFT | self.FUNC | self.SIGN
            elif self._is_constant():
                if not expect & self.PRIM:
                    self._raise_error('unexpected constant')
                key, val = self._cur_key, self._cur_val
                tokens.append(Token(CONSTANT, 0, 0, val, key))
                expect = self.OPER | self.RIGHT | self.COMMA
            elif self._is_binary_operator():
                key = self._cur_key
                if not expect & self.FUNC:
                    self._raise_error(f"unexpected function '{key}'")
                self._add_operator(tokens, operators, BINARY)
                nops += 2
                expect = self.LEFT
            elif self._is_unary_operator():
                key = self._cur_key
                if not expect & self.FUNC:
                    self._raise_error(f"unexpected unary operator '{key}'")
                self._add_operator(tokens, operators, UNARY)
                nops += 1
                expect = self.LEFT
            elif self._is_variable():
                index = self._cur_id
                key = self._cur_key
                if not expect & self.PRIM:
                    self._raise_error(f"unexpect variable '{key}'")
                tokens.append(Token(VARIABLE, index, 0, 0, key))
                expect = self.OPER | self.RIGHT | self.COMMA \
                    | self.LEFT | self.CALL
            elif self._is_space():
                pass
            else:
                if self._error:
                    self._raise_error(self._error)
                self._raise_error(f"unknown character '{self._cur_char}'")
        if self._tmp_priority < 0 or self._tmp_priority >= 100:
            self._raise_error('unmatched \"()\"')
        while operators:
            tokens.append(operators.pop())
        if nops + 1 != len(tokens):
            self._raise_error('parity')

        return Expression(
            tokens=tokens, vocabulary=self.vocabulary, mapping=mapping)

    def eval(self, expression: str, *args: Any, **kwds: Any) -> Any:
        return self.parse(expression).eval(*args, **kwds)

    def _add_operator(
            self, tokens: List[Token], operators: List[Token],
            typeid: int) -> None:
        priority = self._cur_priority + self._tmp_priority
        while operators:
            if priority > operators[-1].priority:
                break
            tokens.append(operators.pop())
        index = self._cur_id
        key = self._cur_key
        operators.append(Token(typeid, index, priority, key))

    @property
    def _cur_char(self) -> str:
        return self._expression[self._cur_pos]

    @property
    def _prev(self) -> str:
        return self._expression[self._cur_pos - 1]

    def _is_number(self) -> bool:
        key = ''
        while self._cur_pos < len(self._expression):
            c = self._cur_char
            if not c.isdecimal() and c != '.':
                break
            if not key and c == '.':
                key = '0'
            key += c
            self._cur_pos += 1
        if key:
            try:
                self._cur_val = int(key)
            except ValueError:
                self._cur_val = float(key)
            self._cur_id = key
            self._cur_key = key
            return True
        return False

    def _is_string(self) -> bool:
        r = False
        key = ''
        start = self._cur_pos
        if self._cur_pos < len(self._expression) and self._cur_char == "'":
            self._cur_pos += 1
            while self._cur_pos < len(self._expression):
                if self._cur_char != '\'' or (key and key[-1] == '\\'):
                    key += self._cur_char
                    self._cur_pos += 1
                else:
                    self._cur_pos += 1
                    self._cur_val = self._unescape(key, start)
                    r = True
                    break
        self._cur_key = repr(key)
        self._cur_id = repr(key)
        return r

    def _is_constant(self) -> bool:
        expr = self._expression
        for key, sym in self.vocabulary.get(CONSTANT).items():
            start = self._cur_pos
            end = start + len(key)
            if key != expr[start:end]:
                continue
            if len(expr) <= end: # TODO: Whats the sense?
                self._cur_val = sym.value
                self._cur_pos = end
                self._cur_key = key
                self._cur_id = key
                return True
            if not expr[end].isalnum() and expr[end] != "_":
                self._cur_val = sym.value
                self._cur_pos = end
                self._cur_key = key
                self._cur_id = key
                return True
        return False

    def _is_unary_sign(self) -> bool:

        # Check if operator is a unary sign operator
        for key, symbol in self._unary.items():
            if any(map(str.isalnum, key)):
                continue
            if not self._expression.startswith(key, self._cur_pos):
                continue

            self._cur_priority = symbol.priority
            self._cur_key = key
            self._cur_id = key
            self._cur_pos += len(key)

            return True
        return False

    def _is_operator(self) -> bool:

        # Check if operator is a binary operator
        for key, symbol in self._binary.items():
            if not self._expression.startswith(key, self._cur_pos):
                continue

            # If the last letter of the binary operator is alphanumerical or
            # contains alphanumerical letters, then the following character is
            # not allowed to be alphanumerical
            if key[-1].isalnum() or key[-1] in '_"':
                next_char = self._expression[self._cur_pos + len(key)]
                if next_char.isalnum() or next_char in '_"':
                    continue

            self._cur_priority = symbol.priority
            self._cur_id = key
            self._cur_key = key
            self._cur_pos += len(key)

            return True

        return False

    def _is_sign(self) -> bool:
        return self._prev in ['+', '-']

    def _is_minus(self) -> bool:
        return self._prev == '-'

    def _is_left(self) -> bool:
        if self._cur_char != '(':
            return False
        self._cur_pos += 1
        self._tmp_priority += 100
        return True

    def _is_right(self) -> bool:
        if self._cur_char != ')':
            return False
        self._cur_pos += 1
        self._tmp_priority -= 100
        return True

    def _is_comma(self) -> bool:
        if self._cur_char != ',':
            return False
        self._cur_pos += 1
        self._cur_priority = -1
        self._cur_id = ','
        self._cur_key = ','
        return True

    def _is_space(self) -> bool:
        if not self._cur_char.isspace():
            return False
        self._cur_pos += 1
        return True

    def _is_unary_operator(self) -> bool:
        key = self._cur_char
        if not key.isalpha():
            return False
        for c in self._expression[self._cur_pos + 1:]:
            if c.isalnum() or c == '_':
                key += c
                continue
            break
        if not key in self._unary:
            return False
        self._cur_id = key
        self._cur_key = key
        self._cur_priority = self._unary[key].priority
        self._cur_pos += len(key)

        return True

    def _is_binary_operator(self) -> bool:
        key = self._cur_char
        if not key.isalpha():
            return False
        for c in self._expression[self._cur_pos + 1:]:
            if c.isalnum() or c == '_':
                key += c
                continue
            break
        binary = self._binary
        if not key in binary:
            return False
        symbol = binary[key]
        self._cur_id = key
        self._cur_key = key
        self._cur_priority = symbol.priority
        self._cur_pos += len(key)

        return True

    def _is_variable(self) -> bool:
        key = ''
        quoted = False
        pos = self._cur_pos
        for i, c in enumerate(self._expression[self._cur_pos:]):
            if not quoted and not c.isalpha():
                if c not in '_."' and not c.isdecimal():
                    break
                if not i and c != '"':
                    break
            if c == '"':
                quoted = not quoted
            key += c
        if not key:
            return False

        self._cur_id = key
        self._cur_key = key
        self._cur_priority = 0 # 4 / WHY
        self._cur_pos += len(key)
        return True

    def _get_mapping(self, expr: str, variables: OptVars = None) -> dict:
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

    def _replace_vars(self, expression: str, mapping: dict) -> str:
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
        new_expr = expression
        for field, var in mapping.items():
            if field == var:
                continue
            new_expr = re.sub(pattern(field), repl, new_expr)

        return new_expr

    def _raise_error(self, msg: str) -> None:
        self._success = False
        self._error = f'parse error [column {self._cur_pos}]: {msg}'
        raise ValueError(self._error)

    def _unescape(self, key: str, pos: int) -> str:
        encoding = env.get_var('encoding') or 'UTF-8'
        return key.encode(encoding).decode('unicode_escape')

#
# Constructor
#

def parse(
        expression: str, variables: OptVars = None,
        vocabulary: Optional[Vocabulary] = None) -> Expression:
    parser = Parser(vocabulary)
    return parser.parse(expression, variables=variables)
