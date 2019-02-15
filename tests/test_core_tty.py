# -*- coding: utf-8 -*-
# Copyright (c) 2013-2019 Patrick Michl
#
# This file is part of nemoa, https://frootlab.github.io/nemoa
#
#  nemoa is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  nemoa is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with
#  nemoa. If not, see <http://www.gnu.org/licenses/>.
#
"""Unittests for module 'nemoa.core.tty'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from unittest import skipIf
from nemoa.core import tty
from flab.base.types import Module
from flab.base import test

ttylib = tty.get_lib().__name__

#
# Test Cases
#

class TestTTY(test.ModuleTest):
    module = tty

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
