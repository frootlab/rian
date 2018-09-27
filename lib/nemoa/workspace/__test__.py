# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

import nemoa

from nemoa.common import ntest

class TestSuite(ntest.TestSuite):

    def test_workspace_open(self):
        nemoa.open('testsuite')
        test = nemoa.get('workspace') == 'testsuite'
        self.assertTrue(test)
