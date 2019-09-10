# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 Frootlab
# Copyright (C) 2013-2019 Patrick Michl
#
# This file is part of Frootlab Rian, https://www.frootlab.org/rian
#
#  Rian is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rian is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with
#  Rian. If not, see <http://www.gnu.org/licenses/>.
#
"""Unittests for module 'rian.math.regress'."""

__copyright__ = '2019 Frootlab'
__license__ = 'GPLv3'
__docformat__ = 'google'
__author__ = 'Frootlab Developers'
__email__ = 'contact@frootlab.org'
__authors__ = ['Patrick Michl <patrick.michl@frootlab.org>']

from rian.math import regress, test

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
