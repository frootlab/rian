# -*- coding: utf-8 -*-
"""Testcases including setup and teardown for nemoa."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import unittest

from unittest import TestCase, TestResult, TestLoader, TestSuite, TextTestRunner
from io import StringIO

from nemoa.base import nmodule, nobject
from nemoa.types import ClassInfo, Function, Method, OptStr, StringIOLike

################################################################################
# Global Setting
################################################################################

skip_completeness_test: bool = False

################################################################################
# Test Cases
################################################################################

class GenericTestCase(TestCase):
    """Custom testcase."""

class ModuleTestCase(GenericTestCase):
    """Custom testcase."""

    module: str
    test_completeness: bool = True

    def assertModuleIsComplete(self) -> None:
        """Assert that all members of module are tested."""
        message: OptStr = None
        if hasattr(self, 'module') and self.test_completeness:
            mref = nmodule.inst(self.module)
            if hasattr(mref, '__all__'):
                required = set(getattr(mref, '__all__'))
            else:
                required = set()
                fdict = nobject.get_members(mref, classinfo=Function)
                for attr in fdict.values():
                    name = attr['name']
                    if not name.startswith('_'):
                        required.add(name)
            tdict = nobject.get_members(
                self, classinfo=Method, pattern='test_*')
            implemented = set()
            for attr in tdict.values():
                implemented.add(attr['name'][5:])
            complete = required <= implemented
            untested = ', '.join(required - implemented)
            message = f"untested functions: {untested}"
        else:
            complete = True
        if not complete:
            raise AssertionError(message)

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
    root = nmodule.root()
    cases = nmodule.search(root, classinfo=classinfo, val='reference')
    for ref in cases.values():
        suite.addTests(loader.loadTestsFromTestCase(ref))
    return TextTestRunner(stream=stream, verbosity=verbosity).run(suite)
