# -*- coding: utf-8 -*-
# Copyright (c) 2013-2019 Patrick Michl
#
# This file is part of nemoa, https://frootlab.github.io/nemoa
#
#  nemoa is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  nemoa is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with
#  nemoa. If not, see <http://www.gnu.org/licenses/>.
#

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

import numpy
import nemoa
from flab.base import otree, test
import nemoa.dataset

class TestCase(test.GenericTest):

    def test_dataset_import(self):

        with self.subTest(filetype="csv"):
            dataset = nemoa.dataset.open('sinus', workspace='testsuite')
            test = otree.has_base(dataset, 'Dataset')
            self.assertTrue(test)

        with self.subTest(filetype="tab"):
            dataset = nemoa.dataset.open('linear', workspace='testsuite')
            test = otree.has_base(dataset, 'Dataset')
            self.assertTrue(test)

    def test_dataset_evaluate(self):
        dataset = nemoa.dataset.open('linear', workspace='testsuite')

        with self.subTest("test_gauss"):
            evaluate = dataset.evaluate('test_gauss')
            self.assertTrue(evaluate)

        with self.subTest("test_binary"):
            evaluate = dataset.evaluate('test_binary')
            self.assertFalse(evaluate)

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

        with self.subTest(evaluate="k-correlation"):
            evaluate = dataset.evaluate('k-correlation')[0][2]
            self.assertEqual(numpy.around(evaluate, 3), 0.141)

    def test_dataset_create(self):

        with self.subTest(create="rules"):
            dataset = nemoa.dataset.create('rules',
                name='example',
                columns=['i1', 'i2', 'i3', 'i4', 'o1', 'o2'],
                initialize='gauss + bernoulli',
                sdev=0.1,
                abin=0.5,
                rules=[('o1', 'i1 + i2'), ('o2', 'i3 + i4')],
                normalize='gauss',
                samples=10000)
            test = otree.has_base(dataset, 'Dataset')
            self.assertTrue(test)
