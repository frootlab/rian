# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa

class TestSuite(nemoa.common.unittest.TestSuite):

    def test_common_dict(self):
        with self.subTest(function = "merge"):
            d1, d2, d3 = {'a': 1}, {'a': 2, 'b': 2}, {'c': 3}
            test = nemoa.common.dict.merge(d1, d2, d3)['a'] == 1
            test &= len(d3) == 1
            self.assertTrue(test)
