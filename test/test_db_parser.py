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
"""Unittests for module 'nemoa.db.parser'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from nemoa.db import parser
from nemoa.types import AnyOp
import test
from test import Case

#
# Test Cases
#

class TestParser(test.ModuleTest):
    module = parser

    def test_parse_clause(self) -> None:
        pass # Implicitely tested in test_SQLOperators

    def test_SQLOperators(self) -> None:
        # The individual operators are tested within seperate tests. Here the
        # operator associativity and precedence is tested.
        # Note: The Precedence is not required to be tested between different
        # operators of same precedence, like comparison operators. In this case
        # the operators are always evaluated from left to right.
        parse = parser.parse_clause
        peval: AnyOp = lambda expr, *args: parse(expr).eval(*args)

        # Logical Operators
        with self.subTest():
            self.assertCaseEqual(peval, [
                Case(('x AND NOT(y)', 1, 0), {}, True),
                Case(('NOT(x AND y)', 1, 0), {}, True),
                Case(('x OR y AND z', 1, 0, 0), {}, True),
                Case(('(x OR y) AND z', 1, 0, 0), {}, False)])

        # Bitwise Operators
        with self.subTest():
            self.assertCaseEqual(peval, [
                Case(('x | y ^ z', 1, 0, 3), {}, 3),
                Case(('(x | y) ^ z', 1, 0, 3), {}, 2),
                Case(('x ^ y ^ z', 1, 0, 3), {}, 2),
                Case(('x ^ y & z', 3, 1, 0), {}, 3),
                Case(('(x ^ y) & z', 3, 1, 0), {}, 0)])

        # Arithmetic Operators
        with self.subTest():
            self.assertCaseEqual(peval, [
                Case(('x + (-y)', 1, 1), {}, 0),
                Case(('-(x + y)', 1, 1), {}, -2),
                Case(('x + y * z', 1, 0, 0), {}, 1),
                Case(('(x + y) * z', 1, 0, 0), {}, 0)])

        # Mixed Operators
        # TODO

    def test_SQLOperators_arithmetic(self) -> None:
        parse = parser.parse_clause
        peval: AnyOp = lambda expr, *args: parse(expr).eval(*args)

        # Unary Plus
        with self.subTest(symbol='+'):
            self.assertCaseEqual(peval, [
                Case(('+x', 1), {}, 1),
                Case(('+x', -1), {}, -1),
                Case(('+(+x)', 1), {}, 1),
                Case(('+(+x)', -1), {}, -1)])

        # Negation
        with self.subTest(symbol='-'):
            self.assertCaseEqual(peval, [
                Case(('-x', 1), {}, -1),
                Case(('-x', -1), {}, 1),
                Case(('-(-x)', 1), {}, 1),
                Case(('-(-x)', -1), {}, -1)])

        # Division
        with self.subTest(symbol='/'):
            self.assertCaseEqual(peval, [
                Case(('x / y', 1, 1), {}, 1.),
                Case(('x / y', 2, 1), {}, 2.),
                Case(('x / y', 1, .2), {}, 5.),
                Case(('x / y', 1, 2), {}, .5)])

        # Remainder
        with self.subTest(symbol='%'):
            self.assertCaseEqual(peval, [
                Case(('x % y', 2, 3), {}, 2),
                Case(('x % y', 3, 2), {}, 1),
                Case(('x % y', 2, 1), {}, 0),
                Case(('x % y', .1, .5), {}, .1)])

        # Multiplication
        with self.subTest(symbol='*'):
            self.assertCaseEqual(peval, [
                Case(('x * y', -1, -1), {}, 1),
                Case(('x * y', 2, .5), {}, 1),
                Case(('x * y', 2, 2), {}, 4),
                Case(('x * y', -.5, .5), {}, -.25)])

        # Addition
        with self.subTest(symbol='+'):
            self.assertCaseEqual(peval, [
                Case(('x + y', 0, 1), {}, 1),
                Case(('x + y', -1, 1), {}, 0),
                Case(('x + y', 2, 2), {}, 4),
                Case(('x + y', .5, .5), {}, 1)])

        # Subtraction
        with self.subTest(symbol='-'):
            self.assertCaseEqual(peval, [
                Case(('x - y', 0, 1), {}, -1),
                Case(('x - y', -1, 1), {}, -2),
                Case(('x - y', 2, 2), {}, 0),
                Case(('x - y', .5, .5), {}, 0)])

    def test_SQLOperators_bitwise(self) -> None:
        parse = parser.parse_clause
        peval: AnyOp = lambda expr, *args: parse(expr).eval(*args)

        # Bitwise AND
        with self.subTest(symbol='&'):
            self.assertCaseEqual(peval, [
                Case(('x & y', 2, 2), {}, 2),
                Case(('x & y', 2, 3), {}, 2),
                Case(('x & y', 1, 3), {}, 1),
                Case(('x & y', 1, 2), {}, 0)])

        # Bitwise XOR
        with self.subTest(symbol='^'):
            self.assertCaseEqual(peval, [
                Case(('x ^ y', 2, 2), {}, 0),
                Case(('x ^ y', 2, 3), {}, 1),
                Case(('x ^ y', 1, 3), {}, 2),
                Case(('x ^ y', 1, 2), {}, 3)])

        # Bitwise OR
        with self.subTest(symbol='|'):
            self.assertCaseEqual(peval, [
                Case(('x | y', 2, 2), {}, 2),
                Case(('x | y', 2, 3), {}, 3),
                Case(('x | y', 1, 3), {}, 3),
                Case(('x | y', 1, 2), {}, 3)])

    def test_SQLOperators_comparison(self) -> None:
        parse = parser.parse_clause
        peval: AnyOp = lambda expr, *args: parse(expr).eval(*args)

        # Equality
        with self.subTest(symbol='='):
            self.assertCaseEqual(peval, [
                Case(('x = y', 1, 1), {}, True),
                Case(('x = y', 1, 2), {}, False),
                Case(('x = y', 'a', 'a'), {}, True),
                Case(('x = y', 'a', 'b'), {}, False)])

        # Inequality
        with self.subTest(symbol='<>'):
            self.assertCaseEqual(peval, [
                Case(('x <> y', 1, 1), {}, False),
                Case(('x <> y', 1, 2), {}, True),
                Case(('x <> y', 'a', 'a'), {}, False),
                Case(('x <> y', 'a', 'b'), {}, True)])

        # Greater
        with self.subTest(symbol='>'):
            self.assertCaseEqual(peval, [
                Case(('x > y', 1, 1), {}, False),
                Case(('x > y', 2, 1), {}, True),
                Case(('x > y', 'a', 'a'), {}, False),
                Case(('x > y', 'b', 'a'), {}, True)])

        # Greater or Equal
        with self.subTest(symbol='>='):
            self.assertCaseEqual(peval, [
                Case(('x >= y', 1, 2), {}, False),
                Case(('x >= y', 1, 1), {}, True),
                Case(('x >= y', 'a', 'b'), {}, False),
                Case(('x >= y', 'a', 'a'), {}, True)])

        # Lower
        with self.subTest(symbol='<'):
            self.assertCaseEqual(peval, [
                Case(('x < y', 1, 1), {}, False),
                Case(('x < y', 1, 2), {}, True),
                Case(('x < y', 'a', 'a'), {}, False),
                Case(('x < y', 'a', 'b'), {}, True)])

        # Lower or Equal
        with self.subTest(symbol='<='):
            self.assertCaseEqual(peval, [
                Case(('x <= y', 2, 1), {}, False),
                Case(('x <= y', 1, 1), {}, True),
                Case(('x <= y', 'b', 'a'), {}, False),
                Case(('x <= y', 'a', 'a'), {}, True)])

        # Containment
        with self.subTest(symbol='IN'):
            self.assertCaseEqual(peval, [
                Case(('x IN y', 'a', ['a', 'b']), {}, True),
                Case(('x IN y', 'a', ['b', 'c']), {}, False),
                Case(('x IN y', 'a', 'ba'), {}, True),
                Case(('x IN y', 'ab', 'ba'), {}, False)])

        # Matching
        with self.subTest(symbol='LIKE'):
            self.assertCaseEqual(peval, [
                Case(('x LIKE y', 'a', 'a%'), {}, True),
                Case(('x LIKE y', 'a', 'a_'), {}, False),
                Case(('x LIKE y', 'ab', 'a%'), {}, True),
                Case(('x LIKE y', 'ab', 'a_'), {}, True),
                Case(('x LIKE y', 'ba', 'a%'), {}, False),
                Case(('x LIKE y', 'ba', '%a'), {}, True),
                Case(('x LIKE y', 'ab', '%a'), {}, False),
                Case(('x LIKE y', 'ab', '__'), {}, True),
                Case(('x LIKE y', 'ab', '_'), {}, False),
                Case(('x LIKE y', 'ab', '_%'), {}, True),
                Case(('x LIKE y', 'ab', '%_'), {}, True),
                Case(('x LIKE y', 'ab', '%'), {}, True)])

    def test_SQLOperators_logical(self) -> None:
        parse = parser.parse_clause
        peval: AnyOp = lambda expr, *args: parse(expr).eval(*args)

        # Boolean OR
        with self.subTest(symbol='OR'):
            self.assertCaseEqual(peval, [
                Case(('x OR y', True, False), {}, True),
                Case(('x OR y', False, True), {}, True),
                Case(('x OR y', False, False), {}, False),
                Case(('x OR y', True, True), {}, True)])

        # Boolean AND
        with self.subTest(symbol='AND'):
            self.assertCaseEqual(peval, [
                Case(('x AND y', True, False), {}, False),
                Case(('x AND y', False, True), {}, False),
                Case(('x AND y', False, False), {}, False),
                Case(('x AND y', True, True), {}, True)])

        # Boolean NOT
        with self.subTest(symbol='NOT'):
            self.assertCaseEqual(peval, [
                Case(('NOT(x)', True), {}, False),
                Case(('NOT(x)', False), {}, True)])
