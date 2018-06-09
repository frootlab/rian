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

    def test_nemoa_dataset_import_csv(self):
        dataset = nemoa.dataset.open('sinus', workspace = 'testsuite')
        test = nemoa.common.type.isdataset(dataset)
        self.assertTrue(test)

    def test_nemoa_dataset_import_tab(self):
        dataset = nemoa.dataset.open('linear', workspace = 'testsuite')
        test = nemoa.common.type.isdataset(dataset)
        self.assertTrue(test)

    def test_nemoa_dataset_evaluate_gauss(self):
        dataset = nemoa.dataset.open('linear', workspace = 'testsuite')
        test = dataset.evaluate('test_gauss')
        self.assertTrue(test)

    def test_nemoa_dataset_evaluate_binary(self):
        dataset = nemoa.dataset.open('linear', workspace = 'testsuite')
        test = not dataset.evaluate('test_binary') == True
        self.assertTrue(test)

    def test_nemoa_dataset_create_rules(self):
        dataset = nemoa.dataset.create('rules',
            name = 'example',
            columns = ['i1', 'i2', 'i3', 'i4', 'o1', 'o2'],
            initialize = 'gauss + bernoulli', sdev = 0.1, abin = 0.5,
            rules = [
                ('o1', 'i1 + i2'),
                ('o2', 'i3 + i4')],
            normalize = 'gauss',
            samples = 10000)
        test = nemoa.common.type.isdataset(dataset)
        self.assertTrue(test)
