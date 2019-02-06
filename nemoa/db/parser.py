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
import operator
from typing import Any, Sequence
import numpy as np
from nemoa.base import parser
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
            Symbol(BINARY, ',', parser._pack, 30, True)]) # pylint: disable=W0212
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

class SQLFunctions(SQLOperators):
    """SQL:2016 Clause Operator and Function Vocabulary.

    This Vocabulary follows the specifications of the ISO standard SQL:2016
    (ISO 9075:2016), which is developed by a common committee of ISO and IEC.

    """
    def __init__(self) -> None:
        super().__init__()

        # Aggregate Functions
        self.update([
            Symbol(FUNCTION, 'COUNT', len, 20, False),
            Symbol(FUNCTION, 'MIN', min, 20, False),
            Symbol(FUNCTION, 'MAX', max, 20, False),
            Symbol(FUNCTION, 'SUM', sum, 20, False),
            Symbol(FUNCTION, 'AVG', np.mean, 20, False),
            Symbol(FUNCTION, 'STDDEV_POP',
                functools.partial(np.std, ddof=0), 20, False),
            Symbol(FUNCTION, 'STDDEV_SAMP',
                functools.partial(np.std, ddof=1), 20, False),
            Symbol(FUNCTION, 'VAR_POP',
                functools.partial(np.var, ddof=0), 20, False),
            Symbol(FUNCTION, 'VAR_SAMP',
                functools.partial(np.var, ddof=1), 20, False),
            Symbol(FUNCTION, 'COVAR_POP', sql_covar_pop, 20, False),
            Symbol(FUNCTION, 'COVAR_SAMP', sql_covar_samp, 20, False)])

#
# Constructors
#

#def parse_projection(): ...

def parse_clause(
        clause: str, variables: parser.OptVars = None) -> parser.Expression:
    return parser.Parser(SQLFunctions()).parse(clause, variables=variables)
