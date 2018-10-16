# -*- coding: utf-8 -*-
"""Testcases including setup and teardown for nemoa."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import unittest
from io import StringIO

from nemoa.core import nmodule

class TestCase(unittest.TestCase):
    pass

def run_tests(
        stream: StringIO = StringIO(),
        verbosity: int = 2) -> unittest.TestResult:
    """Run Testcases."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    root = nmodule.root()
    cases = nmodule.search(root, base=TestCase, val='reference')
    for ref in cases.values():
        suite.addTests(loader.loadTestsFromTestCase(ref))

    # Initialize runner
    runner = unittest.TextTestRunner(stream=stream, verbosity=verbosity)

    # Run testsuite
    return runner.run(suite)
