# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import unittest
import sys
sys.path.append('./package')
import nemoa

class NemoaTestCase(unittest.TestCase):

    def setUp(self):
        nemoa.log('set', mode = 'silent')
        self.workspace = nemoa.open('unittest', base = 'common')

    def test_list_workspaces(self):
        workspaces = nemoa.list()
        test = isinstance(workspaces, list)
        self.assertTrue(test)

    def test_dataset_import_tab(self):
        test = nemoa.common.type.isdataset(nemoa.dataset.open('linear'))
        self.assertTrue(test)

    def test_network_import_ini(self):
        test = nemoa.common.type.isnetwork(nemoa.network.open('deep'))
        self.assertTrue(test)

    def test_system_import_ini(self):
        test = nemoa.common.type.issystem(nemoa.system.open('dbn'))
        self.assertTrue(test)

    def test_model_import_npz(self):
        test = nemoa.common.type.ismodel(nemoa.model.open('test'))
        self.assertTrue(test)

    def test_model_create_ann(self):
        model = nemoa.model.create(
            dataset = 'linear', network = 'shallow', system = 'ann')
        test = nemoa.common.type.ismodel(model)
        self.assertTrue(test)

    def test_model_create_dbn(self):
        model = nemoa.model.create(
            dataset = 'linear', network = 'deep', system = 'dbn')
        test = nemoa.common.type.ismodel(model)
        self.assertTrue(test)

    def test_model_algorithm_shallow_ann(self):
        model = nemoa.model.create(
            dataset = 'linear', network = 'shallow', system = 'ann')
        model.optimize()
        test = model.evaluate('system', 'error') < 0.1
        self.assertTrue(test)

    def test_model_algorithm_deep_dbn(self):
        model = nemoa.model.create(
            dataset = 'linear', network = 'deep', system = 'dbn')
        model.optimize()
        test = model.evaluate('system', 'error') < 0.3
        self.assertTrue(test)

if __name__ == '__main__':
    unittest.main()
