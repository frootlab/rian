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
"""Unittests for module 'nemoa.math.regress'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from nemoa.math import regress, test

#
# Test Cases
#

class TestRegress(test.MathModule):
    module = regress

    def test_Error(self) -> None:
        pass # Not required to test

    def test_errors(self) -> None:
        errs = regress.errors()
        self.assertIsInstance(errs, list)
        self.assertTrue(errs)

    def test_error(self) -> None:
        for name in regress.errors():
            with self.subTest(name=name):
                self.assertIsSemiMetric(regress.error, name=name)

    def test_sad(self) -> None:
        self.assertIsSemiMetric(regress.sad)

    def test_rss(self) -> None:
        self.assertIsSemiMetric(regress.rss)

    def test_mae(self) -> None:
        self.assertIsSemiMetric(regress.mae)

    def test_mse(self) -> None:
        self.assertIsSemiMetric(regress.mse)

    def test_rmse(self) -> None:
        self.assertIsSemiMetric(regress.rmse)
