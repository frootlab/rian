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
"""Unittests for module 'nemoa.base.parser'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import dataclasses
from unittest import mock
import numpy as np
from nemoa.base import parser
from nemoa.types import AnyOp
import test
from test import Case

#
# Test Cases
#

class TestParser(test.ModuleTest):
    module = parser

    def test_parse(self) -> None:
        pass # Implicitely tested

    def test_Symbol(self) -> None:
        conj: AnyOp = lambda z: complex(z).real - complex(z).imag * 1j
        self.assertCaseRaises(TypeError, parser.Symbol, [
            Case(tuple()), # Too few args
            Case((None, )), # Too few args
            Case((None, None)), # Too few args
            Case((None, None, None)), # Wrong type for 'type'
            Case((parser.UNARY, None, None)), # Wrong type for 'key'
            Case((parser.UNARY, '*', None)), # Unary must be callable
            Case((parser.UNARY, '*', conj, None))]) # Wrong type for 'priority'

        sym = parser.Symbol(parser.UNARY, '*', conj)
        self.assertEqual(
            dataclasses.astuple(sym),
            (parser.UNARY, '*', conj, 0, False, False))

    def test_Vocabulary(self) -> None:
        voc = parser.PyOperators()
        self.assertEqual(voc.search(type=parser.FUNCTION), {})

        mean: AnyOp = lambda s: sum(s) / len(s)
        voc.add(parser.Symbol(parser.FUNCTION, 'mean', mean))
        self.assertIn('mean', voc.search(type=parser.FUNCTION, builtin=False))
        self.assertNotIn('mean', voc.search(type=parser.FUNCTION, builtin=True))

        p = parser.Parser(vocabulary=voc)
        self.assertEqual(p.parse('mean(s)').variables, ('s', ))
        self.assertEqual(p.parse('mean(s)').symbols, ('mean', 's'))
        self.assertEqual(p.parse('mean(s)').eval([1, 2, 3]), 2)

    def test_PyOperators(self) -> None:
        # The individual operators are tested within seperate tests. Here the
        # operator associativity and precedence is tested.
        # Note: The Precedence is not required to be tested between different
        # operators of same precedence, like comparison operators. In this case
        # the operators are always evaluated from left to right.
        p = parser.Parser(vocabulary=parser.PyOperators())
        peval: AnyOp = lambda expr, *args: p.parse(expr).eval(*args)

        # Logical Operators
        with self.subTest():
            self.assertCaseEqual(peval, [
                Case(('x and not(y)', 1, 0), {}, True),
                Case(('not(x and y)', 1, 0), {}, True),
                Case(('x or y and z', 1, 0, 0), {}, True),
                Case(('(x or y) and z', 1, 0, 0), {}, False)])

        # Bitwise Operators
        with self.subTest():
            self.assertCaseEqual(peval, [
                Case(('x | (~y)', 1, 0), {}, -1),
                Case(('~(x | y)', 1, 0), {}, -2),
                Case(('x | y ^ z', 1, 0, 3), {}, 3),
                Case(('(x | y) ^ z', 1, 0, 3), {}, 2),
                Case(('x ^ y ^ z', 1, 0, 3), {}, 2),
                Case(('x ^ y & z', 3, 1, 0), {}, 3),
                Case(('(x ^ y) & z', 3, 1, 0), {}, 0),
                Case(('x & y >> z', 2, 4, 1), {}, 2),
                Case(('(x & y) >> z', 2, 4, 1), {}, 0)])

        # Arithmetic Operators
        with self.subTest():
            self.assertCaseEqual(peval, [
                Case(('x + (-y)', 1, 1), {}, 0),
                Case(('-(x + y)', 1, 1), {}, -2),
                Case(('x + y * z', 1, 0, 0), {}, 1),
                Case(('(x + y) * z', 1, 0, 0), {}, 0),
                Case(('x * y ** z', 2, 2, 2), {}, 8),
                Case(('(x * y) ** z', 2, 2, 2), {}, 16)])

        # Comparison Operators
        # The Precedence is not required to be tested between different
        # comparison operators, since it is always evaluated from left to right

        # Mixed Operators
        with self.subTest():
            self.assertCaseEqual(peval, [
                Case(('x and y | z', 0, 2, 3), {}, 0),
                Case(('(x and y) | z', 0, 2, 3), {}, 3),
                Case(('x << y + z', 1, 2, 3), {}, 32),
                Case(('(x << y) + z', 1, 2, 3), {}, 7)])

    def test_PyOperators_logical(self) -> None:
        p = parser.Parser(vocabulary=parser.PyOperators())
        peval: AnyOp = lambda expr, *args: p.parse(expr).eval(*args)

        # Boolean OR
        with self.subTest(symbol='or'):
            self.assertCaseEqual(peval, [
                Case(('x or y', True, False), {}, True),
                Case(('x or y', False, True), {}, True),
                Case(('x or y', False, False), {}, False),
                Case(('x or y', True, True), {}, True)])

        # Boolean AND
        with self.subTest(symbol='and'):
            self.assertCaseEqual(peval, [
                Case(('x and y', True, False), {}, False),
                Case(('x and y', False, True), {}, False),
                Case(('x and y', False, False), {}, False),
                Case(('x and y', True, True), {}, True)])

        # Boolean NOT
        with self.subTest(symbol='not'):
            self.assertCaseEqual(peval, [
                Case(('not(x)', True), {}, False),
                Case(('not(x)', False), {}, True)])

    def test_PyOperators_comparison(self) -> None:
        p = parser.Parser(vocabulary=parser.PyOperators())
        peval: AnyOp = lambda expr, *args: p.parse(expr).eval(*args)

        # Equality
        with self.subTest(symbol='=='):
            self.assertCaseEqual(peval, [
                Case(('x == y', 1, 1), {}, True),
                Case(('x == y', 1, 2), {}, False),
                Case(('x == y', 'a', 'a'), {}, True),
                Case(('x == y', 'a', 'b'), {}, False)])

        # Inequality
        with self.subTest(symbol='!='):
            self.assertCaseEqual(peval, [
                Case(('x != y', 1, 1), {}, False),
                Case(('x != y', 1, 2), {}, True),
                Case(('x != y', 'a', 'a'), {}, False),
                Case(('x != y', 'a', 'b'), {}, True)])

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

        # Identity
        with self.subTest(symbol='is'):
            self.assertCaseEqual(peval, [
                Case(('x is y', True, True), {}, True),
                Case(('x is y', True, False), {}, False)])

        # Containment
        with self.subTest(symbol='in'):
            self.assertCaseEqual(peval, [
                Case(('x in y', 'a', 'a'), {}, True),
                Case(('x in y', 'a', 'b'), {}, False),
                Case(('x in y', 'a', 'ba'), {}, True),
                Case(('x in y', 'ab', 'ba'), {}, False)])

    def test_PyOperators_bitwise(self) -> None:
        p = parser.Parser(vocabulary=parser.PyOperators())
        peval: AnyOp = lambda expr, *args: p.parse(expr).eval(*args)

        # Bitwise Inversion
        with self.subTest(symbol='~'):
            self.assertCaseEqual(peval, [
                Case(('~x', 0), {}, -1),
                Case(('~x', -1), {}, 0),
                Case(('~x', 1), {}, -2),
                Case(('~x', -2), {}, 1),
                Case(('~(~x)', 3), {}, 3)])

        # Bitwise Right Shift
        with self.subTest(symbol='>>'):
            self.assertCaseEqual(peval, [
                Case(('x >> y', 1, 1), {}, 0),
                Case(('x >> y', 2, 2), {}, 0),
                Case(('x >> y', 1, 2), {}, 0),
                Case(('x >> y', 2, 1), {}, 1)])

        # Bitwise Left Shift
        with self.subTest(symbol='>>'):
            self.assertCaseEqual(peval, [
                Case(('x << y', 1, 1), {}, 2),
                Case(('x << y', 2, 2), {}, 8),
                Case(('x << y', 1, 2), {}, 4),
                Case(('x << y', 2, 1), {}, 4)])

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

    def test_PyOperators_arithmetic(self) -> None:
        p = parser.Parser(vocabulary=parser.PyOperators())
        peval: AnyOp = lambda expr, *args: p.parse(expr).eval(*args)

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

        # Exponentiation
        with self.subTest(symbol='**'):
            self.assertCaseEqual(peval, [
                Case(('x ** y', 1, 1), {}, 1),
                Case(('x ** y', 1., 1), {}, 1.),
                Case(('x ** y', 4, .5), {}, 2.),
                Case(('x ** y', 2, 2.), {}, 4.)])

        # Division
        with self.subTest(symbol='/'):
            self.assertCaseEqual(peval, [
                Case(('x / y', 1, 1), {}, 1.),
                Case(('x / y', 2, 1), {}, 2.),
                Case(('x / y', 1, .2), {}, 5.),
                Case(('x / y', 1, 2), {}, .5)])

        # Floor Division
        with self.subTest(symbol='//'):
            self.assertCaseEqual(peval, [
                Case(('x // y', 1, 1), {}, 1),
                Case(('x // y', 2, 1), {}, 2),
                Case(('x // y', 1, .2), {}, 4),
                Case(('x // y', 1, 2), {}, 0)])

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

        # Matrix Product
        with self.subTest(symbol='@'):
            N = np.matrix([(0, 0), (0, 0)]) # Zero Matrix
            I = np.matrix([(1, 0), (0, 1)]) # Identity Matrix
            C = np.matrix([(0, 1), (1, 0)]) # Row Exchange Matrix
            X = np.matrix([(1, 0), (0, 0)]) # Projection to 'x' Component
            Y = np.matrix([(0, 0), (0, 1)]) # Projection to 'y' Component

            self.assertCaseEqual(peval, [
                Case(('X @ Y', I, I), {}, I),
                Case(('X @ Y', I, X), {}, X),
                Case(('X @ Y', Y, I), {}, Y),
                Case(('X @ Y', N, I), {}, N),
                Case(('X @ Y', X, N), {}, N),
                Case(('X @ Y', C, C), {}, I),
                Case(('X @ Y', X, Y), {}, N)])

    def test_PyBuiltin(self) -> None:
        # The parser evaluation of the Python Builtin Vocabulary is seperately
        # tested within individual categories
        pass

    def test_PyBuiltin_constants(self) -> None:
        p = parser.Parser(vocabulary=parser.PyBuiltin())
        peval: AnyOp = lambda expr, *args: p.parse(expr).eval(*args)

        # Builtin Constants
        self.assertCaseEqual(peval, [
            Case(('True', ), {}, True),
            Case(('False', ), {}, False),
            Case(('None', ), {}, None),
            Case(('Ellipsis', ), {}, Ellipsis)])

    def test_PyBuiltin_types(self) -> None:
        p = parser.Parser(vocabulary=parser.PyBuiltin())
        peval: AnyOp = lambda expr, *args: p.parse(expr).eval(*args)

        # Builtin Number Types
        self.assertCaseEqual(peval, [
            Case(('bool(x)', 1), {}, True),
            Case(('complex(x)', 1), {}, 1+0j),
            Case(('float(x)', 1), {}, 1.),
            Case(('int(x)', 1.), {}, 1.)])

        # Builtin Container Types
        self.assertCaseEqual(peval, [
            Case(('bytearray(x)', 1), {}, bytearray(b'\x00')),
            Case(('bytearray(x, e)', 'x', 'utf8'), {}, bytearray(b'x')),
            Case(('bytes(x)', 1), {}, b'\x00'),
            Case(('bytes(x, e)', 'x', 'utf8'), {}, b'x'),
            Case(('dict(s)', [(1, 1)]), {}, {1: 1}),
            Case(('frozenset(l)', [1, 2]), {}, frozenset([1, 2])),
            Case(('list(a)', (1, 2, 3)), {}, [1, 2, 3]),
            Case(('list(memoryview(x))', b'x'), {}, [120]),
            Case(('str(o)', list()), {}, '[]'),
            Case(('set(l)', [1, 2, 3]), {}, {1, 2, 3}),
            Case(('tuple(l)', [1, 2, 3]), {}, (1, 2, 3))])

        # Further Builtin Types
        # Note: object and type are tested within test_PyBuiltin_oop()
        self.assertCaseEqual(peval, [
            Case(('slice(n)', 3), {}, slice(3))])

    def test_PyBuiltin_conversion(self) -> None:
        p = parser.Parser(vocabulary=parser.PyBuiltin())
        peval: AnyOp = lambda expr, *args: p.parse(expr).eval(*args)

        # Conversion
        self.assertCaseEqual(peval, [
            Case(('ascii(x)', 1), {}, '1'),
            Case(('bin(x)', 1), {}, '0b1'),
            Case(('chr(x)', 65), {}, 'A'),
            Case(('format(x)', 'A'), {}, 'A'),
            Case(('hex(x)', 1), {}, '0x1'),
            Case(('oct(x)', 1), {}, '0o1'),
            Case(('ord(x)', 'A'), {}, 65)])

    def test_PyBuiltin_math(self) -> None:
        p = parser.Parser(vocabulary=parser.PyBuiltin())
        peval: AnyOp = lambda expr, *args: p.parse(expr).eval(*args)

        # Simple mathematical functions
        self.assertCaseEqual(peval, [
            Case(('abs(x)', -1), {}, 1),
            Case(('divmod(a, b)', 2, 1), {}, (2, 0)),
            Case(('max(l)', [1, 2, 3]), {}, 3),
            Case(('min(l)', [1, 2, 3]), {}, 1),
            Case(('pow(x, y)', 2, 2), {}, 4),
            Case(('round(x)', .6), {}, 1),
            Case(('sum(l)', [1, 2, 3]), {}, 6)])

    def test_PyBuiltin_oop(self) -> None:
        p = parser.Parser(vocabulary=parser.PyBuiltin())
        peval: AnyOp = lambda expr, *args: p.parse(expr).eval(*args)

        # Builtin Types for Object Oriented Programming
        self.assertCaseEqual(peval, [
            Case(('isinstance(object(), c)', object), {}, True),
            Case(('type(o)', object), {}, type)])

        # Builtin functions for Object and Class Tree Organisation
        self.assertCaseEqual(peval, [
            Case(('isinstance(a, b)', 1, int), {}, True),
            Case(('issubclass(a, b)', int, int), {}, True)])

        # Builtin functions for Attribute Organisation
        self.assertCaseEqual(peval, [
            Case(('delattr(o, a)', mock.Mock(), 'a'), {}, None),
            Case(('dir(o)', object), {}, dir(object)),
            Case(('getattr(o, a)', 1j, 'imag'), {}, 1.),
            Case(('hasattr(o, a)', 1j, 'imag'), {}, True),
            Case(('setattr(o, a, v)', mock.Mock(), 'a', 0), {}, None)])

        # Builtin functions for special Methods
        self.assertCaseEqual(peval, [
            Case(('bool(classmethod(o))', object), {}, True),
            Case(("hasattr(property(), 'getter')", ), {}, True),
            Case(("hasattr(staticmethod(f), '__func__')", list), {}, True)])

        # Builtin functions for special Attributes
        self.assertCaseEqual(peval, [
            Case(('callable(o)', object), {}, True),
            Case(('hash(o)', 1), {}, 1),
            Case(('len(o)', [1, 2, 3]), {}, 3),
            Case(('repr(o)', 'x'), {}, "'x'"),
            Case(('sorted(vars(o))', type), {}, sorted(vars(type)))])

    def test_PyBuiltin_functional(self) -> None:
        p = parser.Parser(vocabulary=parser.PyBuiltin())
        peval: AnyOp = lambda expr, *args: p.parse(expr).eval(*args)

        # Functional Programming and Iterator functions
        self.assertCaseEqual(peval, [
            Case(('all(l)', [1, 1, 0]), {}, False),
            Case(('any(l)', [1, 1, 0]), {}, True),
            Case(('list(enumerate(l))', [1, 2]), {}, [(0, 1), (1, 2)]),
            Case(('list(filter(None, l))', []), {}, []),
            Case(('list(iter(l))', [1, 2, 3]), {}, [1, 2, 3]),
            Case(('list(map(f, l))', bool, [0]), {}, [False]),
            Case(('next(iter(l))', [1, 2, 3]), {}, 1),
            Case(('list(range(n))', 3), {}, [0, 1, 2]),
            Case(('sorted(l)', [3, 2, 1]), {}, [1, 2, 3]),
            Case(('list(zip(l, l))', range(2)), {}, [(0, 0), (1, 1)])])

    def test_PyBuiltin_runtime(self) -> None:
        p = parser.Parser(vocabulary=parser.PyBuiltin())
        peval: AnyOp = lambda expr, *args: p.parse(expr).eval(*args)

        # Runtime Evaluation and Meta Programming
        # TODO: Untested functions: breakpoint(), help(), input(), print()
        self.assertCaseEqual(peval, [
            Case(('bool(compile(a, b, c))', '1', '1', 'eval'), {}, True),
            Case(('eval(e)', 'True'), {}, True),
            Case(('exec(e)', 'True'), {}, None),
            Case(('bool(globals())', ), {}, True),
            Case(('id(x)', None), {}, id(None)),
            Case(('bool(locals())', ), {}, True)])

    def test_Parser(self) -> None:
        # Implicitely tested within test_PyOperators(), test_PyBuiltin() and
        # test_PyExprEval()
        pass

    def test_PyExprEval(self) -> None:
        p = parser.Parser(vocabulary=parser.PyExprEval())
        peval: AnyOp = lambda expr, *args: p.parse(expr).eval(*args)

        self.assertCaseEqual(peval, [
            Case(("Ee1", 2), {}, 2),
            Case(("Ee1 + 1", 1), {}, 2),
            Case(('2^x', 3), {}, 8.),
            Case(('2 - 3^x', 4), {}, -79.),
            Case(('-2 - 3^x', 4), {}, -83.),
            Case(('-3^x', 4), {}, -81.),
            Case(('(-3)^x', 4), {}, 81.),
            Case(('2*x + y', 4, 1), {}, 9),
            Case(("'x' == 'x'", ), {}, True),
            Case(("(a + b) == c", 1, 2, 3), {}, True),
            Case(("(a + b) != c", 1, 2, 3), {}, False),
            Case(("x || y", 'hi ', 'u'), {}, 'hi u'),
            Case(("'x' || 'y'", ), {}, 'xy'),
            Case(("concat('hi', ' ', 'u')", ), {}, 'hi u'),
            Case(('if(a>b, 5, 6)', 8, 3), {}, 5),
            Case(('if(a, b, c)', None, 1, 3), {}, 3),
            Case(('a, 3', [1, 2]), {}, [1, 2, 3]),
            Case((".1", ), {}, .1),
            Case((".5^3", ), {}, .125),
            Case(("16^.5", ), {}, 4.),
            Case(("8300*.8", ), {}, 6640.),
            Case(('"abc"*2', 2), {}, 'abcabc'),
            Case(("a^2-b^2==(a+b)*(a-b)", 12, 4), {}, True),
            Case(("a^2-b^2+1==(a+b)*(a-b)", 5, 2), {}, False),
            Case(("concat('a\n','\n','\rb')=='a\n\n\rb'", ), {}, True),
            Case(("a==''", ''), {}, True)])

        self.assertRaises(ValueError, peval, '..5')

    def test_Expression(self) -> None:
        pass # Explicitely tested by partial test of the methods

    def test_Expression_subst(self) -> None:
        p = parser.Parser(vocabulary=parser.PyExprEval())
        peval: AnyOp = lambda e, v, w, *args: p.parse(e).subst(v, w).eval(*args)

        self.assertCaseEqual(peval, [
            Case(('2*x + 1', 'x', '4*x', 3), {}, 25),
            Case(('a + 1', 'a', 'b', 3), {}, 4)])

    def test_Expression_simplify(self) -> None:
        p = parser.Parser(vocabulary=parser.PyExprEval())
        psubs: AnyOp = lambda e, d, *args: p.parse(e).simplify(d).eval(*args)
        pvars: AnyOp = lambda e, d: p.parse(e).simplify(d).variables

        # expr = p.parse('x * (y * atan(1))').simplify({'y': 4})
        # self.assertIn('x*3.141592', expr.to_string())

        self.assertCaseEqual(psubs, [
            Case(("x / ((x + y))", {}, 1, 1), {}, .5),
            Case(('x * (y * 1)', {'y': 4}, 2), {}, 8)])

        self.assertCaseEqual(pvars, [
            Case(('x * (y * atan(1))', {'y': 4}), {}, ('x', ))])

    def test_Expression_to_string(self) -> None:
        p = parser.Parser(vocabulary=parser.PyExprEval())
        pstr: AnyOp = lambda e: str(p.parse(e))

        self.assertCaseEqual(pstr, [
            Case(("'a'=='b'", ), {}, "'a' == 'b'"),
            Case(("func(a,1.51,'ok')", ), {}, "func(a, 1.51, 'ok')")])

    def test_Expression_variables(self) -> None:
        p = parser.Parser(vocabulary=parser.PyExprEval())
        pvars: AnyOp = lambda e: p.parse(e).variables

        self.assertCaseEqual(pvars, [
            Case(('x * (y * atan(1))', ), {}, ('x', 'y')),
            Case(('pow(x, y)', ), {}, ('x', 'y')),
            Case(("PI", ), {}, tuple()),
            Case(("PI ", ), {}, tuple()),
            Case(("E ", ), {}, tuple()),
            Case((" E", ), {}, tuple()),
            Case(("E", ), {}, tuple()),
            Case(("E+1", ), {}, tuple()),
            Case(("E/1", ), {}, tuple()),
            Case(("sin(PI)+E", ), {}, tuple()),
            Case(('Pie', ), {}, ('Pie', )),
            Case(('PIe', ), {}, ('PIe', )),
            Case(('Eval', ), {}, ('Eval', )),
            Case(('Eval1', ), {}, ('Eval1', )),
            Case(('EPI', ), {}, ('EPI', )),
            Case(('PIE', ), {}, ('PIE', )),
            Case(('Engage', ), {}, ('Engage', )),
            Case(('Engage * PIE', ), {}, ('Engage', 'PIE')),
            Case(('Engage_', ), {}, ('Engage_', )),
            Case(('Engage1', ), {}, ('Engage1', )),
            Case(('E1', ), {}, ('E1', )),
            Case(('PI2', ), {}, ('PI2', )),
            Case(('(E1 + PI)', ), {}, ('E1', )),
            Case(('E1_', ), {}, ('E1_', )),
            Case(('E_', ), {}, ('E_', ))])

    def test_Parser_symbols(self) -> None:
        p = parser.Parser(vocabulary=parser.PyExprEval())
        psyms: AnyOp = lambda e: p.parse(e).symbols

        self.assertCaseEqual(psyms, [
            Case(('pow(x,y)', ), {}, ('pow', 'x', 'y'))])

    def test_Token(self) -> None:
        pass # Implicitely tested by test_Parser
