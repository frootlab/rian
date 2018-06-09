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

    def test_nemoa_system_import_ini(self):
        system = nemoa.system.open('dbn', workspace = 'testsuite')
        test = nemoa.common.type.issystem(system)
        self.assertTrue(test)
