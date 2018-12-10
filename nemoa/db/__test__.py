# -*- coding: utf-8 -*-
"""Unittests for submodules of package 'nemoa.db'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from nemoa.db import table
from nemoa.test import ModuleTestCase

class TestTable(ModuleTestCase):
    """Testcase for the module nemoa.db.table."""

    module = 'nemoa.db.table'

    def setUp(self) -> None:
        # Create test table
        pass

    def test_Cursor(self) -> None:
        pass

    def test_Table(self) -> None:
        pass
