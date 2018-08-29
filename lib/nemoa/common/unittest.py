# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

from unittest import TestCase

class TestSuite(TestCase):

    def setUp(self):
        import nemoa

        self.mode = nemoa.get('mode')
        self.workspace = nemoa.get('workspace')
        nemoa.set('mode', 'silent')

    def tearDown(self):
        import nemoa

        nemoa.set('mode', self.mode)
