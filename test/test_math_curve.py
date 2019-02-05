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
"""Unittests for module 'nemoa.math.curve'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import numpy as np
from nemoa.math import curve
import test

#
# Test Cases
#

class TestCurve(test.MathTest, test.ModuleTest):
    module = curve

    def setUp(self) -> None:
        self.x = np.array([[0.0, 0.5], [1.0, -1.0]])

    def test_Curve(self) -> None:
        pass # Testing is not required for Catalog Categories

    def test_Bell(self) -> None:
        pass # Testing is not required for Catalog Categories

    def test_SoftStep(self) -> None:
        pass # Testing is not required for Catalog Categories

    def test_Sigmoid(self) -> None:
        pass # Testing is not required for Catalog Categories

    def test_sigmoids(self) -> None:
        funcs = curve.sigmoids()
        self.assertIsInstance(funcs, list)
        self.assertTrue(funcs)

    def test_sigmoid(self) -> None:
        for func in curve.sigmoids():
            with self.subTest(name=func):
                self.assertIsSigmoid(curve.sigmoid, name=func)

    def test_logistic(self) -> None:
        self.assertIsSigmoid(curve.logistic)
        self.assertCheckSum(curve.logistic, self.x, 2.122459)

    def test_tanh(self) -> None:
        self.assertIsSigmoid(curve.tanh)
        self.assertCheckSum(curve.tanh, self.x, 0.462117)

    def test_tanh_lecun(self) -> None:
        self.assertIsSigmoid(curve.tanh_lecun)
        self.assertCheckSum(curve.tanh_lecun, self.x, 0.551632)

    def test_elliot(self) -> None:
        self.assertIsSigmoid(curve.elliot)
        self.assertCheckSum(curve.elliot, self.x, 0.333333)

    def test_hill(self) -> None:
        self.assertCheckSum(curve.hill, self.x, 0.447213)
        for n in range(2, 10, 2):
            with self.subTest(n=n):
                self.assertIsSigmoid(curve.hill, n=n)

    def test_arctan(self) -> None:
        self.assertIsSigmoid(curve.arctan)
        self.assertCheckSum(curve.arctan, self.x, 0.463647)

    def test_bells(self) -> None:
        funcs = curve.bells()
        self.assertIsInstance(funcs, list)
        self.assertTrue(funcs)

    def test_bell(self) -> None:
        for name in curve.bells():
            with self.subTest(name=name):
                self.assertIsBell(curve.bell, name=name)

    def test_gauss(self) -> None:
        self.assertIsBell(curve.gauss)
        self.assertCheckSum(curve.gauss, self.x, 1.234949)

    def test_dlogistic(self) -> None:
        self.assertIsBell(curve.dlogistic)
        self.assertCheckSum(curve.dlogistic, self.x, 0.878227)

    def test_delliot(self) -> None:
        self.assertIsBell(curve.delliot)
        self.assertCheckSum(curve.delliot, self.x, 1.944444)

    def test_dhill(self) -> None:
        self.assertIsBell(curve.dhill)
        self.assertCheckSum(curve.dhill, self.x, 2.422648)

    def test_dtanh_lecun(self) -> None:
        self.assertIsBell(curve.dtanh_lecun)
        self.assertCheckSum(curve.dtanh_lecun, self.x, 3.680217)

    def test_dtanh(self) -> None:
        self.assertIsBell(curve.dtanh)
        self.assertCheckSum(curve.dtanh, self.x, 2.626396)

    def test_darctan(self) -> None:
        self.assertIsBell(curve.darctan)
        self.assertCheckSum(curve.darctan, self.x, 2.800000)

    def test_dialogistic(self) -> None:
        self.assertIncreasing(curve.dialogistic)
        self.assertCheckSum(curve.dialogistic, self.x, 0.251661)

    def test_softstep(self) -> None:
        self.assertIncreasing(curve.softstep)
        self.assertCheckSum(curve.softstep, self.x, 0.323637)

    def test_multi_logistic(self) -> None:
        self.assertIncreasing(curve.multi_logistic)
        self.assertCheckSum(curve.multi_logistic, self.x, 0.500091)
