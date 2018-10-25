# -*- coding: utf-8 -*-
"""Testcases including setup and teardown for nemoa."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import unittest
from unittest import TestCase, TestResult, TestLoader, TestSuite, TextTestRunner
from io import StringIO
from nemoa.base import nmodule, bare
from nemoa.types import Any, AnyFunc, ClassInfo, ExcType, Function, Method
from nemoa.types import OptStr, StringIOLike, FuncParList

################################################################################
# Global Setting
################################################################################

skip_completeness_test: bool = False

################################################################################
# Test Cases
################################################################################

class GenericTestCase(TestCase):
    """Custom testcase."""

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
            self, Error: ExcType, func: AnyFunc, cases: FuncParList) -> None:
        """Assert that all function parameters raise an exception."""
        for args, kwds in cases:
            with self.subTest(args=args, kwds=kwds):
                self.assertRaises(Error, func, *args, **kwds)

    def assertNoneRaises(
            self, Error: ExcType, func: AnyFunc, cases: FuncParList) -> None:
        """Assert that no function parameter raises an exception."""
        for args, kwds in cases:
            with self.subTest(args=args, kwds=kwds):
                self.assertNotRaises(Error, func, *args, **kwds)

class ModuleTestCase(GenericTestCase):
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

    @unittest.skipIf(skip_completeness_test, "completeness is not tested")
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
