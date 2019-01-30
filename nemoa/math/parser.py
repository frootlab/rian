# -*- coding: utf-8 -*-
#
# Copyright (C) 2019, Patrick Michl
# Copyright (C) 2014-2019, AxiaCore S.A.S.
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
"""Arithmetic Expression Parser."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import dataclasses
import itertools
import math
import operator
import random
import re
from typing import Any, Callable, Dict, List, Match, Optional, Union
from nemoa.base import stype
from nemoa.types import AnyOp

OptVars = Optional[stype.Frame]

#
# Tokens
#

NUMBER_TYPE = 0
UNARY_TYPE = 1
BINARY_TYPE = 2
VARIABLE_TYPE = 3
FUNCTION_TYPE = 4

@dataclasses.dataclass(frozen=True)
class Token:
    type: int
    name: Union[str, int] = 0
    priority: int = 0
    value: Any = 0

    def __str__(self) -> str:
        if self.type == NUMBER_TYPE:
            return self.value
        if self.type in [UNARY_TYPE, BINARY_TYPE, VARIABLE_TYPE]:
            if not isinstance(self.name, str):
                raise ValueError() # TODO
            return self.name
        if self.type == FUNCTION_TYPE:
            return 'CALL'
        return 'Invalid Token'

#
# Expressions
#

class Expression:

    def __init__(
            self, tokens: List[Token],
            unary: Dict[str, Callable[[Any], Any]],
            binary: Dict[str, Callable[[Any, Any], Any]],
            functions: Dict[str, Callable[..., Any]]) -> None:
        self.tokens = tokens
        self.unary = unary
        self.binary = binary
        self.functions = functions

    def __str__(self) -> str:
        return self.to_string()

    def simplify(self, values: Optional[dict] = None) -> 'Expression':
        values = values or {}
        stack = []
        newexpr = []
        for token in self.tokens:
            if token.type == NUMBER_TYPE:
                stack.append(token)
            elif token.type == VARIABLE_TYPE and token.name in values:
                value = values[token.name]
                stack.append(Token(NUMBER_TYPE, 0, 0, value))
            elif token.type == BINARY_TYPE and len(stack) > 1:
                if not isinstance(token.name, str):
                    raise ValueError() #TODO
                b, a = stack.pop(), stack.pop()
                value = self.binary[token.name](a.value, b.value)
                stack.append(Token(NUMBER_TYPE, 0, 0, value))
            elif token.type == UNARY_TYPE and stack:
                if not isinstance(token.name, str):
                    raise ValueError() # TODO
                a = stack.pop()
                value = self.unary[token.name](a.value)
                stack.append(Token(NUMBER_TYPE, 0, 0, value))
            else:
                while stack:
                    newexpr.append(stack.pop(0))
                newexpr.append(token)
        while stack:
            newexpr.append(stack.pop(0))

        return Expression(newexpr, self.unary, self.binary, self.functions)

    def subst(
            self, variable: str,
            expr: Union['Expression', str]) -> 'Expression':
        """Substitute variable in expression."""
        if not isinstance(expr, Expression):
            expr = Parser().parse(str(expr))
        newexpr = []
        for token in self.tokens:
            if token.type != VARIABLE_TYPE:
                newexpr.append(token)
                continue
            if token.name != variable:
                newexpr.append(token)
                continue
            for etok in expr.tokens:
                repl = Token(etok.type, etok.name, etok.priority, etok.value)
                newexpr.append(repl)
        return Expression(newexpr, self.unary, self.binary, self.functions)

    def eval(self, values: Optional[dict] = None) -> Any:
        values = values or {}
        stack = []
        for token in self.tokens:
            if token.type == NUMBER_TYPE:
                stack.append(token.value)
            elif token.type == BINARY_TYPE and isinstance(token.name, str):
                b, a = stack.pop(), stack.pop()
                stack.append(self.binary[token.name](a, b))
            elif token.type == VARIABLE_TYPE and isinstance(token.name, str):
                if token.name in values:
                    stack.append(values[token.name])
                elif token.name in self.functions:
                    stack.append(self.functions[token.name])
                else:
                    raise Exception(f"undefined variable '{token.name}'")
            elif token.type == UNARY_TYPE and isinstance(token.name, str):
                a = stack.pop()
                stack.append(self.unary[token.name](a))
            elif token.type == FUNCTION_TYPE:
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
        for token in self.tokens:
            if token.type == NUMBER_TYPE:
                if isinstance(token.value, str):
                    stack.append(repr(token.value))
                else:
                    stack.append(token.value)
            elif token.type == BINARY_TYPE:
                b = stack.pop()
                a = stack.pop()
                f = token.name
                if f == '^' and python:
                    stack.append(f'{a}**{b}')
                elif f == ',':
                    stack.append(f'{a}, {b}')
                else:
                    stack.append(f'({a}{f}{b})')
            elif token.type == VARIABLE_TYPE and isinstance(token.name, str):
                stack.append(token.name)
            elif token.type == UNARY_TYPE:
                a = stack.pop()
                f = token.name
                if f == '-':
                    stack.append(f'(-{a})')
                else:
                    stack.append(f'{f}({a})')
            elif token.type == FUNCTION_TYPE:
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
        for token in self.tokens:
            if token.type != VARIABLE_TYPE:
                continue
            if token.name in symlist:
                continue
            if not isinstance(token.name, str):
                raise ValueError() # TODO
            symlist.append(token.name)
        return symlist

    @property
    def variables(self) -> List[str]:
        return [sym for sym in self.symbols if sym not in self.functions]

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

    unary: Dict[str, Callable[[Any], Any]]
    binary: Dict[str, Callable[[Any, Any], Any]]
    functions: Dict[str, Callable[..., Any]]

    _expression: str
    _success: bool
    _errormsg: str
    _pos: int
    _cur_value: Union[str, float, int]
    _cur_priority: int
    _cur_name: Union[str, int]
    _tmp_priority: int

    def __init__(self) -> None:
        self._expression = ''
        self._success = False
        self._error = ''
        self._pos = 0
        self._cur_name = 0
        self._cur_value = 0
        self._cur_priority = 0
        self._tmp_priority = 0

        rnd: AnyOp = lambda x: random.uniform(0., x)
        iif: AnyOp = lambda a, b, c: b if a else c
        iand: AnyOp = lambda a, b: a and b
        ior: AnyOp = lambda a, b: a or b
        concat: AnyOp = lambda *args: ''.join(map(str, args))
        append: AnyOp = lambda a, b: a + [b] if isinstance(a, list) else [a, b]

        self.unary = {
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'asin': math.asin,
            'acos': math.acos,
            'atan': math.atan,
            'sqrt': math.sqrt,
            'log': math.log,
            'abs': abs,
            'ceil': math.ceil,
            'floor': math.floor,
            'round': round,
            '-': operator.neg,
            'exp': math.exp}

        self.binary = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv,
            '%': operator.mod,
            '^': math.pow,
            ',': append,
            '||': concat,
            '==': operator.eq,
            '!=': operator.ne,
            '>': operator.gt,
            '<': operator.lt,
            '>=': operator.ge,
            '<=': operator.le,
            'and': iand,
            'or': ior}

        self.functions = {
            'random': rnd,
            'fac': math.factorial,
            'min': min,
            'max': max,
            'pow': math.pow,
            'atan2': math.atan2,
            'concat': concat,
            'if': iif}

        self.constants = {
            'E': math.e,
            'PI': math.pi}

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
        expected = self.PRIMARY | self.LPAREN | self.FUNCTION | self.SIGN
        noperators = 0

        while self._pos < len(self._expression):
            if self._is_operator():
                if self._is_sign() and expected & self.SIGN:
                    if self._is_minus():
                        self._cur_priority = 5
                        self._cur_name = '-'
                        noperators += 1
                        self._add_operator(tokens, operators, UNARY_TYPE)
                    expected = \
                        self.PRIMARY | self.LPAREN | self.FUNCTION | self.SIGN
                elif self._is_comment():
                    pass
                else:
                    if expected and self.OPERATOR == 0:
                        self._raise_error(self._pos, 'unexpected operator')
                    noperators += 2
                    self._add_operator(tokens, operators, BINARY_TYPE)
                    expected = \
                        self.PRIMARY | self.LPAREN | self.FUNCTION | self.SIGN
            elif self._is_number():
                if expected and self.PRIMARY == 0:
                    self._raise_error(self._pos, 'unexpected number')
                token = Token(NUMBER_TYPE, 0, 0, self._cur_value)
                tokens.append(token)
                expected = self.OPERATOR | self.RPAREN | self.COMMA
            elif self._is_string():
                if (expected & self.PRIMARY) == 0:
                    self._raise_error(self._pos, 'unexpected string')
                token = Token(NUMBER_TYPE, 0, 0, self._cur_value)
                tokens.append(token)
                expected = self.OPERATOR | self.RPAREN | self.COMMA
            elif self._is_left_parenth():
                if (expected & self.LPAREN) == 0:
                    self._raise_error(self._pos, 'unexpected \"(\"')
                if expected & self.CALL:
                    noperators += 2
                    self._cur_priority = -2
                    self._cur_name = -1
                    self._add_operator(tokens, operators, FUNCTION_TYPE)
                expected = \
                    self.PRIMARY | self.LPAREN | self.FUNCTION | \
                    self.SIGN | self.NULLARY
            elif self._is_right_parenth():
                if expected & self.NULLARY:
                    token = Token(NUMBER_TYPE, 0, 0, [])
                    tokens.append(token)
                elif (expected & self.RPAREN) == 0:
                    self._raise_error(self._pos, 'unexpected \")\"')
                expected = \
                    self.OPERATOR | self.RPAREN | self.COMMA | \
                    self.LPAREN | self.CALL
            elif self._is_comma():
                if (expected & self.COMMA) == 0:
                    self._raise_error(self._pos, 'unexpected \",\"')
                self._add_operator(tokens, operators, BINARY_TYPE)
                noperators += 2
                expected = \
                    self.PRIMARY | self.LPAREN | self.FUNCTION | self.SIGN
            elif self._is_constant():
                if (expected & self.PRIMARY) == 0:
                    self._raise_error(self._pos, 'unexpected constant')
                consttoken = Token(NUMBER_TYPE, 0, 0, self._cur_value)
                tokens.append(consttoken)
                expected = self.OPERATOR | self.RPAREN | self.COMMA
            elif self._is_binary_operator():
                if (expected & self.FUNCTION) == 0:
                    self._raise_error(self._pos, 'unexpected function')
                self._add_operator(tokens, operators, BINARY_TYPE)
                noperators += 2
                expected = self.LPAREN
            elif self._is_unary_operator():
                if (expected & self.FUNCTION) == 0:
                    self._raise_error(self._pos, 'unexpected function')
                self._add_operator(tokens, operators, UNARY_TYPE)
                noperators += 1
                expected = self.LPAREN
            elif self._is_variable():
                if (expected & self.PRIMARY) == 0:
                    self._raise_error(self._pos, 'unexpected variable')
                vartoken = Token(VARIABLE_TYPE, self._cur_name, 0, 0)
                tokens.append(vartoken)
                expected = \
                    self.OPERATOR | self.RPAREN | \
                    self.COMMA | self.LPAREN | self.CALL
            elif self._is_space():
                pass
            else:
                if self._error == '':
                    self._raise_error(self._pos, 'unknown character')
                else:
                    self._raise_error(self._pos, self._error)
        if self._tmp_priority < 0 or self._tmp_priority >= 10:
            self._raise_error(self._pos, 'unmatched \"()\"')
        while operators:
            tokens.append(operators.pop())
        if noperators + 1 != len(tokens):
            self._raise_error(self._pos, 'parity')

        return Expression(tokens, self.unary, self.binary, self.functions)

    def eval(self, expression: str, variables: Optional[dict] = None) -> Any:
        return self.parse(expression).eval(variables)

    def _add_operator(
            self, tokens: List[Token], operators: List[Token],
            typeid: int) -> None:
        name = self._cur_name
        priority = self._cur_priority + self._tmp_priority
        token = Token(typeid, name, priority, 0)
        while operators:
            if token.priority > operators[-1].priority:
                break
            tokens.append(operators.pop())
        operators.append(token)

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
        for i in self.constants:
            L = len(i)
            string = self._expression[self._pos:self._pos + L]
            if i == string:
                if len(self._expression) <= self._pos + L:
                    self._cur_value = self.constants[i]
                    self._pos += L
                    return True
                if not self._expression[self._pos + L].isalnum() \
                    and self._expression[self._pos + L] != "_":
                    self._cur_value = self.constants[i]
                    self._pos += L
                    return True
        return False

    def _is_operator(self) -> bool:
        ops = [
            ('+', 2, '+'),
            ('-', 2, '-'),
            ('*', 3, '*'),
            ('/', 4, '/'),
            ('%', 4, '%'),
            ('^', 6, '^'),
            ('||', 1, '||'),
            ('==', 1, '=='),
            ('!=', 1, '!='),
            ('<=', 1, '<='),
            ('>=', 1, '>='),
            ('<', 1, '<'),
            ('>', 1, '>'),
            ('and', 0, 'and'),
            ('or', 0, 'or')]

        for token, priorityrity, index in ops:
            if self._expression.startswith(token, self._pos):
                self._cur_priority = priorityrity
                self._cur_name = index
                self._pos += len(token)
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
        for i in range(self._pos, len(self._expression)):
            c = self._expression[i]
            if c.upper() == c.lower():
                if i == self._pos or (c != '_' and (c < '0' or c > '9')):
                    break
            string += c
        if string and string in self.unary:
            self._cur_name = string
            self._cur_priority = 7
            self._pos += len(string)

            return True
        return False

    def _is_binary_operator(self) -> bool:
        string = ''
        for i in range(self._pos, len(self._expression)):
            c = self._expression[i]
            if c.upper() == c.lower():
                if i == self._pos or (c != '_' and (c < '0' or c > '9')):
                    break
            string += c
        if string and string in self.binary:
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
                if not (c in '_."') and (c < '0' or c > '9'):
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

    def _is_comment(self) -> bool:
        code = self._prev
        if code == '/' and self._cur == '*':
            self._pos = self._expression.index('*/', self._pos) + 2
            if self._pos == 1:
                self._pos = len(self._expression)
            return True
        return False

    def _raise_error(self, column: int, msg: str) -> None:
        self._success = False
        self._error = 'parse error [column ' + str(column) + ']: ' + msg
        raise Exception(self._error)

    def _unescape(self, string: str, pos: int) -> str:
        buffer = []
        escaping = False
        transform = {
            "'": "'", '\\': '\\', '/': '/',
            'b': '\b', 'f': '\f', 'n': '\n', 'r': '\r', 't': '\t'}

        for i, c in enumerate(string):
            if escaping:
                if c in transform:
                    buffer.append(transform[c])
                    break
                if c == 'u':
                    # interpret the following 4 characters
                    # as the hex of the unicode code point
                    buffer.append(chr(int(string[i + 1: i + 5], 16)))
                    i += 4
                    break
                self._raise_error(
                        pos + i, 'illegal escape sequence: \'\\' + c + '\'')
                escaping = False
            elif c == '\\':
                escaping = True
            else:
                buffer.append(c)

        return ''.join(buffer)

#
# Workarounds
#

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
