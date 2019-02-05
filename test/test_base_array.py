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
"""Unittests for module 'nemoa.base.array'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import numpy as np
from nemoa.base import array
from nemoa.types import NaN
import test

#
# Test Cases
#

class TestModule(test.ModuleTest):
    module = array

    def setUp(self) -> None:
        self.x = np.array([[NaN, 1.], [NaN, NaN]])
        self.d = {('a', 'b'): 1.}
        self.tuples = [
            ('this', 1, 1., 1j), ('is', 2, 2., 2j),
            ('awesome', 3, 3., 3j)]
        self.labels = (['a', 'b'], ['a', 'b'])

    def test_cast(self) -> None:
        x = np.array([[NaN, 1.], [NaN, NaN]])
        with self.subTest(x=x):
            self.assertNotRaises(TypeError, array.cast, x)
            self.assertIsInstance(array.cast(x), np.ndarray)

        x = list(range(1000))
        with self.subTest(x=x):
            self.assertNotRaises(TypeError, array.cast, x)
            self.assertIsInstance(array.cast(x), np.ndarray)

        x = set()
        with self.subTest(x=x):
            self.assertRaises(TypeError, array.cast, x)
            self.assertNotRaises(TypeError, array.cast, x, otype=True)

    def test_from_dict(self) -> None:
        x = array.from_dict(self.d, labels=self.labels)
        self.assertTrue(np.allclose(x, self.x, equal_nan=True))

    def test_as_dict(self) -> None:
        d = array.as_dict(self.x, labels=self.labels)
        self.assertEqual(d, self.d)

    def test_from_tuples(self) -> None:
        x = array.from_tuples(self.tuples) # type: ignore
        self.assertEqual(x.tolist(), self.tuples)

    def test_as_tuples(self) -> None:
        dtype = [('', str, 7), ('', int), ('', float), ('', complex)]
        x = np.array(self.tuples, dtype=dtype)
        self.assertEqual(array.as_tuples(x), self.tuples)

    def test_add_cols(self) -> None:
        src = np.array([('a'), ('b')], dtype=[('z', 'U4')])
        tgt = np.array([(1., 2), (3., 4)], dtype=[('x', float), ('y', int)])
        new = array.add_cols(tgt, src, 'z')
        self.assertEqual(new['z'][0], 'a')
