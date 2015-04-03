# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import unittest

_WORKSPACE = None

class NemoaTestCase(unittest.TestCase):

    def setUp(self):
        self.mode = nemoa.get('mode')
        nemoa.set('mode', 'silent')
        self.workspace = _WORKSPACE

    def tearDown(self):
        nemoa.set('mode', self.mode)

    def test_optimize_shallow_ann(self):
        model = nemoa.model.create(
            dataset = 'linear', network = 'shallow', system = 'ann')
        model.optimize()
        test = model.evaluate('error') < 0.1
        self.assertTrue(test)

    def test_optimize_deep_dbn(self):
        model = nemoa.model.create(
            dataset = 'linear', network = 'deep', system = 'dbn')
        model.optimize()
        test = model.evaluate('error') < 0.5
        self.assertTrue(test)

def main(workspace, *args, **kwargs):
    _WORKSPACE = workspace
    suite = unittest.TestLoader().loadTestsFromTestCase(NemoaTestCase)
    nemoa.log('testing nemoa ' + nemoa.__version__)
    unittest.TextTestRunner(verbosity = 2).run(suite)

    return True
