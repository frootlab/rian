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
"""Unittests for module 'nemoa.base.phonetic'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from nemoa.base import phonetic
import test
from test import Case

#
# Test Cases
#

class TestPhonetic(test.ModuleTest):
    module = phonetic

    def test_soundex(self) -> None:
        self.assertCaseEqual(phonetic.soundex, [
            Case(('Smith', ), {}, 'S530'),
            Case(('Robert', ), {}, 'R163'),
            Case(('Rupert', ), {}, 'R163'),
            Case(('Rubin', ), {}, 'R150'),
            Case(('Ashcraft', ), {}, 'A261'),
            Case(('Tymczak', ), {}, 'T522'),
            Case(('Pfister', ), {}, 'P236'),
            Case(('Honeyman', ), {}, 'H555')])
