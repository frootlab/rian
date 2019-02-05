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
"""Unittests for module 'nemoa.io.raw'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from nemoa.base import env
from nemoa.io import raw
import test

#
# Test Cases
#

class TestRaw(test.ModuleTest):
    module = raw

    def setUp(self) -> None:
        self.filepath = env.get_temp_file(suffix='.gz')
        self.data = b'eJxrYK4tZDoiGBkGT0ZqotZJzt3/AbFpXoAgyI=='
        raw.save(self.data, self.filepath)

    def test_openx(self) -> None:
        filepath = env.get_temp_file(suffix='.gz')
        with self.subTest(file=filepath):
            with raw.openx(filepath, mode='w') as fh:
                fh.write(self.data)
            if filepath.is_file():
                with raw.openx(filepath, mode='r') as fh:
                    data = fh.read()
                filepath.unlink()
                self.assertTrue(data == self.data)
        file = filepath.open(mode='wb')
        with self.subTest(file=file):
            with raw.openx(file, mode='w') as fh:
                fh.write(self.data)
            if not file.closed:
                file.close()
                file = filepath.open(mode='rb')
                with raw.openx(file, mode='r') as fh:
                    data = fh.read()
                if not file.closed:
                    file.close()
                    self.assertTrue(data == self.data)

    def test_save(self) -> None:
        self.assertTrue(self.filepath.is_file())

    def test_load(self) -> None:
        data = raw.load(self.filepath)
        self.assertEqual(data, self.data)

    def tearDown(self) -> None:
        if self.filepath.is_file():
            self.filepath.unlink()
