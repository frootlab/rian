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
"""Unittests for module 'nemoa.base.literal'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import datetime
import pathlib
from nemoa.base import literal
import test
from test import Case

#
# Test Cases
#

class TestLiteral(test.ModuleTest):
    module = literal

    def test_as_path(self) -> None:
        self.assertCaseEqual(literal.as_path, [
            Case(args=('a/b/c', ), value=pathlib.Path('a/b/c')),
            Case(args=('%cwd%/test', ), value=pathlib.Path.cwd() / 'test'),
            Case(args=('%home%/test', ), value=pathlib.Path.home() / 'test')])

    def test_as_datetime(self) -> None:
        val = datetime.datetime.now()
        self.assertEqual(literal.as_datetime(str(val)), val)

    def test_as_list(self) -> None:
        self.assertCaseEqual(literal.as_list, [
            Case(args=('a, 2, ()', ), value=['a', '2', '()']),
            Case(args=('[1, 2, 3]', ), value=[1, 2, 3])])

    def test_as_tuple(self) -> None:
        self.assertCaseEqual(literal.as_tuple, [
            Case(args=('a, 2, ()', ), value=('a', '2', '()')),
            Case(args=('(1, 2, 3)', ), value=(1, 2, 3))])

    def test_as_set(self) -> None:
        self.assertCaseEqual(literal.as_set, [
            Case(args=('a, 2, ()', ), value={'a', '2', '()'}),
            Case(args=('{1, 2, 3}', ), value={1, 2, 3})])

    def test_as_dict(self) -> None:
        self.assertCaseEqual(literal.as_dict, [
            Case(args=("a = 'b', b = 1", ), value={'a': 'b', 'b': 1}),
            Case(args=("'a': 'b', 'b': 1", ), value={'a': 'b', 'b': 1})])

    def test_decode(self) -> None:
        self.assertCaseEqual(literal.decode, [
            Case(args=('text', str), value='text'),
            Case(args=(repr(True), bool), value=True),
            Case(args=(repr(1), int), value=1),
            Case(args=(repr(.5), float), value=.5),
            Case(args=(repr(1+1j), complex), value=1+1j)])

    def test_from_str(self) -> None:
        self.assertCaseEqual(literal.from_str, [
            Case(args=(chr(1) + 'a', 'printable'), value='a'),
            Case(args=('a, b', 'uax-31'), value='ab'),
            Case(args=('max(x)', 'uax-31'),
                kwds={'spacer': '_'}, value='max_x_')])

    def test_encode(self) -> None:
        self.assertCaseEqual(literal.encode, [
            Case(args=(chr(1) + 'a', ),
                kwds={'charset': 'printable'}, value='a'),
            Case(args=('a, b', ),
                kwds={'charset': 'uax-31'}, value='ab')])

    def test_estimate(self) -> None:
        Date = datetime.datetime
        self.assertCaseEqual(literal.estimate, [
            Case(args=('text', ), value=None),
            Case(args=(repr('text'), ), value=str),
            Case(args=(repr(True), ), value=bool),
            Case(args=(repr(1), ), value=int),
            Case(args=(repr(1.), ), value=float),
            Case(args=(repr(1j), ), value=complex),
            Case(args=(str(Date.now()), ), value=Date)])
