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

TNUMBER = 0
TUNOP = 1
TBINOP = 2
TVAR = 3
TFUNCALL = 4

class Token:

    type: int
    index: Union[str, int]
    #prio:
    #number:

    def __init__(self, typ: int, ind: Union[str, int], prio, num) -> None:
        self.type = typ
        self.index = ind or 0
        self.prio = prio or 0
        self.number = num if num is not None else 0

    def __str__(self) -> str:
        if self.type == TNUMBER:
            return self.number
        if self.type in [TUNOP, TBINOP, TVAR]:
            if isinstance(self.index, str):
                return self.index
            raise ValueError() # TODO
        if self.type == TFUNCALL:
            return 'CALL'
        return 'Invalid Token'

class Expression:

    def __init__(self, tokens: List[Token], ops1, ops2, functions) -> None:
        self.tokens = tokens
        self.ops1 = ops1
        self.ops2 = ops2
        self.functions = functions

    def simplify(self, values: Optional[dict] = None) -> 'Expression':
        values = values or {}
        nstack = []
        newexpr = []
        for i, item in enumerate(self.tokens):
            if item.type == TNUMBER:
                nstack.append(item)
            elif item.type == TVAR and item.index in values:
                item = Token(TNUMBER, 0, 0, values[item.index])
                nstack.append(item)
            elif item.type == TBINOP and len(nstack) > 1:
                n2 = nstack.pop()
                n1 = nstack.pop()
                f = self.ops2[item.index]
                item = Token(TNUMBER, 0, 0, f(n1.number, n2.number))
                nstack.append(item)
            elif item.type == TUNOP and nstack:
                n1 = nstack.pop()
                f = self.ops1[item.index]
                item = Token(TNUMBER, 0, 0, f(n1.number))
                nstack.append(item)
            else:
                while nstack:
                    newexpr.append(nstack.pop(0))
                newexpr.append(item)
        while nstack:
            newexpr.append(nstack.pop(0))

        return Expression(newexpr, self.ops1, self.ops2, self.functions)

    def substitute(
            self, variable: str,
            expr: Union['Expression', str]) -> 'Expression':
        if not isinstance(expr, Expression):
            expr = Parser().parse(str(expr))
        newexpr = []
        for i, item in enumerate(self.tokens):
            if item.type == TVAR and item.index == variable:
                for j, expritem in enumerate(expr.tokens):
                    replitem = Token(
                        expritem.type,
                        expritem.index,
                        expritem.prio,
                        expritem.number)
                    newexpr.append(replitem)
            else:
                newexpr.append(item)

        return Expression(newexpr, self.ops1, self.ops2, self.functions)

    def evaluate(self, values: Optional[dict] = None) -> Any:
        values = values or {}
        nstack = []
        L = len(self.tokens)
        for item in self.tokens:
            type_ = item.type
            if type_ == TNUMBER:
                nstack.append(item.number)
            elif type_ == TBINOP:
                n2 = nstack.pop()
                n1 = nstack.pop()
                f = self.ops2[item.index]
                nstack.append(f(n1, n2))
            elif type_ == TVAR:
                if item.index in values:
                    nstack.append(values[item.index])
                elif item.index in self.functions:
                    nstack.append(self.functions[item.index])
                else:
                    raise Exception(f"undefined variable '{item.index}'")
            elif type_ == TUNOP:
                n1 = nstack.pop()
                f = self.ops1[item.index]
                nstack.append(f(n1))
            elif type_ == TFUNCALL:
                n1 = nstack.pop()
                f = nstack.pop()
                if callable(f):
                    if isinstance(n1, list):
                        nstack.append(f(*n1))
                    else:
                        nstack.append(f(n1))
                else:
                    raise Exception(f'{f} is not a function')
            else:
                raise Exception('invalid expression')
        if len(nstack) > 1:
            raise Exception('invalid expression (parity)')

        return nstack[0]

    def to_string(self, topy: bool = False) -> str:
        nstack = []
        for i, item in enumerate(self.tokens):
            if item.type == TNUMBER:
                if isinstance(item.number, str):
                    nstack.append(repr(item.number))
                else:
                    nstack.append(item.number)
            elif item.type == TBINOP:
                n2 = nstack.pop()
                n1 = nstack.pop()
                f = item.index
                if f == '^' and topy:
                    nstack.append(f'{n1}**{n2}')
                elif f == ',':
                    nstack.append(f'{n1}, {n2}')
                else:
                    nstack.append(f'({n1}{f}{n2})')
            elif item.type == TVAR:
                var = item.index
                if isinstance(var, str):
                    nstack.append(var)
                else:
                    raise ValueError() # TODO
            elif item.type == TUNOP:
                n1 = nstack.pop()
                f = item.index
                if f == '-':
                    nstack.append(f'({f}{n1})')
                else:
                    nstack.append(f'{f}({n1})')
            elif item.type == TFUNCALL:
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
            if item.type == TVAR and not item.index in symlist:
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
    #tokenprio:
    tokenindex: Union[str, int]
    #tmpprio:
    ops1: Dict[str, Callable[[Any], Any]]
    ops2: Dict[str, Callable[[Any, Any], Any]]
    functions: Dict[str, AnyOp]

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

        self.ops1 = {
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

        self.ops2 = {
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

        # self.values = {
        #     'sin': math.sin,
        #     'cos': math.cos,
        #     'tan': math.tan,
        #     'asin': math.asin,
        #     'acos': math.acos,
        #     'atan': math.atan,
        #     'sqrt': math.sqrt,
        #     'log': math.log,
        #     'abs': abs,
        #     'ceil': math.ceil,
        #     'floor': math.floor,
        #     'round': round,
        #     'random': rnd,
        #     'fac': math.factorial,
        #     'exp': math.exp,
        #     'min': min,
        #     'max': max,
        #     'pow': math.pow,
        #     'atan2': math.atan2,
        #     'E': math.e,
        #     'PI': math.pi}

    def parse(self, expr) -> Expression:
        self.errormsg = ''
        self.success = True
        operstack = []
        tokenstack = []
        self.tmpprio = 0
        expected = self.PRIMARY | self.LPAREN | self.FUNCTION | self.SIGN
        noperators = 0
        self.expression = expr
        self.pos = 0

        while self.pos < len(self.expression):
            if self._is_operator():
                if self._is_sign() and expected & self.SIGN:
                    if self._is_minus():
                        self.tokenprio = 5
                        self.tokenindex = '-'
                        noperators += 1
                        self.addfunc(tokenstack, operstack, TUNOP)
                    expected = \
                        self.PRIMARY | self.LPAREN | self.FUNCTION | self.SIGN
                elif self._is_comment():
                    pass
                else:
                    if expected and self.OPERATOR == 0:
                        self.error_parsing(self.pos, 'unexpected operator')
                    noperators += 2
                    self.addfunc(tokenstack, operstack, TBINOP)
                    expected = \
                        self.PRIMARY | self.LPAREN | self.FUNCTION | self.SIGN
            elif self._is_number():
                if expected and self.PRIMARY == 0:
                    self.error_parsing(self.pos, 'unexpected number')
                token = Token(TNUMBER, 0, 0, self.tokennumber)
                tokenstack.append(token)
                expected = self.OPERATOR | self.RPAREN | self.COMMA
            elif self._is_string():
                if (expected & self.PRIMARY) == 0:
                    self.error_parsing(self.pos, 'unexpected string')
                token = Token(TNUMBER, 0, 0, self.tokennumber)
                tokenstack.append(token)
                expected = self.OPERATOR | self.RPAREN | self.COMMA
            elif self._is_left_parenth():
                if (expected & self.LPAREN) == 0:
                    self.error_parsing(self.pos, 'unexpected \"(\"')
                if expected & self.CALL:
                    noperators += 2
                    self.tokenprio = -2
                    self.tokenindex = -1
                    self.addfunc(tokenstack, operstack, TFUNCALL)
                expected = \
                    self.PRIMARY | self.LPAREN | self.FUNCTION | \
                    self.SIGN | self.NULLARY_CALL
            elif self._is_right_parenth():
                if expected & self.NULLARY_CALL:
                    token = Token(TNUMBER, 0, 0, [])
                    tokenstack.append(token)
                elif (expected & self.RPAREN) == 0:
                    self.error_parsing(self.pos, 'unexpected \")\"')
                expected = \
                    self.OPERATOR | self.RPAREN | self.COMMA | \
                    self.LPAREN | self.CALL
            elif self._is_comma():
                if (expected & self.COMMA) == 0:
                    self.error_parsing(self.pos, 'unexpected \",\"')
                self.addfunc(tokenstack, operstack, TBINOP)
                noperators += 2
                expected = \
                    self.PRIMARY | self.LPAREN | self.FUNCTION | self.SIGN
            elif self._is_constant():
                if (expected & self.PRIMARY) == 0:
                    self.error_parsing(self.pos, 'unexpected constant')
                consttoken = Token(TNUMBER, 0, 0, self.tokennumber)
                tokenstack.append(consttoken)
                expected = self.OPERATOR | self.RPAREN | self.COMMA
            elif self._is_binary_operator():
                if (expected & self.FUNCTION) == 0:
                    self.error_parsing(self.pos, 'unexpected function')
                self.addfunc(tokenstack, operstack, TBINOP)
                noperators += 2
                expected = self.LPAREN
            elif self._is_unary_operator():
                if (expected & self.FUNCTION) == 0:
                    self.error_parsing(self.pos, 'unexpected function')
                self.addfunc(tokenstack, operstack, TUNOP)
                noperators += 1
                expected = self.LPAREN
            elif self._is_variable():
                if (expected & self.PRIMARY) == 0:
                    self.error_parsing(self.pos, 'unexpected variable')
                vartoken = Token(TVAR, self.tokenindex, 0, 0)
                tokenstack.append(vartoken)
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
            tmp = operstack.pop()
            tokenstack.append(tmp)
        if noperators + 1 != len(tokenstack):
            self.error_parsing(self.pos, 'parity')

        return Expression(tokenstack, self.ops1, self.ops2, self.functions)

    def evaluate(self, expr: str, variables: Optional[dict] = None) -> Any:
        return self.parse(expr).evaluate(variables)

    def error_parsing(self, column: int, msg: str) -> None:
        self.success = False
        self.errormsg = 'parse error [column ' + str(column) + ']: ' + msg

        raise Exception(self.errormsg)

    def addfunc(self, tokenstack, operstack, type_):
        tok = Token(type_, self.tokenindex, self.tokenprio + self.tmpprio, 0)

        while operstack:
            if tok.prio <= operstack[len(operstack) - 1].prio:
                tokenstack.append(operstack.pop())
            else:
                break

        operstack.append(tok)

    @property
    def cur(self) -> str:
        return self.expression[self.pos]

    @property
    def prev(self) -> str:
        return self.expression[self.pos - 1]

    def _is_number(self) -> bool:
        r = False
        string = ''
        while self.pos < len(self.expression):
            code = self.cur
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
        if self.pos < len(self.expression) and self.cur == "'":
            self.pos += 1
            while self.pos < len(self.expression):
                code = self.cur
                if code != '\'' or (string != '' and string[-1] == '\\'):
                    string += self.cur
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
        return self.prev in ['+', '-']

    def _is_plus(self) -> bool:
        return self.prev == '+'

    def _is_minus(self) -> bool:
        return self.prev == '-'

    def _is_left_parenth(self) -> bool:
        if self.cur != '(':
            return False
        self.pos += 1
        self.tmpprio += 10
        return True

    def _is_right_parenth(self) -> bool:
        if self.cur != ')':
            return False
        self.pos += 1
        self.tmpprio -= 10
        return True

    def _is_comma(self) -> bool:
        if self.cur != ',':
            return False
        self.pos += 1
        self.tokenprio = -1
        self.tokenindex = ','
        return True

    def _is_space(self) -> bool:
        if not self.cur.isspace():
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
        if string and string in self.ops1:
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
        if string and string in self.ops2:
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
        code = self.prev
        if code == '/' and self.cur == '*':
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
