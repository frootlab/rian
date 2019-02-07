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
"""Unittests for module 'nemoa.math.stype'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from nemoa.math import stype, operator
import test

#
# Test Cases
#

class TestStype(test.ModuleTest):
    module = stype

    def test_Variable(self) -> None:
        pass # Implicitly tested by test_create_variable()

    def test_create_variable(self) -> None:
        create = stype.create_variable

        with self.subTest(args=tuple()):
            self.assertRaises(TypeError, create)

        with self.subTest(args=('x', )):
            var = create('x')
            self.assertEqual(var.name, 'x')
            self.assertIsInstance(var.operator, operator.Identity)
            self.assertEqual(var.frame, ('x', ))

        with self.subTest(args=('x**2', )):
            var = create('x**2')
            self.assertEqual(var.name, 'x**2')
            self.assertIsInstance(var.operator, operator.Lambda)
            self.assertEqual(var.frame, ('x', ))
            self.assertEqual(int(var(0)), 0)
            self.assertEqual(int(var(1)), 1)
            self.assertEqual(int(var(2)), 4)

        with self.subTest(args=(('x', list), )):
            var = create(('x', list))
            self.assertEqual(var.name, 'x')
            self.assertEqual(var.operator, list)
            self.assertEqual(var.frame, ('x', ))

        with self.subTest(args=(('y', 'x'), )):
            var = create(('y', 'x'))
            self.assertEqual(var.name, 'y')
            self.assertIsInstance(var.operator, operator.Identity)
            self.assertEqual(var.frame, ('x', ))

        with self.subTest(args=(('x', ('x1', 'x2')), )):
            var = create(('x', ('x1', 'x2')))
            self.assertEqual(var.name, 'x')
            self.assertIsInstance(var.operator, operator.Identity)
            self.assertEqual(var.frame, ('x1', 'x2'))

        with self.subTest(args=(('y', list, 'x'), )):
            var = create(('y', list, 'x'))
            self.assertEqual(var.name, 'y')
            self.assertEqual(var.operator, list)
            self.assertEqual(var.frame, ('x', ))

        with self.subTest(args=(('y', list), ('x1', 'x2'))):
            var = create(('y', list, ('x1', 'x2')))
            self.assertEqual(var.name, 'y')
            self.assertEqual(var.operator, list)
            self.assertEqual(var.frame, ('x1', 'x2'))

        with self.subTest(args=(('y', 'x**2', 'x'), )):
            var = create(('y', 'x**2', 'x'))
            self.assertEqual(var.name, 'y')
            self.assertIsInstance(var.operator, operator.Lambda)
            self.assertEqual(var.frame, ('x', ))
            self.assertEqual(int(var(0)), 0)
            self.assertEqual(int(var(1)), 1)
            self.assertEqual(int(var(2)), 4)

        with self.subTest(args=(('y', 'max(x)**2', ('max(x)', 'z')), )):
            var = create(('y', 'max(x)**2', ('max(x)', 'z')))
            self.assertEqual(var.name, 'y')
            self.assertIsInstance(var.operator, operator.Lambda)
            self.assertEqual(var.frame, ('max(x)', 'z'))
            self.assertEqual(int(var(2, 0)), 4)
            self.assertEqual(int(var(2, 1)), 4)
            self.assertEqual(int(var(3, 2)), 9)

    def test_Field(self) -> None:
        pass # Implicitly tested by test_create_domain()

    def test_create_field(self) -> None:
        create = stype.create_field

        with self.subTest():
            self.assertRaises(TypeError, create)

        with self.subTest(args=('x', )):
            field = create('x')
            self.assertIsInstance(field, stype.Field)
            self.assertEqual(field.id, 'x')
            self.assertEqual(field.type, type(None))

        with self.subTest(args=(('x', int))):
            field = create(('x', int))
            self.assertIsInstance(field, stype.Field)
            self.assertEqual(field.id, 'x')
            self.assertEqual(field.type, int)

    def test_create_basis(self) -> None:
        create = stype.create_basis

        with self.subTest():
            self.assertRaises(TypeError, create)

        with self.subTest(args=('x', )):
            frame, basis = create('x')
            self.assertEqual(frame, ('x', ))
            self.assertEqual(len(basis), 1)
            self.assertEqual(basis['x'].id, 'x')
            self.assertEqual(basis['x'].type, type(None))

        with self.subTest(args=(('x', 'y'), )):
            frame, basis = create(('x', 'y'))
            self.assertEqual(frame, ('x', 'y'))
            self.assertEqual(len(basis), 2)
            self.assertTrue('x' in basis)
            self.assertTrue('y' in basis)

    def test_Domain(self) -> None:
        pass # Implicitly tested by test_create_domain()

    def test_create_domain(self) -> None:
        create = stype.create_domain

        with self.subTest():
            dom = create()
            self.assertEqual(dom.type, type(None))
            self.assertEqual(dom.frame, tuple())

        with self.subTest(args=(object, )):
            dom = create(object)
            self.assertEqual(dom.type, object)
            self.assertEqual(dom.frame, tuple())

        with self.subTest(args=((tuple, ('a', 'b', 'c')), )):
            dom = create((tuple, ('a', 'b', 'c')))
            self.assertEqual(dom.type, tuple)
            self.assertEqual(dom.frame, ('a', 'b', 'c'))

        with self.subTest(args=(tuple, ), defaults={'fields': ('a', 'b', 'c')}):
            dom = create(tuple, defaults={'fields': ('a', 'b', 'c')})
            self.assertEqual(dom.type, tuple)
            self.assertEqual(dom.frame, ('a', 'b', 'c'))
