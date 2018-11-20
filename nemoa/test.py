# -*- coding: utf-8 -*-
"""Testcases including setup and teardown for nemoa."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from io import StringIO
from typing import NamedTuple
from unittest import skipIf
from unittest import TestCase, TestResult, TestLoader, TestSuite, TextTestRunner
import numpy as np
from nemoa.base import entity, this
from nemoa.types import Any, AnyFunc, ClassInfo, ExcType, Function, Method
from nemoa.types import StringIOLike, Tuple, Dict, List, Callable, NpArray

################################################################################
# Global Setting
################################################################################

skip_completeness_test: bool = False

################################################################################
# Test Parameters
################################################################################

class Case(NamedTuple):
    """Case parameter."""

    args: Tuple[Any, ...] = tuple()
    kwds: Dict[Any, Any] = {}
    value: Any = None

Cases = List[Case]

################################################################################
# Test Cases
################################################################################

class BaseTestCase(TestCase):
    """Custom testcase."""

    def assertAllIn(self, func: AnyFunc, cases: Cases) -> None:
        """Assert that all function evaluations are in the given values."""
        for case in cases:
            with self.subTest(case):
                self.assertIn(func(*case.args, **case.kwds), case.value)

    def assertNoneIn(self, func: AnyFunc, cases: Cases) -> None:
        """Assert that all function evaluations are in the given values."""
        for case in cases:
            with self.subTest(case):
                self.assertNotIn(func(*case.args, **case.kwds), case.value)

    def assertAllComprise(self, func: AnyFunc, cases: Cases) -> None:
        """Assert that all function evaluations comprise the given values."""
        for case in cases:
            with self.subTest(case):
                self.assertIn(case.value, func(*case.args, **case.kwds))

    def assertNoneComprise(self, func: AnyFunc, cases: Cases) -> None:
        """Assert that all function evaluations comprise the given values."""
        for case in cases:
            with self.subTest(case):
                self.assertNotIn(case.value, func(*case.args, **case.kwds))

    def assertAllTrue(self, func: AnyFunc, cases: Cases) -> None:
        """Assert that all function evaluations cast to True."""
        for case in cases:
            with self.subTest(case):
                self.assertTrue(func(*case.args, **case.kwds))

    def assertNoneTrue(self, func: AnyFunc, cases: Cases) -> None:
        """Assert that all function evaluations cast to False."""
        for case in cases:
            with self.subTest(case):
                self.assertFalse(func(*case.args, **case.kwds))

    def assertAllEqual(self, func: AnyFunc, cases: Cases) -> None:
        """Assert that all function evaluations equal the given values."""
        for case in cases:
            with self.subTest(case):
                self.assertEqual(func(*case.args, **case.kwds), case.value)

    def assertNoneEqual(self, func: AnyFunc, cases: Cases) -> None:
        """Assert that all function evaluations differ from the given values."""
        for case in cases:
            with self.subTest(case):
                self.assertNotEqual(func(*case.args, **case.kwds), case.value)

    def assertNotRaises(
            self, Error: ExcType, func: AnyFunc, *args: Any,
            **kwds: Any) -> None:
        """Assert that an exception is not raised."""
        try:
            func(*args, **kwds)
        except Error:
            raise AssertionError(
                f"function {func.__name__} raises error {Error.__name__}")

    def assertAllRaises(
            self, Error: ExcType, func: AnyFunc, cases: Cases) -> None:
        """Assert that all function parameters raise an exception."""
        for case in cases:
            with self.subTest(case):
                self.assertRaises(Error, func, *case.args, **case.kwds)

    def assertNoneRaises(
            self, Error: ExcType, func: AnyFunc, cases: Cases) -> None:
        """Assert that no function parameter raises an exception."""
        for case in cases:
            with self.subTest(case):
                self.assertNotRaises(Error, func, *case.args, **case.kwds)

class ModuleTestCase(BaseTestCase):
    """Custom testcase."""

    module: str
    test_completeness: bool = True

    def assertModuleIsComplete(self) -> None:
        """Assert that all members of module are tested."""
        if not hasattr(self, 'module') or not self.test_completeness:
            return

        # Get reference to module
        ref = entity.get_module(self.module)
        if not ref:
            raise AssertionError(f"module {self.module} does not exist")

        # Get module members
        members = set()
        for name in getattr(ref, '__all__',
            entity.get_members(ref, classinfo=(type, Function))):
            if name.startswith('_'):
                continue # Filter protected members
            if getattr(ref, name).__module__ != ref.__name__:
                continue # Filter imported members
            if BaseException in getattr(getattr(ref, name), '__mro__', []):
                continue # Filter exceptions
            members.add(name)

        # Get tested module members
        tested = set(name[5:] for name in entity.get_members(
            self, classinfo=Method, pattern='test_*'))

        # Get untested module members
        untested = members - tested
        if not untested:
            return

        # Raise error on untested module members
        raise AssertionError(
            f"module '{self.module}' comprises "
            f"untested members: {', '.join(sorted(untested))}")

    @skipIf(skip_completeness_test, "completeness is not tested")
    def test_completeness_of_module(self) -> None:
        self.assertModuleIsComplete()

class MathTestCase(BaseTestCase):
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

#
# Public Module Functions
#

def run(
        classinfo: ClassInfo = TestCase, stream: StringIOLike = StringIO(),
        verbosity: int = 2) -> TestResult:
    """Run all tests if given type."""
    loader = TestLoader()
    suite = TestSuite()
    root = this.get_root()
    cases = entity.search(root, classinfo=classinfo, val='reference')
    for ref in cases.values():
        suite.addTests(loader.loadTestsFromTestCase(ref))
    return TextTestRunner(stream=stream, verbosity=verbosity).run(suite)
