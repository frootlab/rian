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

import operator
from nemoa.base import parser
from nemoa.base.parser import Symbol, UNARY, BINARY
from nemoa.types import AnyOp

#
# SQL Clause Vocabulary
#

class SQLOperators(parser.Vocabulary):
    """SQL:2016 Clause Operator Vocabulary.

    This Vocabulary follows the specifications of the ISO standard SQL:2016
    (ISO 9075:2016), which is developed by a common committee of ISO and IEC.

    """

    def __init__(self) -> None:
        super().__init__()

        bool_and: AnyOp = lambda a, b: a and b
        bool_or: AnyOp = lambda a, b: a or b
        comp_in: AnyOp = lambda a, b: operator.contains(b, a)

        self.update([
            # Binding Operators
            Symbol(BINARY, ',', parser._pack, 13, True), # pylint: disable=W0212

            # SQL Arithmetic Operators
            Symbol(UNARY, '+', operator.pos, 11, True), # Unary Plus
            Symbol(UNARY, '-', operator.neg, 11, True), # Negation
            Symbol(BINARY, '/', operator.truediv, 9, True), # Division
            Symbol(BINARY, '%', operator.mod, 9, True), # Remainder
            Symbol(BINARY, '*', operator.mul, 9, True), # Multiplication
            Symbol(BINARY, '+', operator.add, 8, True), # Addition
            Symbol(BINARY, '-', operator.sub, 8, True), # Subtraction

            # SQL Bitwise Operators
            Symbol(BINARY, '&', operator.and_, 6, True), # Bitwise AND
            Symbol(BINARY, '^', operator.xor, 5, True), # Bitwise XOR
            Symbol(BINARY, '|', operator.or_, 4, True), # Bitwise OR

            # SQL Comparison Operators
            Symbol(BINARY, '=', operator.eq, 3, False), # Equality
            Symbol(BINARY, '>', operator.gt, 3, True), # Greater
            Symbol(BINARY, '<', operator.lt, 3, True), # Lower
            Symbol(BINARY, '>=', operator.ge, 3, True), # Greater or Equal
            Symbol(BINARY, '<=', operator.le, 3, True), # Lower or Equal
            Symbol(BINARY, 'IN', comp_in, 3, False), # Containment

            # SQL Compound Operators
            # See: https://www.w3schools.com/sql/sql_operators.asp

            # Logical Operators
            Symbol(UNARY, 'NOT', operator.not_, 2, True), # Boolean NOT
            Symbol(BINARY, 'AND', bool_and, 1, True), # Boolean AND
            Symbol(BINARY, 'OR', bool_or, 0, True)]) # Boolean OR

# class SQLFunctions(SQLOperators):
#     """SQL:2016 Clause Operator and Function Vocabulary.
#
#     This Vocabulary follows the specifications of the ISO standard SQL:2016
#     (ISO 9075:2016), which is developed by a common committee of ISO and IEC.
#
#     """
#     def __init__(self) -> None:
#         super().__init__()
