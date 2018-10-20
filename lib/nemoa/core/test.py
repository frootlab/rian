# -*- coding: utf-8 -*-
"""Testcases including setup and teardown for nemoa."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import unittest

from unittest import TestCase, TestResult, TestLoader, TestSuite, TextTestRunner
from io import StringIO

from nemoa.core import nmodule, nobject
from nemoa.types import Function, Method, OptStr

#
# Public Module Variables
#

skip_completeness_test: bool = False

#
# Public Module Classes
#

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
                fdict = nobject.members(mref, base=Function)
                for attr in fdict.values():
                    name = attr['name']
                    if not name.startswith('_'):
                        required.add(name)
            tdict = nobject.members(self, base=Method, pattern='test_*')
            implemented = set()
            for attr in tdict.values():
                implemented.add(attr['name'][5:])
            complete = required <= implemented
            utested = ', '.join(required - implemented)
            message = f"utested functions: {utested}"
        else:
            complete = True
        if not complete:
            raise AssertionError(message)

    @unittest.skipIf(skip_completeness_test, "completeness is not tested")
    def test_compleness_of_module(self) -> None:
        """Test if all members of module are testet."""
        self.assertModuleIsComplete()

#
# Public Module Functions
#

def run_tests(
        stream: StringIO = StringIO(), verbosity: int = 2) -> TestResult:
    """Search and run testcases."""
    loader = TestLoader()
    suite = TestSuite()
    root = nmodule.root()
    cases = nmodule.search(root, base=GenericTestCase, val='reference')
    for ref in cases.values():
        suite.addTests(loader.loadTestsFromTestCase(ref))

    # Initialize runner and run testsuite
    return TextTestRunner(stream=stream, verbosity=verbosity).run(suite)
