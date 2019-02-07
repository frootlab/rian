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
"""Unittests for module 'nemoa.math.operator'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from unittest import mock
from nemoa.math import operator
import test

#
# Test Cases
#

class TestOperator(test.ModuleTest):
    module = operator

    def test_Operator(self) -> None:
        pass # Implicitely tested within subclasses

    def test_Zero(self) -> None:
        create = operator.Zero

        for target in [set, tuple, list, dict]:
            with self.subTest(target=target):
                zero = create(target)
                self.assertEqual(zero(), target())

        with self.subTest(target=object):
            self.assertRaises(ValueError, create, object)

    def test_Identity(self) -> None:
        create = operator.Identity

        with self.subTest():
            identity = create()
            self.assertIsInstance(identity, operator.Identity)
            self.assertRaises(TypeError, len, identity)
            self.assertTrue(identity)
            self.assertEqual(identity(''), '')
            self.assertEqual(identity(1, 2, 3), (1, 2, 3))

        with self.subTest(domain=(None, ('x', ))):
            identity = create(domain=(None, ('x', )))
            self.assertNotEqual(identity, operator.Identity())
            self.assertEqual(identity(1), 1)

        with self.subTest(domain=(None, ('x', 'y'))):
            identity = create(domain=(None, ('x', 'y')))
            self.assertNotEqual(identity, operator.Identity())
            self.assertEqual(identity(1, 2), (1, 2))

    def test_Getter(self) -> None:
        F = operator.Getter
        obj = mock.Mock()
        obj.configure_mock(a=1, b=2)

        with self.subTest():
            f = F()
            self.assertTrue(f is F())
            self.assertEqual(f(1), None)
            self.assertIsInstance(f, operator.Zero)
            self.assertIsInstance(f, operator.Getter)

        with self.subTest(domain=tuple):
            f = F(domain=tuple)
            self.assertTrue(f is F())
            self.assertIsInstance(f, operator.Zero)

        with self.subTest(domain=list):
            f = F(domain=list)
            self.assertIsInstance(f, operator.Zero)

        with self.subTest(domain=dict):
            f = F(domain=dict)
            self.assertIsInstance(f, operator.Zero)

        with self.subTest(domain=object):
            f = F(domain=object)
            self.assertIsInstance(f, operator.Zero)

        with self.subTest(args=('a',)):
            f = F('a')
            self.assertFalse(f is F())
            self.assertTrue(f is F('a'))
            self.assertEqual(f(1), 1)
            self.assertIsInstance(f, operator.Identity)
            self.assertIsInstance(f, operator.Getter)

        with self.subTest(args=('a', 'b')):
            f = F('a', 'b')
            self.assertIsInstance(f, operator.Identity)
            self.assertEqual(f(1, 2), (1, 2))

        with self.subTest(args=('a', ), domain=(None, ('a', 'b'))):
            f = F('a', domain=(None, ('a', 'b')))
            self.assertEqual(f(1, 2), 1)
            self.assertRaises(IndexError, f)

        with self.subTest(args=('a', 'b'), domain=tuple):
            f = F('a', 'b', domain=tuple)
            self.assertEqual(f((1, 2)), (1, 2))

        with self.subTest(args=('a', 'b'), domain=(tuple, ('a', 'b', 'c'))):
            f = F('a', 'b', domain=(tuple, ('a', 'b', 'c')))
            self.assertEqual(f((1, 2, 3)), (1, 2))

        with self.subTest(args=('a', 'b'), domain=list):
            f = F('a', 'b', domain=list)
            self.assertEqual(f([1, 2]), (1, 2))

        with self.subTest(args=('a', 'b'), domain=(list, ('a', 'b', 'c'))):
            f = F('a', 'b', domain=(list, ('a', 'b', 'c')))
            self.assertEqual(f([1, 2, 3]), (1, 2))

        with self.subTest(args=('a', 'b'), domain=dict):
            f = F('a', 'b', domain=dict)
            self.assertEqual(f({'a':1, 'b':2}), (1, 2))

        with self.subTest(args=('a', 'b'), domain=object):
            f = F('a', 'b', domain=object)
            self.assertEqual(f(obj), (1, 2))

        with self.subTest(args=('x', ), domain=dict):
            f = F('x', domain=dict)
            self.assertEqual(f({'x': 1, 'y': 2, 'z': 3}), 1)

        with self.subTest(args=('x', ), domain=(tuple, ('x', 'y', 'z'))):
            f = F('x', domain=(tuple, ('x', 'y', 'z')))
            self.assertEqual(f((1, 2, 3)), 1)

        with self.subTest(args=('x', ), domain=(None, ('x', 'y', 'z'))):
            f = F('x', domain=(None, ('x', 'y', 'z')))
            self.assertEqual(f(1, 2, 3), 1)

        with self.subTest(args=('x', 'z'), domain=(None, ('x', 'y', 'z'))):
            f = F('x', 'z', domain=(None, ('x', 'y', 'z')))
            self.assertEqual(f(1, 2, 3), (1, 3))

        with self.subTest(args=('a',)):
            f = F('a')
            self.assertIsInstance(f, operator.Identity)
            self.assertRaises(TypeError, f)
            self.assertEqual(f(1), 1)

        with self.subTest(args=('a', 'b')):
            f = F('a', 'b')
            self.assertIsInstance(f, operator.Identity)
            self.assertRaises(TypeError, f, 1)
            self.assertEqual(f(1, 2), (1, 2))

        with self.subTest(args=('a', 'b', 'c')):
            f = F('a', 'b', 'c')
            self.assertIsInstance(f, operator.Identity)
            self.assertRaises(TypeError, f, 1, 2)
            self.assertEqual(f(1, 2, 3), (1, 2, 3))

        with self.subTest(args=('a', 'b'), target=dict):
            f = F('a', 'b', target=dict)
            self.assertEqual(f(1, 2), {'a': 1, 'b': 2})

    def test_Lambda(self) -> None:
        create = operator.Lambda

        with self.subTest(args=tuple()):
            op = create()
            self.assertIsInstance(op, operator.Lambda)
            self.assertIsInstance(op, operator.Zero)

        with self.subTest(args=('x', )):
            op = create('x')
            self.assertIsInstance(op, operator.Lambda)
            self.assertIsInstance(op, operator.Identity)

        with self.subTest(args=('x**2 + y', )):
            op = create('x**2 + y')
            self.assertIsInstance(op, operator.Lambda)
            self.assertRaises(TypeError, op, 1)
            self.assertEqual(int(op(2, -4)), 0)

        with self.subTest(args=('{x}', )):
            self.assertRaises(Exception, create, '{x}')

        with self.subTest(args=('{x}', ), variables=('{x}', )):
            op = create('{x}', variables=('{x}', ))
            self.assertIsInstance(op, operator.Lambda)
            self.assertEqual(int(op(1)), 1)

        with self.subTest(args=('{x}**2 + y', ), variables=('{x}', )):
            self.assertRaises(
                ValueError, create, '{x}**2 + y', variables=('{x}', ))

        with self.subTest(args=('{x}**2 + y', ), variables=('{x}', 'y')):
            op = create('{x}**2 + y', variables=('{x}', 'y'))
            self.assertIsInstance(op, operator.Lambda)
            self.assertRaises(TypeError, op, 1)
            self.assertEqual(int(op(2, -4)), 0)

        with self.subTest(
                args=('{x}**2 + y', ), variables=('{x}', 'y'),
                domain=(None, ('{x}', '{y}'))):
            self.assertRaises(
                ValueError, create, '{x}**2 + y', variables=('{x}', ),
                domain=(None, ('{x}', '{y}')))

        with self.subTest(
                args=('{x}**2 + y', ), variables=('{x}', 'y'),
                domain=(None, ('y', '{x}'))):
            op = create('{x}**2 + y', variables=('{x}', 'y'),
                domain=(None, ('y', '{x}')))
            self.assertIsInstance(op, operator.Lambda)
            self.assertRaises(IndexError, op, 1)
            self.assertEqual(int(op(-4, 2)), 0)

        with self.subTest(args=('{x}**2', ), variables=('{x}', 'y')):
            op = create('{x}**2', variables=('{x}', 'y'))
            self.assertIsInstance(op, operator.Lambda)
            self.assertEqual(int(op(2)), 4)
            self.assertEqual(int(op(2, 2)), 4)

    def test_Vector(self) -> None:
        Op = operator.Vector
        obj = mock.Mock()
        obj.configure_mock(a=1, b=2)
        dic = {'a': 1, 'b': 2}
        seq = [1, 2]

        with self.subTest(args=('a', 'b'), domain=None, target=dict):
            f = Op('a', 'b', domain=None, target=dict)
            self.assertEqual(f(1, 2), {'a': 1, 'b': 2})

        with self.subTest(
                args=('a', 'b'), domain=None, target=(dict, ('_', 1))):
            f = Op('a', 'b', domain=None, target=(dict, ('_', 1)))
            self.assertEqual(f(1, 2), {'_': 1, 1: 2})

        with self.subTest(args=('a', 'b'), domain=object, target=tuple):
            f = Op('a', 'b', domain=object, target=tuple)
            self.assertEqual(f(obj), (1, 2))

        with self.subTest(args=('a', 'b'), domain=object, target=list):
            f = Op('a', 'b', domain=object, target=list)
            self.assertEqual(f(obj), [1, 2])

        with self.subTest(args=('a', 'b'), domain=object, target=dict):
            f = Op('a', 'b', domain=object, target=dict)
            self.assertEqual(f(obj), {'a': 1, 'b': 2})

        with self.subTest(
                args=('a', 'b'), domain=object, target=(dict, ('_', 1))):
            f = Op('a', 'b', domain=object, target=(dict, ('_', 1)))
            self.assertEqual(f(obj), {'_': 1, 1: 2})

        with self.subTest(args=('a', 'b'), domain=dict, target=dict):
            f = Op('a', 'b', domain=dict, target=dict)
            self.assertEqual(f(dic), {'a': 1, 'b': 2})

        with self.subTest(args=('a', 'b'), domain=dict, target=tuple):
            f = Op('a', 'b', domain=dict, target=tuple)
            self.assertEqual(f(dic), (1, 2))

        with self.subTest(args=('a', 'b'), domain=dict, target=list):
            f = Op('a', 'b', domain=dict, target=list)
            self.assertEqual(f(dic), [1, 2])

        with self.subTest(args=('a', 'b'), domain=list, target=dict):
            f = Op('a', 'b', domain=(list, ('a', 'b')), target=dict)
            self.assertEqual(f(seq), {'a': 1, 'b': 2})

        with self.subTest(args=('a', 'b'), domain=list, target=tuple):
            f = Op('a', 'b', domain=(list, ('a', 'b')), target=tuple)
            self.assertEqual(f(seq), (1, 2))

        with self.subTest(args=('a', 'b'), domain=list, target=list):
            f = Op('a', 'b', domain=(list, ('a', 'b')), target=list)
            self.assertEqual(f(seq), [1, 2])

        with self.subTest(args=('a', ('b', ), ('c', len), ('Y', max, 'd'))):
            f = Op('a', ('b', ), ('c', len), ('Y', max, 'd'))
            self.assertEqual(f.fields, ('a', 'b', 'c', 'd'))
            self.assertTrue(all(map(callable, f)))
            self.assertEqual(f.components, ('a', 'b', 'c', 'Y'))

    def test_create_setter(self) -> None:
        items = [('name', 'monty'), ('id', 42)]

        with self.subTest(domain=object):
            obj = mock.Mock()
            operator.create_setter(*items, domain=object)(obj)
            self.assertEqual((obj.name, obj.id), ('monty', 42))

        with self.subTest(domain=dict):
            dic: dict = dict()
            operator.create_setter(*items, domain=dict)(dic)
            self.assertEqual((dic['name'], dic['id']), ('monty', 42))

        with self.subTest(domain=list):
            seq: list = [None] * 2
            operator.create_setter((0, 'monty'), (1, 42), domain=list)(seq)
            self.assertEqual((seq[0], seq[1]), ('monty', 42))

    def test_create_wrapper(self) -> None:
        setter = operator.create_wrapper(name='test', group=1)
        op = operator.Zero()
        self.assertEqual(getattr(setter(op), 'name'), 'test')
        self.assertEqual(getattr(setter(op), 'group'), 1)

    def test_create_sorter(self) -> None:
        seq = list(mock.Mock() for i in range(10))
        for i, obj in enumerate(seq):
            obj.configure_mock(x=i, y=-i)
        getx = operator.Vector('x', domain=object)
        sorter = operator.create_sorter('x', domain=object)
        self.assertEqual(list(map(getx, sorter(seq))), list(range(10)))
        sorter = operator.create_sorter('y', domain=object, reverse=True)
        self.assertEqual(list(map(getx, sorter(seq))), list(range(10)))

    def test_create_aggregator(self) -> None:
        seq = list(mock.Mock() for i in range(10))
        for i, obj in enumerate(seq):
            obj.configure_mock(id=i, bool=bool(i > 5))
        groups = operator.create_grouper('bool', domain=object)

        with self.subTest():
            aggregate = operator.create_aggregator()
            self.assertFalse(bool(aggregate))

        args = ('bool', ('count', len, 'bool'), ('max(id)', max, 'id'))
        with self.subTest(args=args, domain=object, target=tuple):
            aggregate = operator.create_aggregator(
                *args, domain=object, target=tuple)
            self.assertEqual(
                list(aggregate(g) for g in groups(seq)),
                [(False, 6, 5), (True, 4, 9)])

        with self.subTest(args=args, domain=object, target=dict):
            aggregate = operator.create_aggregator(
                *args, domain=object, target=dict)
            self.assertEqual(
                list(aggregate(g) for g in groups(seq)), [
                {'bool': False, 'count': 6, 'max(id)': 5},
                {'bool': True, 'count': 4, 'max(id)': 9}])

    def test_create_group_aggregator(self) -> None:
        with self.subTest(domain=object):
            objseq = list(mock.Mock() for i in range(15))
            for i, obj in enumerate(objseq):
                obj.configure_mock(id=i, bool=bool(i > 5))
            args = ('bool', ('count', len, 'bool'), ('max(id)', max, 'id'))
            with self.subTest(args=args, key='bool', target=tuple):
                op = operator.create_group_aggregator(
                    *args, key='bool', domain=object, target=tuple)
                self.assertEqual(
                    list(op(objseq)), [(False, 6, 5), (True, 9, 14)])
            with self.subTest(args=args, key='bool', target=dict):
                op = operator.create_group_aggregator(
                    *args, key='bool', domain=object, target=dict)
                self.assertEqual(
                    list(op(objseq)), [
                    {'bool': False, 'count': 6, 'max(id)': 5},
                    {'bool': True, 'count': 9, 'max(id)': 14}])

    def test_create_grouper(self) -> None:
        seq = list(mock.Mock() for i in range(10))
        for i, obj in enumerate(seq):
            obj.configure_mock(id=i, name=f'{i>5}')

        with self.subTest(domain=object):
            grouper = operator.create_grouper(domain=object)
            self.assertEqual(len(grouper(seq)), 1)
            self.assertEqual(len(grouper(seq)[0]), 10)

        with self.subTest(args=('name', ), domain=object):
            grouper = operator.create_grouper('name', domain=object)
            self.assertEqual(len(grouper(seq)), 2)
            self.assertEqual(len(grouper(seq)[0]), 6)

        with self.subTest(args=('name', ), domain=object, presorted=True):
            grouper = operator.create_grouper(
                'name', domain=object, presorted=True)
            self.assertEqual(len(grouper(seq)), 2)
            self.assertEqual(len(grouper(seq)[0]), 6)

        with self.subTest(args=('id', )):
            grouper = operator.create_grouper('id', domain=object)
            self.assertEqual(len(grouper(seq)), 10)
            self.assertEqual(len(grouper(seq)[0]), 1)

        with self.subTest(args=('name', 'id')):
            grouper = operator.create_grouper('name', 'id', domain=object)
            self.assertEqual(len(grouper(seq)), 10)
            self.assertEqual(len(grouper(seq)[0]), 1)

    def test_compose(self) -> None:
        with self.subTest(args=tuple()):
            op = operator.compose()
            self.assertEqual(op, operator.Identity())

        with self.subTest(args=(None, None)):
            op = operator.compose(None, None)
            self.assertEqual(op, operator.Identity())

        with self.subTest(args=(None, lambda x: x)):
            op = operator.compose(None, lambda x: x)
            self.assertEqual(op(1), 1)

        with self.subTest(args=(lambda x: x + 1, lambda x: x - 1)):
            op = operator.compose(lambda x: x + 1, lambda x: x - 1)
            self.assertEqual(op(1), 1)
