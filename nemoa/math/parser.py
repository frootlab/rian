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
# py-expression-eval
#

class Token:
    NUMBER = 0
    UNARY = 1
    BINARY = 2
    VARIABLE = 3
    FUNCTION = 4

    tid: int
    index: Union[str, int]
    prio: int
    value: Any

    def __init__(
            self, tid: int, ind: Union[str, int], prio: int,
            value: Any) -> None:
        self.tid = tid
        self.index = ind or 0
        self.prio = prio or 0
        self.value = value if value is not None else 0

    def __str__(self) -> str:
        if self.tid == self.NUMBER:
            return self.value
        if self.tid in [self.UNARY, self.BINARY, self.VARIABLE]:
            if isinstance(self.index, str):
                return self.index
            raise ValueError() # TODO
        if self.tid == self.FUNCTION:
            return 'CALL'
        return 'Invalid Token'

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

    def simplify(self, values: Optional[dict] = None) -> 'Expression':
        values = values or {}
        nstack = []
        newexpr = []
        f: AnyOp
        for i, item in enumerate(self.tokens):
            if item.tid == Token.NUMBER:
                nstack.append(item)
            elif item.tid == Token.VARIABLE and item.index in values:
                tnum = values[item.index]
                nstack.append(Token(Token.NUMBER, 0, 0, tnum))
            elif item.tid == Token.BINARY and len(nstack) > 1:
                if not isinstance(item.index, str):
                    raise ValueError() #TODO
                n2 = nstack.pop()
                n1 = nstack.pop()
                tnum = self.binary[item.index](n1.value, n2.value)
                nstack.append(Token(Token.NUMBER, 0, 0, tnum))
            elif item.tid == Token.UNARY and nstack:
                if not isinstance(item.index, str):
                    raise ValueError() # TODO
                n1 = nstack.pop()
                tnum = self.unary[item.index](n1.value)
                nstack.append(Token(Token.NUMBER, 0, 0, tnum))
            else:
                while nstack:
                    newexpr.append(nstack.pop(0))
                newexpr.append(item)
        while nstack:
            newexpr.append(nstack.pop(0))

        return Expression(newexpr, self.unary, self.binary, self.functions)

    def substitute(
            self, variable: str,
            expr: Union['Expression', str]) -> 'Expression':
        if not isinstance(expr, Expression):
            expr = Parser().parse(str(expr))
        newexpr = []
        for i, item in enumerate(self.tokens):
            if item.tid == Token.VARIABLE and item.index == variable:
                for j, expritem in enumerate(expr.tokens):
                    replitem = Token(
                        expritem.tid,
                        expritem.index,
                        expritem.prio,
                        expritem.value)
                    newexpr.append(replitem)
            else:
                newexpr.append(item)

        return Expression(newexpr, self.unary, self.binary, self.functions)

    def evaluate(self, values: Optional[dict] = None) -> Any:
        values = values or {}
        nstack = []
        for token in self.tokens:
            if token.tid == Token.NUMBER:
                nstack.append(token.value)
            elif token.tid == Token.BINARY and isinstance(token.index, str):
                n2 = nstack.pop()
                n1 = nstack.pop()
                nstack.append(self.binary[token.index](n1, n2))
            elif token.tid == Token.VARIABLE and isinstance(token.index, str):
                if token.index in values:
                    nstack.append(values[token.index])
                elif token.index in self.functions:
                    nstack.append(self.functions[token.index])
                else:
                    raise Exception(f"undefined variable '{token.index}'")
            elif token.tid == Token.UNARY and isinstance(token.index, str):
                n1 = nstack.pop()
                nstack.append(self.unary[token.index](n1))
            elif token.tid == Token.FUNCTION:
                args = nstack.pop()
                func = nstack.pop()
                if not callable(func):
                    raise Exception(f'{func} is not callable')
                if isinstance(args, list):
                    nstack.append(func(*args))
                else:
                    nstack.append(func(args))
            else:
                raise Exception('invalid expression')
        if len(nstack) > 1:
            raise Exception('invalid expression (parity)')

        return nstack[0]

    def to_string(self, topy: bool = False) -> str:
        nstack = []
        for i, item in enumerate(self.tokens):
            if item.tid == Token.NUMBER:
                if isinstance(item.value, str):
                    nstack.append(repr(item.value))
                else:
                    nstack.append(item.value)
            elif item.tid == Token.BINARY:
                n2 = nstack.pop()
                n1 = nstack.pop()
                f = item.index
                if f == '^' and topy:
                    nstack.append(f'{n1}**{n2}')
                elif f == ',':
                    nstack.append(f'{n1}, {n2}')
                else:
                    nstack.append(f'({n1}{f}{n2})')
            elif item.tid == Token.VARIABLE:
                var = item.index
                if isinstance(var, str):
                    nstack.append(var)
                else:
                    raise ValueError() # TODO
            elif item.tid == Token.UNARY:
                n1 = nstack.pop()
                f = item.index
                if f == '-':
                    nstack.append(f'({f}{n1})')
                else:
                    nstack.append(f'{f}({n1})')
            elif item.tid == Token.FUNCTION:
                n1 = nstack.pop()
                f = nstack.pop()
                nstack.append(f + '(' + n1 + ')')
            else:
                raise Exception('invalid expression')
        if len(nstack) > 1:
            raise Exception('invalid expression (parity)')

        # Remove unnecessary parantheses
        rexpr = nstack[0]
        if rexpr.startswith('(') and rexpr.endswith(')'):
            return rexpr[1:-1]

        return rexpr

    def __str__(self) -> str:
        return self.to_string()

    @property
    def symbols(self) -> List[str]:
        symlist: List[str] = []
        for item in self.tokens:
            if item.tid == Token.VARIABLE and not item.index in symlist:
                if isinstance(item.index, str):
                    symlist.append(item.index)
                else:
                    raise ValueError() # TODO
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
    NULLARY_CALL = 256

    success: bool
    errormsg: str
    expression: str
    pos: int
    tokennumber: Union[str, float, int]
    tokenprio: int
    tokenindex: Union[str, int]
    tmpprio: int
    unary: Dict[str, Callable[[Any], Any]]
    binary: Dict[str, Callable[[Any, Any], Any]]
    functions: Dict[str, Callable[..., Any]]

    def __init__(self) -> None:
        self.success = False
        self.errormsg = ''
        self.expression = ''
        self.pos = 0
        self.tokennumber = 0
        self.tokenprio = 0
        self.tokenindex = 0
        self.tmpprio = 0

        rnd: AnyOp = lambda x: random.uniform(0., x)
        iif: AnyOp = lambda a, b, c: b if a else c
        iand: AnyOp = lambda a, b: a and b
        ior: AnyOp = lambda a, b: a or b
        concat: AnyOp = lambda *args: ''.join(map(str, args))
        append: AnyOp = \
            lambda a, b: a + [b] if isinstance(a, list) else [a, b]

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

        self.consts = {
            'E': math.e,
            'PI': math.pi}

    def parse(self, expr: str) -> Expression:
        self.errormsg = ''
        self.success = True
        self.tmpprio = 0
        self.expression = expr
        self.pos = 0

        operstack: List[Token] = []
        tokens: List[Token] = []
        expected = self.PRIMARY | self.LPAREN | self.FUNCTION | self.SIGN
        noperators = 0

        while self.pos < len(self.expression):
            if self._is_operator():
                if self._is_sign() and expected & self.SIGN:
                    if self._is_minus():
                        self.tokenprio = 5
                        self.tokenindex = '-'
                        noperators += 1
                        self.addfunc(tokens, operstack, Token.UNARY)
                    expected = \
                        self.PRIMARY | self.LPAREN | self.FUNCTION | self.SIGN
                elif self._is_comment():
                    pass
                else:
                    if expected and self.OPERATOR == 0:
                        self.error_parsing(self.pos, 'unexpected operator')
                    noperators += 2
                    self.addfunc(tokens, operstack, Token.BINARY)
                    expected = \
                        self.PRIMARY | self.LPAREN | self.FUNCTION | self.SIGN
            elif self._is_number():
                if expected and self.PRIMARY == 0:
                    self.error_parsing(self.pos, 'unexpected number')
                token = Token(Token.NUMBER, 0, 0, self.tokennumber)
                tokens.append(token)
                expected = self.OPERATOR | self.RPAREN | self.COMMA
            elif self._is_string():
                if (expected & self.PRIMARY) == 0:
                    self.error_parsing(self.pos, 'unexpected string')
                token = Token(Token.NUMBER, 0, 0, self.tokennumber)
                tokens.append(token)
                expected = self.OPERATOR | self.RPAREN | self.COMMA
            elif self._is_left_parenth():
                if (expected & self.LPAREN) == 0:
                    self.error_parsing(self.pos, 'unexpected \"(\"')
                if expected & self.CALL:
                    noperators += 2
                    self.tokenprio = -2
                    self.tokenindex = -1
                    self.addfunc(tokens, operstack, Token.FUNCTION)
                expected = \
                    self.PRIMARY | self.LPAREN | self.FUNCTION | \
                    self.SIGN | self.NULLARY_CALL
            elif self._is_right_parenth():
                if expected & self.NULLARY_CALL:
                    token = Token(Token.NUMBER, 0, 0, [])
                    tokens.append(token)
                elif (expected & self.RPAREN) == 0:
                    self.error_parsing(self.pos, 'unexpected \")\"')
                expected = \
                    self.OPERATOR | self.RPAREN | self.COMMA | \
                    self.LPAREN | self.CALL
            elif self._is_comma():
                if (expected & self.COMMA) == 0:
                    self.error_parsing(self.pos, 'unexpected \",\"')
                self.addfunc(tokens, operstack, Token.BINARY)
                noperators += 2
                expected = \
                    self.PRIMARY | self.LPAREN | self.FUNCTION | self.SIGN
            elif self._is_constant():
                if (expected & self.PRIMARY) == 0:
                    self.error_parsing(self.pos, 'unexpected constant')
                consttoken = Token(Token.NUMBER, 0, 0, self.tokennumber)
                tokens.append(consttoken)
                expected = self.OPERATOR | self.RPAREN | self.COMMA
            elif self._is_binary_operator():
                if (expected & self.FUNCTION) == 0:
                    self.error_parsing(self.pos, 'unexpected function')
                self.addfunc(tokens, operstack, Token.BINARY)
                noperators += 2
                expected = self.LPAREN
            elif self._is_unary_operator():
                if (expected & self.FUNCTION) == 0:
                    self.error_parsing(self.pos, 'unexpected function')
                self.addfunc(tokens, operstack, Token.UNARY)
                noperators += 1
                expected = self.LPAREN
            elif self._is_variable():
                if (expected & self.PRIMARY) == 0:
                    self.error_parsing(self.pos, 'unexpected variable')
                vartoken = Token(Token.VARIABLE, self.tokenindex, 0, 0)
                tokens.append(vartoken)
                expected = \
                    self.OPERATOR | self.RPAREN | \
                    self.COMMA | self.LPAREN | self.CALL
            elif self._is_space():
                pass
            else:
                if self.errormsg == '':
                    self.error_parsing(self.pos, 'unknown character')
                else:
                    self.error_parsing(self.pos, self.errormsg)
        if self.tmpprio < 0 or self.tmpprio >= 10:
            self.error_parsing(self.pos, 'unmatched \"()\"')
        while operstack:
            tokens.append(operstack.pop())
        if noperators + 1 != len(tokens):
            self.error_parsing(self.pos, 'parity')

        return Expression(tokens, self.unary, self.binary, self.functions)

    def evaluate(self, expr: str, variables: Optional[dict] = None) -> Any:
        return self.parse(expr).evaluate(variables)

    def error_parsing(self, column: int, msg: str) -> None:
        self.success = False
        self.errormsg = 'parse error [column ' + str(column) + ']: ' + msg

        raise Exception(self.errormsg)

    def addfunc(
            self, tokens: List[Token], operstack: List[Token],
            tid: int) -> None:
        tok = Token(tid, self.tokenindex, self.tokenprio + self.tmpprio, 0)

        while operstack:
            if tok.prio <= operstack[len(operstack) - 1].prio:
                tokens.append(operstack.pop())
            else:
                break

        operstack.append(tok)

    @property
    def _cur(self) -> str:
        return self.expression[self.pos]

    @property
    def _prev(self) -> str:
        return self.expression[self.pos - 1]

    def _is_number(self) -> bool:
        r = False
        string = ''
        while self.pos < len(self.expression):
            code = self._cur
            if code.isdecimal() or code == '.':
                if not string and code == '.':
                    string = '0'

                string += code
                self.pos += 1

                try:
                    self.tokennumber = int(string)
                except ValueError:
                    self.tokennumber = float(string)
                r = True
            else:
                break
        return r

    def _is_string(self) -> bool:
        r = False
        string = ''
        startpos = self.pos
        if self.pos < len(self.expression) and self._cur == "'":
            self.pos += 1
            while self.pos < len(self.expression):
                code = self._cur
                if code != '\'' or (string != '' and string[-1] == '\\'):
                    string += self._cur
                    self.pos += 1
                else:
                    self.pos += 1
                    self.tokennumber = self._unescape(string, startpos)
                    r = True
                    break
        return r

    def _is_constant(self) -> bool:
        for i in self.consts:
            L = len(i)
            string = self.expression[self.pos:self.pos + L]
            if i == string:
                if len(self.expression) <= self.pos + L:
                    self.tokennumber = self.consts[i]
                    self.pos += L
                    return True
                if not self.expression[self.pos + L].isalnum() \
                    and self.expression[self.pos + L] != "_":
                    self.tokennumber = self.consts[i]
                    self.pos += L
                    return True
        return False

    def _is_operator(self) -> bool:
        ops = [
            ('+', 2, '+'),
            ('-', 2, '-'),
            ('*', 3, '*'),
            (u'\u2219', 3, '*'), # bullet operator
            (u'\u2022', 3, '*'), # black small circle
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

        for token, priority, index in ops:
            if self.expression.startswith(token, self.pos):
                self.tokenprio = priority
                self.tokenindex = index
                self.pos += len(token)
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
        self.pos += 1
        self.tmpprio += 10
        return True

    def _is_right_parenth(self) -> bool:
        if self._cur != ')':
            return False
        self.pos += 1
        self.tmpprio -= 10
        return True

    def _is_comma(self) -> bool:
        if self._cur != ',':
            return False
        self.pos += 1
        self.tokenprio = -1
        self.tokenindex = ','
        return True

    def _is_space(self) -> bool:
        if not self._cur.isspace():
            return False
        self.pos += 1
        return True

    def _is_unary_operator(self) -> bool:
        string = ''
        for i in range(self.pos, len(self.expression)):
            c = self.expression[i]
            if c.upper() == c.lower():
                if i == self.pos or (c != '_' and (c < '0' or c > '9')):
                    break
            string += c
        if string and string in self.unary:
            self.tokenindex = string
            self.tokenprio = 7
            self.pos += len(string)

            return True
        return False

    def _is_binary_operator(self) -> bool:
        string = ''
        for i in range(self.pos, len(self.expression)):
            c = self.expression[i]
            if c.upper() == c.lower():
                if i == self.pos or (c != '_' and (c < '0' or c > '9')):
                    break
            string += c
        if string and string in self.binary:
            self.tokenindex = string
            self.tokenprio = 7
            self.pos += len(string)
            return True
        return False

    def _is_variable(self) -> bool:
        string = ''
        inQuotes = False
        for i in range(self.pos, len(self.expression)):
            c = self.expression[i]
            if not inQuotes and (c.lower() == c.upper()):
                if not (c in '_."') and (c < '0' or c > '9'):
                    break
                if i == self.pos and c != '"':
                    break
            if c == '"':
                inQuotes = not inQuotes
            string += c
        if string:
            self.tokenindex = string
            self.tokenprio = 4
            self.pos += len(string)
            return True
        return False

    def _is_comment(self) -> bool:
        code = self._prev
        if code == '/' and self._cur == '*':
            self.pos = self.expression.index('*/', self.pos) + 2
            if self.pos == 1:
                self.pos = len(self.expression)
            return True
        return False

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
                self.error_parsing(
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
        expr = substitute(expr, vmap)

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

def substitute(expr: str, mapping: dict) -> str:
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
