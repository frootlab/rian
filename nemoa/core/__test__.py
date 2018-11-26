# -*- coding: utf-8 -*-
"""Unittests for package 'nemoa.core'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from unittest import skipIf
from nemoa.core import tty
from nemoa.test import ModuleTestCase
from nemoa.types import Module

#
# Module Variables
#

ttylib = tty.get_lib().__name__

#
# Test Cases
#

class TestTTY(ModuleTestCase):
    """Testcase for the module nemoa.core.tty."""

    module = 'nemoa.core.tty'

    def test_get_lib(self) -> None:
        self.assertIsInstance(tty.get_lib(), Module)

    def test_get_class(self) -> None:
        self.assertIsSubclass(tty.get_class(), tty.TTYBase)

    def test_get_instance(self) -> None:
        self.assertIsInstance(tty.get_instance(), tty.TTYBase)

    @skipIf(ttylib != 'msvcrt', 'Requires Windows/Msvcrt')
    def test_TTYMsvcrt(self) -> None:
        obj = tty.TTYMsvcrt()

    @skipIf(ttylib != 'termios', 'Requires Unix/Termios')
    def test_TTYTermios(self) -> None:
        obj = tty.TTYTermios()
