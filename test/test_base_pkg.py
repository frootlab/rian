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
"""Unittests for module 'nemoa.base.pkg'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from nemoa.base import pkg
from nemoa.types import Module
import test

#
# Test Cases
#

class TestPkg(test.ModuleTest):
    module = pkg

    def test_has_attr(self) -> None:
        pass # Function is testet in otree.get_module

    def test_call_attr(self) -> None:
        pass # Function is testet in otree.call_attr

    def test_get_attr(self) -> None:
        attr = pkg.get_attr('__name__')
        self.assertEqual(attr, __name__)

    def test_get_submodule(self) -> None:
        parent = pkg.get_parent()
        name = __name__.rsplit('.', 1)[-1]

        this = pkg.get_submodule(name=name, parent=parent)
        self.assertIsInstance(this, Module)

    def test_get_submodules(self) -> None:
        parent = pkg.get_parent()
        submodules = pkg.get_submodules(parent=parent)
        self.assertIn(__name__, submodules)

    def test_get_root(self) -> None:
        root = pkg.get_root()
        name = __name__.split('.', 1)[0]
        self.assertEqual(root.__name__, name)

    def test_get_parent(self) -> None:
        parent = pkg.get_parent()
        name = '.'.join(__name__.split('.')[:-1])
        self.assertEqual(parent.__name__, name)

    def test_get_module(self) -> None:
        this = pkg.get_module()
        self.assertEqual(getattr(this, '__name__', None), __name__)

    def test_crop_functions(self) -> None:
        name = pkg.crop_functions.__name__
        fullname = pkg.crop_functions.__module__ + '.' + name
        cropped = pkg.crop_functions(prefix='crop_', module=pkg)
        self.assertIn('functions', cropped)

    def test_search(self) -> None:
        count = len(pkg.search(module=pkg, name='search'))
        self.assertEqual(count, 1)
