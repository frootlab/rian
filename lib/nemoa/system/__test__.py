# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

import nemoa

from nemoa.base import test

class TestCase(test.GenericTestCase):

    def test_system_import(self):
        with self.subTest(filetype = "ini"):
            from nemoa.base import nclass
            system = nemoa.system.open('dbn', workspace = 'testsuite')
            test = nclass.hasbase(system, 'System')
            self.assertTrue(test)
