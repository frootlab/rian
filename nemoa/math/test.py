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
"""Unittesting for math modules."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from typing import Any, Callable
import numpy as np
from flab.base import test
from nemoa.typing import NpArray

class MathModule(test.ModuleTest):
    """TestCase for math modules."""

    def assertCheckSum(self, func: Callable, x: NpArray, val: float) -> None:
        vsum = func(x).sum()
        self.assertTrue(np.isclose(vsum, val, atol=1e-4))

    def assertNotNegative(self, f: Callable, **kwds: Any) -> None:
        x = 5. * np.random.rand(3, 3, 3) - 5.
        self.assertTrue(np.all(f(x, **kwds) >= 0.),
            f"function '{f.__name__}' contains negative target values")

    def assertNotPositive(self, f: Callable, **kwds: Any) -> None:
        x = 5. * np.random.rand(3, 3, 3) - 5.
        self.assertTrue(np.all(f(x, **kwds) <= 0.),
            f"function '{f.__name__}' contains positive target values")

    def assertIncreasing(self, f: Callable, **kwds: Any) -> None:
        x = np.linspace(-10., 10., num=20)
        self.assertTrue(np.all(np.diff(f(x, **kwds)) >= 0.),
            f"function '{f.__name__}' is not monotonically increasing")

    def assertDecreasing(self, f: Callable, **kwds: Any) -> None:
        x = np.linspace(-10., 10., num=20)
        self.assertTrue(np.all(np.diff(f(x, **kwds)) <= 0.),
            f"function '{f.__name__}' is not monotonically decreasing")

    def assertSingleExtremalPoint(self, f: Callable, **kwds: Any) -> None:
        x = np.linspace(-10., 10., num=20)
        s = np.sign(np.diff(f(x, **kwds)))
        d_s = np.diff(s[s[:] != 0.])
        count = d_s[d_s[:] != 0.].size
        self.assertTrue(count == 1,
            f"function '{f.__name__}' has {count} extremal points")

    def assertSingleInflectionPoint(self, f: Callable, **kwds: Any) -> None:
        x = np.linspace(-10., 10., num=20)
        s = np.sign(np.diff(np.diff(f(x, **kwds))))
        d_s = np.diff(s[s[:] != 0.])
        count = d_s[d_s[:] != 0.].size
        self.assertTrue(count == 1,
            f"function '{f.__name__}' has {count} inflection points")

    def assertIsSigmoid(self, f: Callable, **kwds: Any) -> None:
        # Test monotonicity
        self.assertIncreasing(f, **kwds)
        # Test number of inflection points
        self.assertSingleInflectionPoint(f, **kwds)

    def assertIsBell(self, f: Callable, **kwds: Any) -> None:
        # Test that bell function is not negative
        self.assertNotNegative(f, **kwds)
        # Test number of extremal points
        self.assertSingleExtremalPoint(f, **kwds)

    def assertCoDim(self, f: Callable, codim: int = 0, **kwds: Any) -> None:
        x = np.zeros((3, 3, 3))
        self.assertEqual(x.ndim - f(x, **kwds).ndim, codim)

    def assertConserveZero(self, f: Callable, **kwds: Any) -> None:
        x = np.zeros((3, 3, 3))
        self.assertTrue(np.allclose(f(x, **kwds), 0.))

    def assertSubadditivity(self, f: Callable, **kwds: Any) -> None:
        x = 5. * np.random.rand(3, 3, 3) - 5.
        y = 5. * np.random.rand(3, 3, 3) - 5.
        f_x, f_y = f(x, **kwds), f(y, **kwds)
        f_xy = f(x + y, **kwds)
        self.assertTrue(np.all(f_xy < f_x + f_y + 1e-05))

    def assertAbsoluteHomogeneity(self, f: Callable, **kwds: Any) -> None:
        x = 5. * np.random.rand(3, 3, 3) - 5.
        f_x = f(x, **kwds)
        for alpha in np.linspace(0., 10., num=5):
            f_ax = f(alpha * x, **kwds)
            self.assertTrue(np.allclose(f_ax, float(alpha) * f_x))

    def assertIsNorm(self, f: Callable, **kwds: Any) -> None:
        # Test if norm is negative
        self.assertNotNegative(f, **kwds)
        # Test if norm of zero value is zero
        self.assertConserveZero(f, **kwds)
        # Test subadditivity
        self.assertSubadditivity(f, **kwds)
        # Test absolute homogeneity
        self.assertAbsoluteHomogeneity(f, **kwds)

    def assertIsVectorNorm(self, f: Callable, **kwds: Any) -> None:
        # Test codimension of function
        self.assertCoDim(f, codim=1, **kwds)
        # Test if function is norm
        self.assertIsNorm(f, **kwds)

    def assertIsMatrixNorm(self, f: Callable, **kwds: Any) -> None:
        # Test codimension of function
        self.assertCoDim(f, codim=2, **kwds)
        # Test if function is norm
        self.assertIsNorm(f, **kwds)

    def assertBiNotNegative(self, f: Callable, **kwds: Any) -> None:
        x = 5. * np.random.rand(3, 3, 3) - 5.
        y = 5. * np.random.rand(3, 3, 3) - 5.
        self.assertTrue(np.all(f(x, y, **kwds) >= 0.),
            f"function '{f.__name__}' contains negative target values")

    def assertBinFuncCoDim(
            self, f: Callable, codim: int = 0, **kwds: Any) -> None:
        x = np.zeros((3, 3, 3))
        self.assertEqual(x.ndim - f(x, x, **kwds).ndim, codim)

    def assertTriangleInequality(self, f: Callable, **kwds: Any) -> None:
        x = 5. * np.random.rand(3, 3, 3) - 5.
        y = 5. * np.random.rand(3, 3, 3) - 5.
        z = 5. * np.random.rand(3, 3, 3) - 5.
        f_xy = f(x, y, **kwds)
        f_yz = f(y, z, **kwds)
        f_xz = f(x, z, **kwds)
        self.assertTrue(np.all(f_xz < f_xy + f_yz + 1e-05))

    def assertSymmetric(self, f: Callable, **kwds: Any) -> None:
        x = 5. * np.random.rand(3, 3, 3) - 5.
        y = 5. * np.random.rand(3, 3, 3) - 5.
        f_xy, f_yx = f(x, y, **kwds), f(y, x, **kwds)
        self.assertTrue(np.allclose(f_xy, f_yx),
            f"function '{f.__name__}' is not symmetric")

    def assertIndiscernibilityOfIdenticals(
            self, f: Callable, **kwds: Any) -> None:
        x = 5. * np.random.rand(3, 3, 3) - 5.
        f_xx = f(x, x, **kwds)
        self.assertTrue(np.allclose(f_xx, 0.))

    def assertIsSemiMetric(self, f: Callable, **kwds: Any) -> None:
        # Test if function is not negative
        self.assertBiNotNegative(f, **kwds)
        # Test indiscernibility of identicals
        self.assertIndiscernibilityOfIdenticals(f, **kwds)
        # Test if function is symmetric
        self.assertSymmetric(f, **kwds)

    def assertIsMetric(self, f: Callable, **kwds: Any) -> None:
        # Test if function is semi metric
        self.assertIsSemiMetric(f, **kwds)
        # Test triangle inequality
        self.assertTriangleInequality(f, **kwds)

    def assertIsVectorDistance(self, f: Callable, **kwds: Any) -> None:
        # Test of codimension of function is 1
        self.assertBinFuncCoDim(f, codim=1, **kwds)
        # Test if function is metric
        self.assertIsMetric(f, **kwds)

    def assertIsMatrixDistance(self, f: Callable, **kwds: Any) -> None:
        # Test of codimension of function is 2
        self.assertBinFuncCoDim(f, codim=2, **kwds)
        # Test if function is metric
        self.assertIsMetric(f, **kwds)
