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
"""Unittests for module 'nemoa.base.catalog'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from nemoa.base import catalog
import test

#
# Test Cases
#

class TestCatalog(test.ModuleTest):
    module = catalog

    def test_Category(self) -> None:
        pass # Implicitly tested in test_category

    def test_Results(self) -> None:
        @catalog.category
        class C:
            name: str

        @catalog.register(C, name='f')
        def f() -> None:
            pass

        @catalog.register(C, name='g')
        def g() -> None:
            pass

        @catalog.register(C, name='h')
        def h() -> None:
            pass

        names = sorted(catalog.search(C).get('name'))
        self.assertEqual(names, ['f', 'g', 'h'])

    def test_category(self) -> None:
        @catalog.category
        class Parent:
            name: str

        @catalog.category
        class Child(Parent):
            tags: list

        man = catalog.Manager()
        self.assertTrue(man.has_category(Parent))
        self.assertTrue(man.has_category(Child))

        meta = Child('a', tags=[]) # type: ignore
        self.assertEqual(meta.name, 'a')
        self.assertEqual(meta.tags, [])

    def test_register(self) -> None:
        @catalog.category
        class Reg:
            name: str

        @catalog.register(Reg, name='test')
        def test(x: float, y: float) -> float:
            return x ** 2 + y ** 2

        man = catalog.Manager()
        card = man.get(test)
        self.assertEqual(card.category, Reg)
        self.assertEqual(card.reference, test)
        self.assertEqual(card.data, {'name': 'test'})

    def test_search(self) -> None:

        @catalog.category
        class Func:
            name: str

        @catalog.category
        class Const(Func):
            name: str

        @catalog.register(Const, name='1')
        def a_1() -> int:
            return 1

        @catalog.register(Const, name='2')
        def a_2() -> int:
            return 2

        @catalog.register(Const, name='3')
        def b_1() -> int:
            return 3

        @catalog.register(Func, name='4')
        def b_2() -> int:
            return 4

        with self.subTest(path='*.a_*'):
            names = sorted(catalog.search(path='*.a_*').get('name'))
            self.assertEqual(names, ['1', '2'])

        with self.subTest(path='*.b_*'):
            names = catalog.search(path='*.b_*').get('name')
            self.assertEqual(names, ['3', '4'])

        with self.subTest(cat=Const):
            names = sorted(catalog.search(Const).get('name'))
            self.assertEqual(names, ['1', '2', '3'])

        with self.subTest(cat=Func):
            names = sorted(catalog.search(Func).get('name'))
            self.assertEqual(names, ['1', '2', '3', '4'])

        with self.subTest(name='1'):
            names = sorted(catalog.search(name='1').get('name'))
            self.assertEqual(names, ['1'])

    def test_pick(self) -> None:

        @catalog.category
        class P:
            name: str

        @catalog.register(P, name='p')
        def p() -> int:
            pass

        @catalog.register(P, name='q')
        def q() -> int:
            pass

        with self.subTest(path='*.p'):
            card = catalog.pick(path='*.p')
            self.assertEqual(card, p)

        with self.subTest(cat=P, name='p'):
            card = catalog.pick(P, name='p')
            self.assertEqual(card, p)

    def test_Manager(self) -> None:
        pass # Tested by methods

    def test_Manager_search(self) -> None:
        pass # Implicitely tested in test_search()

    def test_Card(self) -> None:
        pass # Implicetly tested in test_Manager

    def test_search_old(self) -> None:
        self.assertEqual(
            len(catalog.search_old(catalog, name='search_old')), 1)

    def test_custom(self) -> None:
        @catalog.custom(category='custom')
        def test_custom() -> None:
            pass
        self.assertEqual(
            getattr(test_custom, 'name', None), 'test_custom')
        self.assertEqual(
            getattr(test_custom, 'category', None), 'custom')

    def test_objective(self) -> None:
        @catalog.objective()
        def test_objective() -> None:
            pass
        self.assertEqual(
            getattr(test_objective, 'name', None), 'test_objective')
        self.assertEqual(
            getattr(test_objective, 'category', None), 'objective')

    def test_sampler(self) -> None:
        @catalog.sampler()
        def test_sampler() -> None:
            pass
        self.assertEqual(
            getattr(test_sampler, 'name', None), 'test_sampler')
        self.assertEqual(
            getattr(test_sampler, 'category', None), 'sampler')

    def test_statistic(self) -> None:
        @catalog.statistic()
        def test_statistic() -> None:
            pass
        self.assertEqual(
            getattr(test_statistic, 'name', None), 'test_statistic')
        self.assertEqual(
            getattr(test_statistic, 'category', None), 'statistic')

    def test_association(self) -> None:
        @catalog.association()
        def test_association() -> None:
            pass
        self.assertEqual(
            getattr(test_association, 'name', None), 'test_association')
        self.assertEqual(
            getattr(test_association, 'category', None), 'association')
