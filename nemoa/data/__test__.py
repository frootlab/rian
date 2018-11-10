# -*- coding: utf-8 -*-
"""Unittests for submodules of package 'nemoa.data'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import numpy as np
from nemoa.test import ModuleTestCase
from nemoa.data import table

class TestTable(ModuleTestCase):
    """Testcase for the module nemoa.data.table."""

    module = 'nemoa.data.table'

    def test_addcols(self) -> None:
        src = np.array(
            [('a'), ('b')], dtype=[('z', 'U4')])
        tgt = np.array(
            [(1., 2), (3., 4)], dtype=[('x', float), ('y', int)])
        new = table.addcols(tgt, src, 'z')
        self.assertEqual(new['z'][0], 'a')
