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

import functools
import inspect
from typing import Any, Callable, Dict, List, NamedTuple, Tuple
import unittest
import numpy as np
from nemoa.base import otree
from nemoa.types import AnyOp, Method, ErrMeta, Module, Function, NpArray

Cases = List['Case']

################################################################################
# Global Test Settings
################################################################################

skip_completeness_test: bool = False

################################################################################
# Parameter Classes
################################################################################

class Case(NamedTuple):
    """Class for the storage of Case parameters."""

    args: Tuple[Any, ...] = tuple()
    kwds: Dict[Any, Any] = {}
    value: Any = None

################################################################################
# Test Cases
################################################################################

class GenericTest(unittest.TestCase):
    """Custom testcase."""

    def assertExactEqual(self, a: object, b: object) -> None:
        """Assert that two objects are equal in type and value."""
        self.assertEqual(type(a), type(b))
        self.assertEqual(a, b)

    def assertAllEqual(self, a: object, b: object) -> None:
        """Assert that two objects are equal."""
        if isinstance(a, np.ndarray):
            self.assertTrue(np.alltrue(a == b))
        else:
            self.assertEqual(a, b)

    def assertNotRaises(
            self, cls: ErrMeta, func: AnyOp, *args: Any, **kwds: Any) -> None:
        """Assert that an exception is not raised."""
        try:
            func(*args, **kwds)
        except cls:
            raise AssertionError(
                f"function {func.__name__} raises error {cls.__name__}")

    def assertIsSubclass(self, cls: type, supercls: type) -> None:
        """Assert that a class is a subclass of another."""
        self.assertTrue(issubclass(cls, supercls))

    def assertCaseIsSubclass(
            self, func: AnyOp, supercls: type, cases: Cases) -> None:
        """Assert outcome type of a class constructor."""
        for case in cases:
            with self.subTest(case):
                self.assertIsSubclass(func(*case.args, **case.kwds), supercls)

    def assertCaseIn(self, func: AnyOp, cases: Cases) -> None:
        """Assert that all function evaluations are in the given values."""
        for case in cases:
            with self.subTest(case):
                self.assertIn(func(*case.args, **case.kwds), case.value)

    def assertCaseNotIn(self, func: AnyOp, cases: Cases) -> None:
        """Assert that all function evaluations are in the given values."""
        for case in cases:
            with self.subTest(case):
                self.assertNotIn(func(*case.args, **case.kwds), case.value)

    def assertCaseContain(self, func: AnyOp, cases: Cases) -> None:
        """Assert that all function evaluations comprise the given values."""
        for case in cases:
            with self.subTest(case):
                self.assertIn(case.value, func(*case.args, **case.kwds))

    def assertCaseNotContain(self, func: AnyOp, cases: Cases) -> None:
        """Assert that all function evaluations comprise the given values."""
        for case in cases:
            with self.subTest(case):
                self.assertNotIn(case.value, func(*case.args, **case.kwds))

    def assertCaseTrue(self, func: AnyOp, cases: Cases) -> None:
        """Assert that all function evaluations cast to True."""
        for case in cases:
            with self.subTest(case):
                self.assertTrue(func(*case.args, **case.kwds))

    def assertCaseFalse(self, func: AnyOp, cases: Cases) -> None:
        """Assert that all function evaluations cast to False."""
        for case in cases:
            with self.subTest(case):
                self.assertFalse(func(*case.args, **case.kwds))

    def assertCaseEqual(self, func: AnyOp, cases: Cases) -> None:
        """Assert that all function evaluations equal the given values."""
        for case in cases:
            with self.subTest(case):
                self.assertAllEqual(func(*case.args, **case.kwds), case.value)

    def assertCaseNotEqual(self, func: AnyOp, cases: Cases) -> None:
        """Assert that all function evaluations differ from the given values."""
        for case in cases:
            with self.subTest(case):
                self.assertNotEqual(func(*case.args, **case.kwds), case.value)

    def assertCaseRaises(self, cls: ErrMeta, func: AnyOp, cases: Cases) -> None:
        """Assert that all function parameters raise an exception."""
        for case in cases:
            with self.subTest(case):
                self.assertRaises(cls, func, *case.args, **case.kwds)

    def assertCaseNotRaises(
            self, cls: ErrMeta, func: AnyOp, cases: Cases) -> None:
        """Assert that no function parameter raises an exception."""
        for case in cases:
            with self.subTest(case):
                self.assertNotRaises(cls, func, *case.args, **case.kwds)

class ModuleTest(GenericTest):
    """Custom testcase."""

    module: Module
    test_completeness: bool = True

    def assertModuleIsComplete(self) -> None:
        """Assert that all members of module are tested."""
        if not hasattr(self, 'module') or not self.test_completeness:
            return

        # Get reference to module
        module = getattr(self, 'module', None)
        if not isinstance(module, Module):
            raise AssertionError(f"module has not been specified")

        # Get module members
        members = set()
        candidates = getattr(module, '__all__', None)
        if not candidates:
            LruWrapper = functools._lru_cache_wrapper # pylint: disable=W0212
            classinfo = (type, Function, LruWrapper)
            candidates = otree.get_members(module, classinfo=classinfo)
        for name in candidates:
            if name.startswith('_'):
                continue # Filter protected members
            obj = getattr(module, name)
            if obj.__module__ != module.__name__:
                continue # Filter imported members
            if BaseException in getattr(obj, '__mro__', []):
                continue # Filter exceptions
            if inspect.isabstract(obj):
                continue # Filter abstract classes
            members.add(name)

        # Get tested module members
        tested = set(name[5:] for name in otree.get_members(
            self, classinfo=Method, pattern='test_*'))

        # Get untested module members
        untested = members - tested
        if not untested:
            return

        # Raise error on untested module members
        raise AssertionError(
            f"module '{self.module.__name__}' comprises "
            f"untested members: {', '.join(sorted(untested))}")

    @unittest.skipIf(skip_completeness_test, "completeness is not tested")
    def test_completeness_of_module(self) -> None:
        self.assertModuleIsComplete()

class MathTest(GenericTest):
    """Additional asserts for math tests."""

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
