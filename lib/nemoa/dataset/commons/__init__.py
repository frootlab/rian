# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.dataset.commons.labels







import unittest

class TestSuite(unittest.TestCase):
    def test_nemoa_dataset_create_rules(self):
        import nemoa

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
