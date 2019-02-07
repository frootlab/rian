# -*- coding: utf-8 -*-
# Copyright (c) 2013-2019 Patrick Michl
#
# This file is part of nemoa, https://frootlab.github.io/nemoa
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
"""SQL Parser."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import fnmatch
import functools
import hashlib
import math
import operator
import random
from typing import Any, Sequence, Union
import uuid
import numpy as np
from nemoa.base import parser, phonetic
from nemoa.base.parser import Symbol, UNARY, BINARY, FUNCTION

#
# SQL Operators
#

def sql_and(a: Any, b: Any) -> bool:
    """SQL-AND Operator."""
    return a and b

def sql_or(a: Any, b: Any) -> bool:
    """SQL-OR Operator."""
    return a or b

def sql_in(a: Any, b: Sequence) -> bool:
    """SQL-IN Operator."""
    return a in b

def sql_like(string: str, pattern: str) -> bool:
    """SQL-LIKE Operator.

    The LIKE operator is used in a WHERE clause to search for a specified
    pattern in a column. There are two wildcards used in conjunction with the
    LIKE operator: The percent (%) sign represents zero, one, or multiple
    characters. The underscore (_)represents a single character.

    """
    # Translate SQL wildcards to Unix wildcards
    # TODO: Better use regular expressions, since the translation approach
    # raises the problem, that '*' and '?' are not allowed anymore
    pattern = pattern.translate(str.maketrans('%_', '*?'))

    # Use fnmatch.fnmatch to match the given string
    return fnmatch.fnmatch(string, pattern)

class SQLOperators(parser.Vocabulary):
    """SQL:2016 Clause Operator Vocabulary.

    This Vocabulary follows the specifications of the ISO standard SQL:2016
    (ISO 9075:2016), which is developed by a common committee of ISO and IEC.

    """

    def __init__(self) -> None:
        super().__init__()

        # Binding Operators
        self.update([
            Symbol(BINARY, ',', parser._pack, 30, True), # pylint: disable=W0212
            Symbol(BINARY, '||', operator.concat, 1, False)])
            #Symbol(BINARY, 'AS', parser._pack, 13, True),

        # Arithmetic Operators
        self.update([
            Symbol(UNARY, '+', operator.pos, 11, True), # Unary Plus
            Symbol(UNARY, '-', operator.neg, 11, True), # Negation
            Symbol(BINARY, '/', operator.truediv, 10, True), # Division
            Symbol(BINARY, '%', operator.mod, 10, True), # Remainder
            Symbol(BINARY, '*', operator.mul, 10, True), # Multiplication
            Symbol(BINARY, '+', operator.add, 9, True), # Addition
            Symbol(BINARY, '-', operator.sub, 9, True)]) # Subtraction

        # Bitwise Operators
        self.update([
            Symbol(BINARY, '&', operator.and_, 7, True), # Bitwise AND
            Symbol(BINARY, '^', operator.xor, 6, True), # Bitwise XOR
            Symbol(BINARY, '|', operator.or_, 5, True)]) # Bitwise OR

        # Comparison Operators
        self.update([
            Symbol(BINARY, '=', operator.eq, 4, False), # Equality
            Symbol(BINARY, '<>', operator.ne, 4, False), # Inequality
            Symbol(BINARY, '>', operator.gt, 4, True), # Greater
            Symbol(BINARY, '<', operator.lt, 4, True), # Lower
            Symbol(BINARY, '>=', operator.ge, 4, True), # Greater or Equal
            Symbol(BINARY, '<=', operator.le, 4, True), # Lower or Equal
            Symbol(BINARY, 'IN', sql_in, 4, False), # Containment
            Symbol(BINARY, 'LIKE', sql_like, 4, False)]) # Matching

        # Logical Operators
        # TODO: ALL, ANY, BETWEEN, EXISTS, SOME
        self.update([
            Symbol(UNARY, 'NOT', operator.not_, 3, False), # Boolean NOT
            Symbol(BINARY, 'AND', sql_and, 2, False), # Boolean AND
            Symbol(BINARY, 'OR', sql_or, 1, False)]) # Boolean OR

        # Compound Operators
        # Hint: For immutable targets such as strings, numbers, and tuples,
        # the updated value is computed, but not assigned back to the input
        # variable
        self.update([
            Symbol(BINARY, '+=', operator.iadd, 0, False),
            Symbol(BINARY, '-=', operator.isub, 0, False),
            Symbol(BINARY, '*=', operator.imul, 0, False),
            Symbol(BINARY, '/=', operator.itruediv, 0, False),
            Symbol(BINARY, '%=', operator.imod, 0, False),
            Symbol(BINARY, '&=', operator.iand, 0, False),
            Symbol(BINARY, '^-=', operator.ixor, 0, False),
            Symbol(BINARY, '|*=', operator.ior, 0, False)])

#
# SQL Functions
#

def sql_covar_pop(seqa: Sequence, seqb: Sequence) -> Any:
    """SQL-COVAR_POP Function."""
    return np.cov(seqa, seqb, ddof=0)[0, 1]

def sql_covar_samp(seqa: Sequence, seqb: Sequence) -> Any:
    """SQL-COVAR_SAMP Function."""
    return np.cov(seqa, seqb, ddof=1)[0, 1]

def sql_locate(search: str, string: str, start: int = 0) -> int:
    """SQL-LOCATE Function."""
    return string.find(search, start)

def sql_lpad(string: str, width: int, fillchar: str = ' ') -> str:
    """SQL-LPAD Function."""
    return string.rjust(width, fillchar)

def sql_rpad(string: str, width: int, fillchar: str = ' ') -> str:
    """SQL-RPAD Function."""
    return string.ljust(width, fillchar)

def sql_repeat(string: str, count: int) -> str:
    """SQL-REPEAT Function."""
    return string * count

def sql_space(count: int) -> str:
    """SQL-SPACE Function."""
    return ' ' * count

def sql_substr(string: str, start: int, length: int = 0) -> str:
    """SQL-SUBSTRING Function."""
    return string[start: start + length] if length else string[start:]

def sql_translate(string: str, in_chars: str, out_chars: str) -> str:
    """SQL-TRANSLATE Function."""
    return string.translate(str.maketrans(in_chars, out_chars))

def sql_octet_length(string: str) -> int:
    """SQL-OCTET_LENGTH Function."""
    return len(string.encode('utf-8'))

def sql_greatest(*args: Any) -> Any:
    """SQL-GREATEST Function."""
    return max(args)

def sql_least(*args: Any) -> Any:
    """SQL-LEAST Function."""
    return min(args)

def sql_md5(string: str) -> str:
    """SQL-MD5 Function."""
    return hashlib.md5(string.encode('utf-8')).hexdigest()

def sql_sha1(string: str) -> str:
    """SQL-SHA1 Function."""
    return hashlib.sha1(string.encode('utf-8')).hexdigest()

def sql_cot(x: Union[float, int, bool]) -> float:
    """SQL-COT Function."""
    return 1 / math.tan(x)

class SQLFunctions(SQLOperators):
    """SQL:2016 Clause Operator and Function Vocabulary.

    This Vocabulary follows the specifications of the ISO standard SQL:2016
    (ISO 9075:2016), which is developed by a common committee of ISO and IEC.

    """
    def __init__(self) -> None:
        super().__init__()

        sql_stddev_pop = functools.partial(np.std, ddof=0)
        sql_stddev_samp = functools.partial(np.std, ddof=1)
        sql_var_pop = functools.partial(np.var, ddof=0)
        sql_var_samp = functools.partial(np.var, ddof=1)

        # Aggregate Functions
        self.update([
            Symbol(FUNCTION, 'COUNT', len, 20, False),
            Symbol(FUNCTION, 'MIN', min, 20, False),
            Symbol(FUNCTION, 'MAX', max, 20, False),
            Symbol(FUNCTION, 'SUM', sum, 20, False),
            Symbol(FUNCTION, 'AVG', np.mean, 20, False),
            Symbol(FUNCTION, 'STDDEV_POP', sql_stddev_pop, 20, False),
            Symbol(FUNCTION, 'STDDEV_SAMP', sql_stddev_samp, 20, False),
            Symbol(FUNCTION, 'VAR_POP', sql_var_pop, 20, False),
            Symbol(FUNCTION, 'VAR_SAMP', sql_var_samp, 20, False),
            Symbol(FUNCTION, 'COVAR_POP', sql_covar_pop, 20, False),
            Symbol(FUNCTION, 'COVAR_SAMP', sql_covar_samp, 20, False)])

        # String Functions
        # TODO:
        # POSITION(search IN str) -> Requires RegEx Operator definition
        # QUOTE(x) Quote SQL in string x
        self.update([
            Symbol(FUNCTION, 'ASCII', ascii, 20, False),
            Symbol(FUNCTION, 'CHR', chr, 20, False),
            Symbol(FUNCTION, 'CONCAT', operator.concat, 20, False),
            Symbol(FUNCTION, 'LOCATE', sql_locate, 20, False),
            Symbol(FUNCTION, 'LOWER', str.lower, 20, False),
            Symbol(FUNCTION, 'UPPER', str.upper, 20, False),
            Symbol(FUNCTION, 'LPAD', sql_lpad, 20, False),
            Symbol(FUNCTION, 'RPAD', sql_rpad, 20, False),
            Symbol(FUNCTION, 'LTRIM', str.lstrip, 20, False),
            Symbol(FUNCTION, 'RTRIM', str.rstrip, 20, False),
            Symbol(FUNCTION, 'TRIM', str.strip, 20, False),
            Symbol(FUNCTION, 'REPEAT', sql_repeat, 20, False),
            Symbol(FUNCTION, 'SPACE', sql_space, 20, False),
            Symbol(FUNCTION, 'CHAR', str, 20, False),
            Symbol(FUNCTION, 'SUBSTR', sql_substr, 20, False),
            Symbol(FUNCTION, 'REPLACE', str.replace, 20, False),
            Symbol(FUNCTION, 'INITCAP', str.capitalize, 20, False),
            Symbol(FUNCTION, 'TRANSLATE', sql_translate, 20, False),
            Symbol(FUNCTION, 'LENGTH', len, 20, False),
            Symbol(FUNCTION, 'OCTET_LENGTH', sql_octet_length, 20, False),
            Symbol(FUNCTION, 'GREATEST', sql_greatest, 20, False),
            Symbol(FUNCTION, 'LEAST', sql_least, 20, False),
            Symbol(FUNCTION, 'SOUNDEX', phonetic.soundex, 20, False),
            Symbol(FUNCTION, 'MD5', sql_md5, 20, False),
            Symbol(FUNCTION, 'SHA1', sql_sha1, 20, False),
            Symbol(FUNCTION, 'UUID', uuid.uuid1, 20, False)])

        # Trigonometric Functions
        self.update([
            Symbol(FUNCTION, 'ASIN', math.asin, 20, False),
            Symbol(FUNCTION, 'ACOS', math.acos, 20, False),
            Symbol(FUNCTION, 'ATAN', math.atan, 20, False),
            Symbol(FUNCTION, 'ATAN2', math.atan2, 20, False),
            Symbol(FUNCTION, 'SIN', math.sin, 20, False),
            Symbol(FUNCTION, 'COS', math.cos, 20, False),
            Symbol(FUNCTION, 'TAN', math.tan, 20, False),
            Symbol(FUNCTION, 'COT', sql_cot, 20, False),
            Symbol(FUNCTION, 'SINH', math.sinh, 20, False),
            Symbol(FUNCTION, 'COSH', math.cosh, 20, False),
            Symbol(FUNCTION, 'TANH', math.tanh, 20, False),
            Symbol(FUNCTION, 'ATANH', math.atanh, 20, False)])

        # Numeric Functions
        self.update([
            Symbol(FUNCTION, 'ABS', abs, 20, False),
            Symbol(FUNCTION, 'SIGN', np.sign, 20, False),
            Symbol(FUNCTION, 'MOD', operator.mod, 20, False),
            Symbol(FUNCTION, 'CEIL', math.ceil, 20, False),
            Symbol(FUNCTION, 'FLOOR', math.floor, 20, False),
            Symbol(FUNCTION, 'ROUND', round, 20, False),
            Symbol(FUNCTION, 'TRUNCATE', math.trunc, 20, False),
            Symbol(FUNCTION, 'SQRT', math.sqrt, 20, False),
            Symbol(FUNCTION, 'EXP', math.exp, 20, False),
            Symbol(FUNCTION, 'POWER', pow, 20, False),
            Symbol(FUNCTION, 'LN', math.log, 20, False),
            Symbol(FUNCTION, 'LOG', math.log, 20, False),
            Symbol(FUNCTION, 'LOG10', math.log10, 20, False),
            Symbol(FUNCTION, 'SETSEED', random.seed, 20, False),
            Symbol(FUNCTION, 'RAND', random.random, 20, False)])


#
# Constructors
#

#def parse_projection(): ...

def parse_clause(
        clause: str, variables: parser.OptVars = None) -> parser.Expression:
    return parser.Parser(SQLFunctions()).parse(clause, variables=variables)
