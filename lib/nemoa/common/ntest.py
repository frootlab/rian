# -*- coding: utf-8 -*-
"""Testcases including setup and teardown for nemoa."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import unittest

class TestSuite(unittest.TestCase):

    def setUp(self):
        try:
            import nemoa
        except ImportError as err:
            raise ImportError(
                "requires package nemoa: "
                "http://fishroot.github.io/nemoa/") from err

        self.mode = nemoa.get('mode')
        self.workspace = nemoa.get('workspace')
        nemoa.set('mode', 'silent')

    def tearDown(self):
        try:
            import nemoa
        except ImportError as err:
            raise ImportError(
                "requires package nemoa: "
                "http://fishroot.github.io/nemoa/") from err

        nemoa.set('mode', self.mode)
