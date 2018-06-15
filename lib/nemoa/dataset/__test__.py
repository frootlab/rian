# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import numpy

class TestSuite(nemoa.common.unittest.TestSuite):

    def test_dataset_import(self):
        with self.subTest(filetype = "csv"):
            dataset = nemoa.dataset.open('sinus', workspace = 'testsuite')
            test = nemoa.common.type.isdataset(dataset)
            self.assertTrue(test)
        with self.subTest(filetype = "tab"):
            dataset = nemoa.dataset.open('linear', workspace = 'testsuite')
            test = nemoa.common.type.isdataset(dataset)
            self.assertTrue(test)

    def test_dataset_evaluate(self):
        dataset = nemoa.dataset.open('linear', workspace = 'testsuite')
        with self.subTest(evaluate = "test_gauss"):
            evaluate = dataset.evaluate('test_gauss')
            self.assertTrue(evaluate)
        with self.subTest(evaluate = "test_binary"):
            evaluate = dataset.evaluate('test_binary')
            self.assertTrue(evaluate != True)
        with self.subTest(evaluate = "covariance"):
            evaluate = dataset.evaluate('covariance')[0][4]
            self.assertEqual(numpy.around(evaluate, 3), 0.544)
        with self.subTest(evaluate = "correlation"):
            evaluate = dataset.evaluate('correlation')[0][4]
            self.assertEqual(numpy.around(evaluate, 3), 0.538)
        with self.subTest(evaluate = "pca", embed = False):
            evaluate = dataset.evaluate('pca', embed = False)[0][0]
            self.assertEqual(numpy.around(evaluate, 3), -3.466)
        with self.subTest(evaluate = "pca", embed = True):
            evaluate = dataset.evaluate('pca', embed = True)[0][0]
            self.assertEqual(numpy.around(evaluate, 3), -1.693)
        with self.subTest(evaluate = "kcorrelation"):
            evaluate = dataset.evaluate('kcorrelation')[0][2]
            self.assertEqual(numpy.around(evaluate, 3), 0.141)

    def test_dataset_create(self):
        with self.subTest(create = "rules"):
            dataset = nemoa.dataset.create('rules',
                name = 'example',
                columns = ['i1', 'i2', 'i3', 'i4', 'o1', 'o2'],
                initialize = 'gauss + bernoulli', sdev = 0.1, abin = 0.5,
                rules = [('o1', 'i1 + i2'), ('o2', 'i3 + i4')],
                normalize = 'gauss',
                samples = 10000)
            test = nemoa.common.type.isdataset(dataset)
            self.assertTrue(test)
