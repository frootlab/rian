# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

import nemoa

from nemoa.common import ntest

class TestSuite(ntest.TestSuite):

    def test_system_import(self):
        with self.subTest(filetype = "ini"):
            from nemoa.common import nclass
            system = nemoa.system.open('dbn', workspace = 'testsuite')
            test = nclass.hasbase(system, 'System')
            self.assertTrue(test)
