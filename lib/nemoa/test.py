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
from nemoa.base import nmodule, bare
from nemoa.types import Any, AnyFunc, ClassInfo, ExcType, Function, Method
from nemoa.types import OptStr, StringIOLike, Tuple, Dict, List

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
        msg: OptStr = None
        if hasattr(self, 'module') and self.test_completeness:
            mref = nmodule.get_instance(self.module)
            if hasattr(mref, '__all__'):
                required = set(getattr(mref, '__all__'))
            else:
                required = set()
                fdict = bare.get_members_attr(mref, classinfo=Function)
                for attr in fdict.values():
                    name = attr['name']
                    if not name.startswith('_'):
                        required.add(name)
            tdict = bare.get_members_attr(
                self, classinfo=Method, pattern='test_*')
            implemented = set()
            for attr in tdict.values():
                implemented.add(attr['name'][5:])
            complete = required <= implemented
            untested = ', '.join(required - implemented)
            msg = f"untested functions: {untested}"
        else:
            complete = True
        if not complete:
            raise AssertionError(msg)

    @skipIf(skip_completeness_test, "completeness is not tested")
    def test_completeness_of_module(self) -> None:
        self.assertModuleIsComplete()

#
# Public Module Functions
#

def run(
        classinfo: ClassInfo = TestCase, stream: StringIOLike = StringIO(),
        verbosity: int = 2) -> TestResult:
    """Run all tests if given type."""
    loader = TestLoader()
    suite = TestSuite()
    root = nmodule.get_root()
    cases = nmodule.search(ref=root, classinfo=classinfo, val='reference')
    for ref in cases.values():
        suite.addTests(loader.loadTestsFromTestCase(ref))
    return TextTestRunner(stream=stream, verbosity=verbosity).run(suite)
