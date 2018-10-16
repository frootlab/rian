# -*- coding: utf-8 -*-
"""Testcases including setup and teardown for nemoa."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import unittest

from nemoa.core import napp, nmodule

class TestCase(unittest.TestCase):
    def setUp(self):
        import nemoa
        self.mode = nemoa.get('mode')
        self.workspace = nemoa.get('workspace')
        nemoa.set('mode', 'silent')

    def tearDown(self):
        import nemoa
        nemoa.set('mode', self.mode)

def run_tests():
    import nemoa

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    root = nmodule.root()
    cases = nmodule.search(root, base=TestCase, val='reference')
    print(sorted(cases))
    for name, ref in cases.items():
        suite.addTests(loader.loadTestsFromTestCase(ref))

    # Initialize runner
    runner = unittest.TextTestRunner(verbosity=0)

    # Run testsuite
    nemoa.log('testing nemoa ' + nemoa.__version__)
    result = runner.run(suite)

    return result
