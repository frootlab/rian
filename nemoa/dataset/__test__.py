# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

import numpy
import nemoa
from nemoa.base import entity
from nemoa.test import BaseTestCase

class TestCase(BaseTestCase):

    def test_dataset_import(self):
        import nemoa.dataset

        with self.subTest(filetype="csv"):
            dataset = nemoa.dataset.open('sinus', workspace='testsuite')
            test = entity.has_base(dataset, 'Dataset')
            self.assertTrue(test)

        with self.subTest(filetype="tab"):
            dataset = nemoa.dataset.open('linear', workspace='testsuite')
            test = entity.has_base(dataset, 'Dataset')
            self.assertTrue(test)

    def test_dataset_evaluate(self):
        import nemoa.dataset

        dataset = nemoa.dataset.open('linear', workspace='testsuite')

        with self.subTest("test_gauss"):
            evaluate = dataset.evaluate('test_gauss')
            self.assertTrue(evaluate)

        with self.subTest("test_binary"):
            evaluate = dataset.evaluate('test_binary')
            self.assertTrue(evaluate != True)

        with self.subTest("covariance"):
            evaluate = dataset.evaluate('covariance')[0][4]
            self.assertEqual(numpy.around(evaluate, 3), 0.544)

        with self.subTest("correlation"):
            evaluate = dataset.evaluate('correlation')[0][4]
            self.assertEqual(numpy.around(evaluate, 3), 0.538)

        with self.subTest(evaluate="pca-sample", embed=False):
            evaluate = dataset.evaluate('pca-sample', embed=False)[0][0]
            self.assertEqual(numpy.around(evaluate, 3), -3.466)

        with self.subTest(evaluate="pca-sample", embed=True):
            evaluate = dataset.evaluate('pca-sample', embed=True)[0][0]
            self.assertEqual(numpy.around(evaluate, 3), -1.693)

        with self.subTest(evaluate = "k-correlation"):
            evaluate = dataset.evaluate('k-correlation')[0][2]
            self.assertEqual(numpy.around(evaluate, 3), 0.141)

    def test_dataset_create(self):
        import nemoa.dataset

        with self.subTest(create = "rules"):
            dataset = nemoa.dataset.create('rules',
                name = 'example',
                columns = ['i1', 'i2', 'i3', 'i4', 'o1', 'o2'],
                initialize = 'gauss + bernoulli', sdev = 0.1, abin = 0.5,
                rules = [('o1', 'i1 + i2'), ('o2', 'i3 + i4')],
                normalize = 'gauss',
                samples = 10000)
            test = entity.has_base(dataset, 'Dataset')
            self.assertTrue(test)
