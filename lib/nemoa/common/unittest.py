# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import unittest

class TestSuite(unittest.TestCase):

    def setUp(self):
        try:
            import nemoa
        except ImportError as e:
            raise ImportError("requires package nemoa: "
                "http://fishroot.github.io/nemoa/") from e

        self.mode = nemoa.get('mode')
        self.workspace = nemoa.get('workspace')
        nemoa.set('mode', 'silent')

    def tearDown(self):
        try:
            import nemoa
        except ImportError as e:
            raise ImportError("requires package nemoa: "
                "http://fishroot.github.io/nemoa/") from e

        nemoa.set('mode', self.mode)
