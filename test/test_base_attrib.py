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
"""Unittests for module 'nemoa.base.attrib'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from typing import Any
from nemoa.base import attrib
import test
from nemoa.types import StrList

#
# Test Cases
#

class TestAttrib(test.ModuleTest):
    module = attrib

    def test_Content(self) -> None:
        Group = type('Group', (attrib.Group, ), {'data': attrib.Content()})
        group = Group()
        group.data = 'test'
        self.assertEqual(
            group._attr_group_data['data'], 'test') # pylint: disable=W0212

    def test_MetaData(self) -> None:
        Group = type('Group', (attrib.Group, ), {'meta': attrib.MetaData()})
        group = Group()
        group.meta = 'test'
        self.assertEqual(
            group._attr_group_meta['meta'], 'test') # pylint: disable=W0212

    def test_Temporary(self) -> None:
        Group = type('Group', (attrib.Group, ), {'temp': attrib.Temporary()})
        group = Group()
        group.temp = 'test'
        self.assertEqual(
            group._attr_group_temp['temp'], 'test') # pylint: disable=W0212

    def test_Virtual(self) -> None:
        val: Any

        class Group(attrib.Group):

            def fget(self) -> str:
                return getattr(self, 'val', None)
            def fset(self, val: Any) -> None:
                self.val = val

            v1: property = attrib.Virtual(fget)
            v2: property = attrib.Virtual(fget, fset)

        group = Group()

        with self.subTest(fget=group.fget):
            self.assertEqual(group.v1, None)
            self.assertRaises(AttributeError, setattr, group, 'v1', True)

        with self.subTest(fget=group.fget, fset=group.fset):
            self.assertEqual(group.v2, None)
            group.v2 = True
            self.assertEqual(group.v2, True)
            self.assertEqual(group.val, True)

    def test_Attribute(self) -> None:

        def factory() -> str:
            return 'ok'

        class Parent(attrib.Group):
            a6: property = attrib.Attribute(default='ok')
            a7: property = attrib.Attribute(default='ok')

        class Group(attrib.Group):
            store: dict
            key: Any

            def __init__(self, parent: attrib.Group) -> None:
                super().__init__(parent=parent)
                self.store = {'a5': 'ok'}
                self.key = 'ok'

            def fget(self) -> str:
                return 'ok'

            def fset(self, val: Any) -> None:
                self.store['a9'] = val

            a0: property = attrib.Attribute(fget)
            a1: property = attrib.Attribute('fget')
            a2: property = attrib.Attribute(default='ok')
            a3: property = attrib.Attribute(factory=factory)
            a4: property = attrib.Attribute(bindkey='key')
            a5: property = attrib.Attribute(binddict='store')
            a6: property = attrib.Attribute(remote=True)
            a7: property = attrib.Attribute(inherit=True)
            a8: property = attrib.Attribute(dtype=str)
            a9: property = attrib.Attribute(fset='fset')
            aa: property = attrib.Attribute(category='test')
            ab: property = attrib.Attribute(readonly=True)

        parent = Parent()
        group = Group(parent=parent)

        with self.subTest(fget=group.fget):
            self.assertEqual(group.a0, 'ok')
            group.a0 = None
            self.assertEqual(group.a0, 'ok')
            self.assertEqual(group.__dict__['a0'], None)

        with self.subTest(fget='fget'):
            self.assertEqual(group.a1, 'ok')
            group.a1 = None
            self.assertEqual(group.a1, 'ok')
            self.assertEqual(group.__dict__['a1'], None)

        with self.subTest(default='ok'):
            self.assertEqual(group.a2, 'ok')
            group.a2 = None
            self.assertEqual(group.a2, None)

        with self.subTest(factory=factory):
            self.assertEqual(group.a3, 'ok')
            group.a3 = None
            self.assertEqual(group.a3, None)

        with self.subTest(bindkey='key'):
            self.assertEqual(group.a4, 'ok')
            group.a4 = None
            self.assertEqual(group.a4, None)
            self.assertEqual(group.key, None)

        with self.subTest(binddict='store'):
            self.assertEqual(group.a5, 'ok')
            group.a5 = None
            self.assertEqual(group.a5, None)
            self.assertEqual(group.store['a5'], None)

        with self.subTest(remote=True):
            self.assertEqual(group.a6, 'ok')
            group.a6 = None
            self.assertEqual(group.a6, None)
            self.assertEqual(parent.a6, None)

        with self.subTest(inherit=True):
            self.assertEqual(group.a7, 'ok')
            group.a7 = None
            self.assertEqual(group.a7, None)
            self.assertEqual(parent.a7, 'ok')

        with self.subTest(dtype=int):
            self.assertRaises(TypeError, setattr, group, 'a8', True)

        with self.subTest(fset='fset'):
            group.a9 = 'ok'
            self.assertEqual(group.store['a9'], 'ok')

        with self.subTest(category='test'):
            attrs = group._get_attr_names( # pylint: disable=W0212
                category='test')
            self.assertEqual(attrs, ['aa'])

        with self.subTest(category='test'):
            self.assertRaises(AttributeError, setattr, group, 'ab', True)

    def test_Group(self) -> None:

        class Leaf(attrib.Group):
            __slots__: StrList = []
            data: property = attrib.Content()
            meta: property = attrib.MetaData()

        class Branch(attrib.Group):
            __slots__: StrList = []
            leaf: attrib.Group = Leaf()
            data: property = attrib.Content()

        class Tree(attrib.Group):
            __slots__: StrList = []
            branch: attrib.Group = Branch()
            temp: property = attrib.Temporary()

        g1 = Tree()
        g2 = Tree()

        # Check correct usage of __slot__
        self.assertRaises(AttributeError, setattr, g1, 'attr', None)

        # Check Re-Creation and Instantiation of Subgroups
        g1.branch.data = 1 # type: ignore
        self.assertNotEqual(g2.branch.data, 1) # type: ignore
