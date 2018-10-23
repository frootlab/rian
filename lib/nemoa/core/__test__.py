# -*- coding: utf-8 -*-
"""Unittests for submodules of package 'nemoa.core'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from nemoa.core import stdio
from nemoa.test import ModuleTestCase
from nemoa.types import Module

class TestStdio(ModuleTestCase):
    """Testcase for the module nemoa.core.stdio."""

    module = 'nemoa.core.stdio'

    def test_get_ttylib(self) -> None:
        self.assertIsInstance(stdio.get_ttylib(), Module)

    def test_Getch(self) -> None:
        obj = stdio.Getch() if callable(stdio.Getch) else None
        self.assertIsInstance(obj, stdio.GetchBase)
