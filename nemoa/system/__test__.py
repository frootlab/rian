# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

import nemoa

from nemoa.base import entity
from nemoa.test import BaseTestCase

class TestCase(BaseTestCase):
    def test_system_import(self):
        with self.subTest(filetype="ini"):
            system = nemoa.system.open('dbn', workspace='testsuite')
            test = entity.has_base(system, 'System')
            self.assertTrue(test)
