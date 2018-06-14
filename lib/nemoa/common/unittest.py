# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import unittest

class TestSuite(unittest.TestCase):

    def setUp(self):
        self.mode = nemoa.get('mode')
        self.workspace = nemoa.get('workspace')
        nemoa.set('mode', 'silent')

    def tearDown(self):
        nemoa.set('mode', self.mode)
