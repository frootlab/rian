# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import unittest

class TestSuite(unittest.TestCase):

    def setUp(self):
        self.mode = nemoa.get('mode')
        nemoa.set('mode', 'silent')

    def tearDown(self):
        nemoa.set('mode', self.mode)

    def test_nemoa_model_import_npz(self):
        model = nemoa.model.open('test', workspace = 'testsuite')
        test = nemoa.common.type.ismodel(model)
        self.assertTrue(test)

    def test_nemoa_model_create_ann(self):
        model = nemoa.model.create(
            dataset = 'linear', network = 'shallow', system = 'ann')
        test = nemoa.common.type.ismodel(model)
        self.assertTrue(test)

    def test_nemoa_model_create_dbn(self):
        model = nemoa.model.create(
            dataset = 'linear', network = 'deep', system = 'dbn')
        test = nemoa.common.type.ismodel(model)
        self.assertTrue(test)
