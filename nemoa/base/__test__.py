# -*- coding: utf-8 -*-
"""Unittests for package 'nemoa.base'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from collections import OrderedDict
import datetime
from unittest import mock
from pathlib import Path
import typing
import numpy as np
from nemoa import errors
from nemoa.base import abc, array, attrib, binary, check, env, literal, mapping
from nemoa.base import operator, otree, pkg, stack, stype
from nemoa.base import nbase
from nemoa.test import ModuleTestCase, Case
from nemoa.types import Module, PathLikeList, StrList
from nemoa.types import NaN, Method, Function

#
# Test Cases
#

class TestAbc(ModuleTestCase):
    module = abc

    def test_SingletonMeta(self) -> None:
        pass # Implicitely tested by test_Singleton()

    def test_Singleton(self) -> None:
        T = type('Singleton', (abc.Singleton, ), {})

        self.assertTrue(T() is T())
        self.assertTrue(T(1) is T(2))

    def test_IsolatedMeta(self) -> None:
        pass # Implicitely tested by test_Isolated()

    def test_Isolated(self) -> None:
        T = type('Isolated', (abc.Isolated, ), {})

        self.assertFalse(type(T()) is type(T()))

    def test_sentinel(self) -> None:

        @abc.sentinel
        class Sentinel(abc.Singleton):
            def __init__(self) -> None:
                self.test = True

        self.assertEqual(Sentinel.__name__, type(Sentinel).__name__)
        self.assertTrue(hasattr(Sentinel, 'test'))
        self.assertTrue(Sentinel.test)

    def test_MultitonMeta(self) -> None:
        pass # Implicitely tested by test_Multiton()

    def test_Multiton(self) -> None:
        f = type('Multiton', (abc.Multiton, ), {})

        self.assertTrue(f() is f())
        self.assertTrue(f(1) is f(1))
        self.assertFalse(f(1) is f(2))

class TestArray(ModuleTestCase):
    module = array

    def setUp(self) -> None:
        self.x = np.array([[NaN, 1.], [NaN, NaN]])
        self.d = {('a', 'b'): 1.}
        self.tuples = [
            ('this', 1, 1., 1j), ('is', 2, 2., 2j),
            ('awesome', 3, 3., 3j)]
        self.labels = (['a', 'b'], ['a', 'b'])

    def test_from_dict(self) -> None:
        x = array.from_dict(self.d, labels=self.labels)
        self.assertTrue(np.allclose(x, self.x, equal_nan=True))

    def test_as_dict(self) -> None:
        d = array.as_dict(self.x, labels=self.labels)
        self.assertEqual(d, self.d)

    def test_from_tuples(self) -> None:
        x = array.from_tuples(self.tuples) # type: ignore
        self.assertEqual(x.tolist(), self.tuples)

    def test_as_tuples(self) -> None:
        dtype = [('', str, 7), ('', int), ('', float), ('', complex)]
        x = np.array(self.tuples, dtype=dtype)
        self.assertEqual(array.as_tuples(x), self.tuples)

    def test_add_cols(self) -> None:
        src = np.array([('a'), ('b')], dtype=[('z', 'U4')])
        tgt = np.array([(1., 2), (3., 4)], dtype=[('x', float), ('y', int)])
        new = array.add_cols(tgt, src, 'z')
        self.assertEqual(new['z'][0], 'a')

class TestAttrib(ModuleTestCase):
    module = attrib

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


class TestStype(ModuleTestCase):
    module = stype

    def test_Field(self) -> None:
        pass # Implicitely tested by test_create_domain()

    def test_create_field(self) -> None:
        f = stype.create_field

        with self.subTest():
            self.assertRaises(TypeError, f)

        with self.subTest(args=('x', )):
            field = f('x')
            self.assertIsInstance(field, stype.Field)
            self.assertEqual(field.id, 'x')
            self.assertEqual(field.type, type(None))

        with self.subTest(args=(('x', int))):
            field = f(('x', int))
            self.assertIsInstance(field, stype.Field)
            self.assertEqual(field.id, 'x')
            self.assertEqual(field.type, int)

    def test_create_basis(self) -> None:
        f = stype.create_basis

        with self.subTest():
            self.assertRaises(TypeError, f)

        with self.subTest(args=('x', )):
            frame, basis = f('x')
            self.assertEqual(frame, ('x', ))
            self.assertEqual(len(basis), 1)
            self.assertEqual(basis['x'].id, 'x')
            self.assertEqual(basis['x'].type, type(None))

        with self.subTest(args=(('x', 'y'), )):
            frame, basis = f(('x', 'y'))
            self.assertEqual(frame, ('x', 'y'))
            self.assertEqual(len(basis), 2)
            self.assertTrue('x' in basis)
            self.assertTrue('y' in basis)

    def test_Domain(self) -> None:
        pass # Implicitely tested by test_create_domain()

    def test_create_domain(self) -> None:
        f = stype.create_domain

        with self.subTest():
            dom = f()
            self.assertEqual(dom.type, type(None))
            self.assertEqual(dom.frame, tuple())

        with self.subTest(args=(object, )):
            dom = f(object)
            self.assertEqual(dom.type, object)
            self.assertEqual(dom.frame, tuple())

        with self.subTest(args=((tuple, ('a', 'b', 'c')), )):
            dom = f((tuple, ('a', 'b', 'c')))
            self.assertEqual(dom.type, tuple)
            self.assertEqual(dom.frame, ('a', 'b', 'c'))

        with self.subTest(args=(tuple, ), defaults={'fields': ('a', 'b', 'c')}):
            dom = f(tuple, defaults={'fields': ('a', 'b', 'c')})
            self.assertEqual(dom.type, tuple)
            self.assertEqual(dom.frame, ('a', 'b', 'c'))

class TestOperator(ModuleTestCase):
    module = operator

    def test_Variable(self) -> None:
        pass # Implicitely tested by test_create_variable()

    def test_create_variable(self) -> None:
        f = operator.create_variable

        with self.subTest(args=tuple()):
            self.assertRaises(TypeError, f)

        with self.subTest(args=('x', )):
            var = f('x')
            self.assertEqual(var.name, 'x')
            self.assertIsInstance(var.operator, operator.Identity)
            self.assertEqual(var.frame, ('x', ))

        with self.subTest(args=(('x', list), )):
            var = f(('x', list))
            self.assertEqual(var.name, 'x')
            self.assertEqual(var.operator, list)
            self.assertEqual(var.frame, ('x', ))

        with self.subTest(args=(('y', 'x'), )):
            var = f(('y', 'x'))
            self.assertEqual(var.name, 'y')
            self.assertIsInstance(var.operator, operator.Identity)
            self.assertEqual(var.frame, ('x', ))

        with self.subTest(args=(('x', ('x1', 'x2')), )):
            var = f(('x', ('x1', 'x2')))
            self.assertEqual(var.name, 'x')
            self.assertIsInstance(var.operator, operator.Identity)
            self.assertEqual(var.frame, ('x1', 'x2'))

        with self.subTest(args=(('y', list, 'x'), )):
            var = f(('y', list, 'x'))
            self.assertEqual(var.name, 'y')
            self.assertEqual(var.operator, list)
            self.assertEqual(var.frame, ('x', ))

        with self.subTest(args=(('y', list), ('x1', 'x2'))):
            var = f(('y', list, ('x1', 'x2')))
            self.assertEqual(var.name, 'y')
            self.assertEqual(var.operator, list)
            self.assertEqual(var.frame, ('x1', 'x2'))

    def test_Composite(self) -> None:
        Op = operator.Composite
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

    def test_Zero(self) -> None:
        f = operator.Zero

        for target in [set, tuple, list, dict]:
            with self.subTest(target=target):
                zero = f(target)
                self.assertEqual(zero(), target())

        with self.subTest(target=object):
            self.assertRaises(ValueError, f, object)

    def test_Lambda(self) -> None:
        f = operator.Lambda

        with self.subTest(args=tuple()):
            op = f()
            self.assertIsInstance(op, operator.Lambda)
            self.assertIsInstance(op._built, operator.Zero)

        with self.subTest(args=('x^2 + y', )):
            op = f('x^2 + y')
            self.assertIsInstance(op, operator.Lambda)
            self.assertRaises(TypeError, op, 1)
            self.assertEqual(int(op(2, -4)), 0)

        with self.subTest(args=('{x}', )):
            self.assertRaises(Exception, f, '{x}')

        with self.subTest(args=('{x}', ), variables=('{x}', )):
            op = f('{x}', variables=('{x}', ))
            self.assertIsInstance(op, operator.Lambda)
            self.assertEqual(int(op(1)), 1)

        with self.subTest(args=('{x}^2 + y', ), variables=('{x}', )):
            self.assertRaises(
                errors.NoSubsetError, f, '{x}^2 + y', variables=('{x}', ))

        with self.subTest(args=('{x}^2 + y', ), variables=('{x}', 'y')):
            op = f('{x}^2 + y', variables=('{x}', 'y'))
            self.assertIsInstance(op, operator.Lambda)
            self.assertRaises(TypeError, op, 1)
            self.assertEqual(int(op(2, -4)), 0)

        with self.subTest(
                args=('{x}^2 + y', ), variables=('{x}', 'y'),
                domain=(None, ('{x}', '{y}'))):
            self.assertRaises(
                errors.NoSubsetError, f, '{x}^2 + y', variables=('{x}', ),
                domain=(None, ('{x}', '{y}')))

        with self.subTest(
                args=('{x}^2 + y', ), variables=('{x}', 'y'),
                domain=(None, ('y', '{x}'))):
            op = f('{x}^2 + y', variables=('{x}', 'y'),
                domain=(None, ('y', '{x}')))
            self.assertIsInstance(op, operator.Lambda)
            self.assertRaises(IndexError, op, 1)
            self.assertEqual(int(op(-4, 2)), 0)

        with self.subTest(args=('{x}^2', ), variables=('{x}', 'y')):
            op = f('{x}^2', variables=('{x}', 'y'))
            self.assertIsInstance(op, operator.Lambda)
            self.assertEqual(int(op(2)), 4)
            self.assertEqual(int(op(2, 2)), 4)

    def test_Identity(self) -> None:
        f = operator.Identity

        with self.subTest():
            identity = f()
            self.assertIsInstance(identity, operator.Identity)
            self.assertEqual(len(identity), 0)
            self.assertFalse(identity)
            self.assertEqual(identity(''), '')
            self.assertEqual(identity(1, 2, 3), (1, 2, 3))

        with self.subTest(domain=(None, ('x', ))):
            identity = f(domain=(None, ('x', )))
            self.assertNotEqual(identity, operator.Identity())
            self.assertEqual(identity(1), 1)

        with self.subTest(domain=(None, ('x', 'y'))):
            identity = f(domain=(None, ('x', 'y')))
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
            self.assertIsInstance(f, operator.Identity)
            self.assertEqual(f(1), 1)

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

    def test_create_setter(self) -> typing.Any:
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
        getx = operator.Composite('x', domain=object)
        sorter = operator.create_sorter('x', domain=object)
        self.assertEqual(list(map(getx, sorter(seq))), list(range(10)))
        sorter = operator.create_sorter('y', domain=object, reverse=True)
        self.assertEqual(list(map(getx, sorter(seq))), list(range(10)))

    def test_create_aggregator(self) -> None:
        seq = list(mock.Mock() for i in range(10))
        for i, obj in enumerate(seq):
            obj.configure_mock(id=i, bool=bool(i>5))
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
                obj.configure_mock(id=i, bool=bool(i>5))
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

    def test_evaluate(self) -> None:
        func = operator.get_parameters
        self.assertAllEqual(operator.evaluate, [
            Case(args=(func, list), value=OrderedDict()),
            Case(args=(func, list), kwds={'test': True}, value=OrderedDict())])

    def test_get_parameters(self) -> None:
        func = operator.get_parameters
        self.assertAllEqual(func, [
            Case(args=(func, ), value=OrderedDict()),
            Case(args=(func, list), value=OrderedDict([('op', list)])),
            Case(args=(func, list), kwds={'test': True},
                value=OrderedDict([('op', list), ('test', True)]))])

    def test_parse_call(self) -> None:
        self.assertEqual(
            operator.parse_call("f(1., 'a', b = 2)"),
            ('f', (1.0, 'a'), {'b': 2}))

class TestOtree(ModuleTestCase):
    module = otree

    def test_has_base(self) -> None:
        self.assertAllEqual(otree.has_base, [
            Case(args=(object, object), value=True),
            Case(args=(object, 'object'), value=True),
            Case(args=('object', object), value=True),
            Case(args=('object', str), value=True),
            Case(args=(object, 'str'), value=False),
            Case(args=(object, type), value=False),
            Case(args=('object', type), value=False)])

    def test_get_members(self) -> None:
        self.assertAllComprise(otree.get_members, [
            Case(args=(object, ), value='__class__'),
            Case(args=(otree, ), value='get_members'),
            Case(args=(otree, ), kwds={'classinfo': Function},
                value='get_members'),
            Case(args=(otree, ), kwds={'name': 'get_members'},
                value='get_members'),
            Case(args=(otree, ), kwds={
                'rules': {'about': lambda arg, attr: arg in attr},
                'about': 'members'}, value='get_members')])

        self.assertNoneComprise(otree.get_members, [
            Case(args=(object, '*dummy*'), value='__class__'),
            Case(args=(otree, ), kwds={'classinfo': str},
                value='get_members'),
            Case(args=(otree, '*dummy*'), value='get_members'),
            Case(args=(otree, ), kwds={'name': 'dummy'},
                value='get_members'),
            Case(args=(otree, ), kwds={
                'rules': {'about': lambda arg, attr: arg == attr},
                'about': 'members'}, value='get_members')])

    def test_get_members_dict(self) -> None:
        self.assertAllComprise(otree.get_members_dict, [
            Case(args=(object, ), value='object.__class__'),
            Case(args=(otree, ), value='nemoa.base.otree.get_members'),
            Case(args=(otree, ), kwds={'classinfo': Function},
                value='nemoa.base.otree.get_members'),
            Case(args=(otree, ), kwds={'name': 'get_members'},
                value='nemoa.base.otree.get_members'),
            Case(args=(otree, ), kwds={
                'rules': {'about': lambda arg, attr: arg in attr},
                'about': 'members'}, value='nemoa.base.otree.get_members')])

        self.assertNoneComprise(otree.get_members_dict, [
            Case(args=(object, '*dummy*'), value='object.__class__'),
            Case(args=(otree, ), kwds={'classinfo': str},
                value='nemoa.base.otree.get_members'),
            Case(args=(otree, '*dummy*'),
                value='nemoa.base.otree.get_members'),
            Case(args=(otree, ), kwds={'name': 'dummy'},
                value='nemoa.base.otree.get_members'),
            Case(args=(otree, ), kwds={
                'rules': {'about': lambda arg, attr: arg == attr},
                'about': 'members'}, value='nemoa.base.otree.get_members')])

    def test_get_name(self) -> None:
        self.assertAllEqual(otree.get_name, [
            Case(args=('', ), value='str'),
            Case(args=(0, ), value='int'),
            Case(args=(object, ), value='object'),
            Case(args=(object(), ), value='object'),
            Case(args=(otree.get_name, ), value='get_name'),
            Case(args=(otree, ), value='nemoa.base.otree')])

    def test_get_lang_repr(self) -> None:
        self.assertAllEqual(otree.get_lang_repr, [
            Case(args=(set(), ), value='no elements'),
            Case(args=([], ), value='no items'),
            Case(args=(['a'], ), value="item 'a'"),
            Case(args=([1, 2], ), value="items '1' and '2'"),
            Case(args=(['a', 'b'], 'or'), value="items 'a' or 'b'")])

    def test_get_summary(self) -> None:
        self.assertAllEqual(otree.get_summary, [
            Case(args=(object, ), value=otree.get_summary(object())),
            Case(args=('summary.\n', ), value='summary')])

    def test_call_attr(self) -> None:
        self.assertAllEqual(otree.call_attr, [
            Case(args=(otree, 'get_name', list), value='list'),
            Case(args=(otree, 'get_name', list), kwds={'test': True},
                value='list')])

    def test_get_methods(self) -> None:
        obj = mock.Mock()
        obj.geta.configure_mock(__class__=Method, name='a', group=1)
        obj.getb.configure_mock(__class__=Method, name='b', group=2)
        obj.setb.configure_mock(__class__=Method, name='b', group=2)
        names = otree.get_methods(obj, pattern='get*').keys()
        self.assertEqual(names, {'geta', 'getb'})
        names = otree.get_methods(obj, pattern='*b').keys()
        self.assertEqual(names, {'getb', 'setb'})

class TestCheck(ModuleTestCase):
    module = check

    def test_has_type(self) -> None:
        self.assertNoneRaises(TypeError, check.has_type, [
            Case(args=('', 0, int)),
            Case(args=('', '', str)),
            Case(args=('', list(), list)),
            Case(args=('', dict(), dict)),
            Case(args=('', object, typing.Callable)),
            Case(args=('', object, typing.Any))])

        self.assertAllRaises(TypeError, check.has_type, [
            Case(args=('', '', int)),
            Case(args=('', 1., int)),
            Case(args=('', 1, float)),
            Case(args=('', dict(), list)),
            Case(args=('', None, typing.Callable))])

    def test_is_identifier(self) -> None:
        self.assertNoneRaises(ValueError, check.is_identifier, [
            Case(args=('', 'id')),
            Case(args=('', 'ID')),
            Case(args=('', 'Table')),
            Case(args=('', 'Table1'))])

        self.assertAllRaises(ValueError, check.is_identifier, [
            Case(args=('', '')),
            Case(args=('', '1')),
            Case(args=('', 'a b')),
            Case(args=('', 'a.b'))])

    def test_has_opt_type(self) -> None:
        self.assertNoneRaises(TypeError, check.has_opt_type, [
            Case(args=('', None, int)),
            Case(args=('', None, str)),
            Case(args=('', list(), list)),
            Case(args=('', dict(), dict))])

        self.assertAllRaises(TypeError, check.has_opt_type, [
            Case(args=('', '', int)),
            Case(args=('', 1., int)),
            Case(args=('', 1, float)),
            Case(args=('', dict(), list))])

    def test_is_callable(self) -> None:
        self.assertNoneRaises(TypeError, check.is_callable, [
            Case(args=('', int)),
            Case(args=('', dict)),
            Case(args=('', list)),
            Case(args=('', str))])

        self.assertAllRaises(TypeError, check.has_type, [
            Case(args=('', None)),
            Case(args=('', 0)),
            Case(args=('', '')),
            Case(args=('', set()))])

    def test_is_typehint(self) -> None:
        self.assertNoneRaises(TypeError, check.is_typehint, [
            Case(args=('', str)),
            Case(args=('', (int, float))),
            Case(args=('', typing.Any)),
            Case(args=('', typing.Callable))])

        self.assertAllRaises(TypeError, check.is_typehint, [
            Case(args=('', None)),
            Case(args=('', 0)),
            Case(args=('', '')),
            Case(args=('', typing.Union))])

    def test_is_class(self) -> None:
        self.assertNoneRaises(TypeError, check.is_class, [
            Case(args=('', int)),
            Case(args=('', dict)),
            Case(args=('', list)),
            Case(args=('', str))])

        self.assertAllRaises(TypeError, check.is_class, [
            Case(args=('', None)),
            Case(args=('', 0)),
            Case(args=('', '')),
            Case(args=('', set()))])

    def test_is_subclass(self) -> None:
        self.assertNoneRaises(TypeError, check.is_subclass, [
            Case(args=('', int, object)),
            Case(args=('', dict, dict)),
            Case(args=('', list, object)),
            Case(args=('', str, str))])

        self.assertAllRaises(TypeError, check.is_subclass, [
            Case(args=('', int, str)),
            Case(args=('', dict, list)),
            Case(args=('', object, float)),
            Case(args=('', str, complex))])

    def test_is_subset(self) -> None:
        self.assertNoneRaises(ValueError, check.is_subset, [
            Case(args=('', set(), '', set())),
            Case(args=('', {1}, '', {1, 2})),
            Case(args=('', {2}, '', {1, 2})),
            Case(args=('', {2, 1}, '', {1, 2}))])

        self.assertAllRaises(ValueError, check.is_subset, [
            Case(args=('', {1}, '', set())),
            Case(args=('', {2}, '', {1})),
            Case(args=('', {1, 2}, '', {1})),
            Case(args=('', {1, 2, 3}, '', set()))])

    def test_no_dublicates(self) -> None:
        self.assertNoneRaises(ValueError, check.no_dublicates, [
            Case(args=('', set())),
            Case(args=('', {1, 1, 2, 3})),
            Case(args=('', [1, 2, 3])),
            Case(args=('', {1: 1, 2: 2}))])

        self.assertAllRaises(ValueError, check.no_dublicates, [
            Case(args=('', (1, 1))),
            Case(args=('', [1, 2, 2]))])

    def test_is_positive(self) -> None:
        self.assertNoneRaises(ValueError, check.is_positive, [
            Case(args=('', 1)),
            Case(args=('', 1.))])

        self.assertAllRaises(ValueError, check.is_positive, [
            Case(args=('', 0)),
            Case(args=('', -1)),
            Case(args=('', -1.))])

    def test_is_negative(self) -> None:
        self.assertNoneRaises(ValueError, check.is_negative, [
            Case(args=('', -1)),
            Case(args=('', -1.))])

        self.assertAllRaises(ValueError, check.is_negative, [
            Case(args=('', 0)),
            Case(args=('', 1)),
            Case(args=('', 1.))])

    def test_is_not_positive(self) -> None:
        self.assertNoneRaises(ValueError, check.is_not_positive, [
            Case(args=('', 0)),
            Case(args=('', -1)),
            Case(args=('', -1.))])

        self.assertAllRaises(ValueError, check.is_not_positive, [
            Case(args=('', 1)),
            Case(args=('', 1.))])

    def test_is_not_negative(self) -> None:
        self.assertNoneRaises(ValueError, check.is_not_negative, [
            Case(args=('', 0)),
            Case(args=('', 1)),
            Case(args=('', 1.))])

        self.assertAllRaises(ValueError, check.is_not_negative, [
            Case(args=('', -1)),
            Case(args=('', -1.))])

    def test_has_attr(self) -> None:
        self.assertNoneRaises(AttributeError, check.has_attr, [
            Case(args=('', 'format')),
            Case(args=(0, 'real')),
            Case(args=(1j, 'imag'))])

        self.assertAllRaises(AttributeError, check.has_attr, [
            Case(args=(list(), 'keys')),
            Case(args=(0, ''))])

    def test_has_size(self) -> None:
        self.assertNoneRaises(ValueError, check.has_size, [
            Case(args=('', set()), kwds={'size': 0}),
            Case(args=('', set()), kwds={'min_size': 0}),
            Case(args=('', tuple([1])), kwds={'max_size': 1}),
            Case(args=('', [1, 2]), kwds={'min_size': 1, 'max_size': 3})])

        self.assertAllRaises(ValueError, check.has_size, [
            Case(args=('', set()), kwds={'size': 1}),
            Case(args=('', tuple()), kwds={'min_size': 1}),
            Case(args=('', set([1])), kwds={'max_size': 0}),
            Case(args=('', [1, 2]), kwds={'min_size': 3, 'max_size': 5})])

    def test_not_empty(self) -> None:
        self.assertNoneRaises(ValueError, check.not_empty, [
            Case(args=('', 'x')),
            Case(args=('', {1})),
            Case(args=('', [1])),
            Case(args=('', {1: 1}))])

        self.assertAllRaises(ValueError, check.not_empty, [
            Case(args=('', set())),
            Case(args=('', tuple())),
            Case(args=('', [])),
            Case(args=('', ''))])

class TestEnv(ModuleTestCase):
    module = env

    def setUp(self) -> None:
        self.sys_dirs = ['home', 'cwd']
        self.app_dirs = [
            'user_cache_dir', 'user_config_dir', 'user_data_dir',
            'user_log_dir', 'site_config_dir', 'site_data_dir']
        self.dist_dirs = ['site_package_dir']
        self.pkg_dirs = ['package_dir', 'package_data_dir', 'package_temp_dir']
        self.site_dirs = ['site_temp_dir']
        self.app_vars = [
            'name', 'author', 'version', 'license', 'encoding', 'hostname',
            'username', 'osname']

    def is_dir_valid(
            self, dirname: str, path: Path, appname: str,
            appauthor: str) -> bool:
        if dirname in self.sys_dirs: # Check system directories
            return True
        if dirname in self.app_dirs: # Check application dir
            if env.get_osname() == 'Linux':
                return appname in str(path)
            return appname in str(path) and appauthor in str(path)
        if dirname in self.dist_dirs: # Check distribution dir
            return appname in str(path)
        if dirname in self.pkg_dirs: # Check package dir
            # TODO (patrick.michl@gmail.com): Check if root package name is in
            # str(path)
            return True
        if dirname in self.site_dirs:
            # Site directories can be of arbitrary structure
            return True
        return False

    def is_dirs_valid(self, d: dict, appname: str, appauthor: str) -> bool:
        keys = set(
            self.sys_dirs + self.app_dirs + self.dist_dirs
            + self.pkg_dirs + self.site_dirs)
        if not d.keys() == keys:
            return False
        for key in keys:
            if not self.is_dir_valid(key, d[key], appname, appauthor):
                return False
        return True

    def test_update_dirs(self) -> None:
        app_name = 'funniest'
        app_author = 'Flying Circus'
        dirs_exist = hasattr(env, '_dirs')
        if dirs_exist:
            prev_dirs = getattr(env, '_dirs').copy()
        try:
            env.update_dirs(appname=app_name, appauthor=app_author)
            new_dirs = getattr(env, '_dirs').copy()
            self.assertTrue(self.is_dirs_valid(new_dirs, app_name, app_author))
        finally:
            if dirs_exist:
                setattr(env, '_dirs', prev_dirs)
            else:
                delattr(env, '_dirs')

    def test_get_dirs(self) -> None:
        app_name = env.get_var('name') or 'no name'
        app_author = env.get_var('author') or 'no author'
        app_dirs = env.get_dirs()
        is_valid = self.is_dirs_valid(app_dirs, app_name, app_author)
        self.assertTrue(is_valid)

    def test_get_dir(self) -> None:
        app_name = env.get_var('name') or 'no name'
        app_author = env.get_var('author') or 'no author'
        keys = set(self.app_dirs + self.dist_dirs + self.pkg_dirs)
        for key in keys:
            with self.subTest(f"get_dir('{key}')"):
                path = Path(env.get_dir(key))
                is_valid = self.is_dir_valid(key, path, app_name, app_author)
                self.assertTrue(is_valid)

    def test_get_temp_dir(self) -> None:
        path = env.get_temp_dir()
        self.assertFalse(path.exists())
        path.mkdir()
        self.assertTrue(path.is_dir())
        path.rmdir()
        self.assertFalse(path.exists())

    def test_get_temp_file(self) -> None:
        path = env.get_temp_file()
        self.assertFalse(path.exists())
        path.touch()
        self.assertTrue(path.is_file())
        path.unlink()
        self.assertFalse(path.exists())

    def test_update_vars(self) -> None:
        vars_exist = hasattr(env, '_vars')
        try:
            if vars_exist:
                prev_vars = getattr(env, '_vars').copy()
            env.update_vars(__file__)
            new_vars = getattr(env, '_vars').copy()
            self.assertEqual(new_vars.get('author'), __author__)
            self.assertEqual(new_vars.get('email'), __email__)
            self.assertEqual(new_vars.get('license'), __license__)
        finally:
            if vars_exist:
                setattr(env, '_vars', prev_vars)
            else:
                delattr(env, '_vars')

    def test_get_var(self) -> None:
        cases = [Case(args=(key, )) for key in self.app_vars]
        self.assertAllTrue(env.get_var, cases)

    def test_get_vars(self) -> None:
        envvars = env.get_vars()
        self.assertTrue(set(self.app_vars) <= envvars.keys())

    def test_get_encoding(self) -> None:
        self.assertIsInstance(env.get_encoding(), str)

    def test_get_hostname(self) -> None:
        self.assertIsInstance(env.get_hostname(), str)

    def test_get_osname(self) -> None:
        self.assertIsInstance(env.get_osname(), str)

    def test_get_username(self) -> None:
        self.assertIsInstance(env.get_username(), str)

    def test_get_cwd(self) -> None:
        self.assertTrue(env.get_cwd().is_dir())

    def test_get_home(self) -> None:
        self.assertTrue(env.get_home().is_dir())

    def test_clear_filename(self) -> None:
        self.assertEqual(env.clear_filename('3/\nE{$5}.e'), '3E5.e')

    def test_match_paths(self) -> None:
        paths: PathLikeList = [
            Path('a.b'), Path('b.a'), Path('c/a.b'), Path('a/b/c')]
        val = env.match_paths(paths, 'a.*')
        self.assertEqual(val, [Path('a.b')])
        val = env.match_paths(paths, '*.a')
        self.assertEqual(val, [Path('b.a')])
        val = env.match_paths(paths, 'c/*')
        self.assertEqual(val, [Path('c/a.b')])
        val = env.match_paths(paths, 'a/*/c')
        self.assertEqual(val, [Path('a/b/c')])

    def test_join_path(self) -> None:
        val = env.join_path(('a', ('b', 'c')), 'd')
        self.assertEqual(val, Path('a/b/c/d'))

    def test_expand(self) -> None:
        udict = {'var1': 'a/%var2%', 'var2': 'b'}
        val = env.expand('%var1%/c', 'd', udict=udict)
        self.assertEqual(val, Path('a/b/c/d'))

    def test_get_dirname(self) -> None:
        path = (('a', ('b', 'c')), 'd', 'base.ext')
        val = env.get_dirname(*path)
        self.assertEqual(val, str(Path('a/b/c/d')))

    def test_filename(self) -> None:
        path = (('a', ('b', 'c')), 'd', 'base.ext')
        val = env.filename(*path)
        self.assertEqual(val, 'base.ext')

    def test_basename(self) -> None:
        path = (('a', ('b', 'c')), 'd', 'base.ext')
        val = env.basename(*path)
        self.assertEqual(val, 'base')

    def test_fileext(self) -> None:
        path = (('a', ('b', 'c')), 'd', 'base.ext')
        val = env.fileext(*path)
        self.assertEqual(val, 'ext')

    def test_mkdir(self) -> None:
        dirpath = env.get_temp_dir()
        env.mkdir(dirpath)
        self.assertTrue(dirpath.is_dir())
        dirpath.rmdir()

    def test_is_dir(self) -> None:
        dirpath = env.get_temp_dir()
        dirpath.mkdir()
        self.assertTrue(env.is_dir(dirpath))
        dirpath.rmdir()
        self.assertFalse(env.is_dir(dirpath))

    def test_touch(self) -> None:
        dirpath = env.get_temp_dir()
        filepath = dirpath / 'test'
        env.touch(filepath)
        self.assertTrue(filepath.is_file())
        filepath.unlink()
        dirpath.rmdir()

    def test_copytree(self) -> None:
        root = env.get_temp_dir()
        root.mkdir()
        source = root / 'source'
        source.mkdir()
        (source / 'file').touch()
        (source / 'dir').mkdir()
        target = root / 'target'
        target.mkdir()
        env.copytree(source, target)
        self.assertTrue((target / 'file').is_file())
        (source / 'file').unlink()
        (target / 'file').unlink()
        self.assertTrue((target / 'dir').is_dir())
        (source / 'dir').rmdir()
        (target / 'dir').rmdir()
        source.rmdir()
        target.rmdir()

    def test_is_file(self) -> None:
        file = env.get_temp_dir()
        file.touch()
        self.assertTrue(env.is_file(file))
        file.unlink()
        self.assertFalse(env.is_file(file))

    def test_rmdir(self) -> None:
        dirpath = env.get_temp_dir()
        dirpath.mkdir()
        env.rmdir(dirpath)
        self.assertFalse(dirpath.is_dir())

class TestNbase(ModuleTestCase):
    module = nbase

    def test_ObjectIP(self) -> None:
        obj = nbase.ObjectIP()
        obj.name = 'test'
        self.assertTrue(obj.get('config') == {'name': 'test'})
        obj.path = ('%site_data_dir%', 'test')
        self.assertNotIn('%', obj.path)

class TestBinary(ModuleTestCase):
    module = binary

    def test_as_bytes(self) -> None:
        self.assertEqual(binary.as_bytes(b'test'), b'test')
        self.assertEqual(binary.as_bytes('test'), b'test')
        self.assertEqual(binary.as_bytes(bytearray(b'test')), b'test')
        self.assertEqual(binary.as_bytes(memoryview(b'test')), b'test')

    def test_compress(self) -> None:
        data = binary.compress(b'test', level=0)
        self.assertEqual(data, b'x\x01\x01\x04\x00\xfb\xfftest\x04]\x01\xc1')
        data = binary.compress(b'test', level=1)
        self.assertEqual(data, b'x\x01+I-.\x01\x00\x04]\x01\xc1')
        data = binary.compress(b'test', level=9)
        self.assertEqual(data, b'x\xda+I-.\x01\x00\x04]\x01\xc1')

    def test_decompress(self) -> None:
        for level in range(-1, 10):
            data = binary.compress(b'test', level=level)
            self.assertEqual(binary.decompress(data), b'test')

    def test_encode(self) -> None:
        data = binary.encode(b'test', encoding='base64')
        self.assertEqual(data, b'dGVzdA==')
        data = binary.encode(b'test', encoding='base32')
        self.assertEqual(data, b'ORSXG5A=')
        data = binary.encode(b'test', encoding='base16')
        self.assertEqual(data, b'74657374')

    def test_decode(self) -> None:
        for encoding in ['base64', 'base32', 'base16', 'base85']:
            data = binary.encode(b'test', encoding=encoding)
            self.assertEqual(binary.decode(data, encoding=encoding), b'test')

    def test_pack(self) -> None:
        data = binary.pack({True: 1}, encoding='base64')
        self.assertEqual(data, b'gAN9cQCISwFzLg==')
        data = binary.pack(None, encoding='base32')
        self.assertEqual(data, b'QABU4LQ=')
        data = binary.pack(True, encoding='base16', compression=9)
        self.assertEqual(data, b'78DA6B60EED00300034B013A')

    def test_unpack(self) -> None:
        o1 = None
        o2 = [None, True, 1, .0, 1+1j, 'a', b'b', type]
        o3 = {True: 1, 'a': [.5, (1j, ), None]}
        tests = [(o1, None, None), (o2, None, None), (o3, None, None)]
        for obj, enc, comp in tests:
            data = binary.pack(obj, encoding=enc, compression=comp)
            iscomp = isinstance(comp, int)
            self.assertEqual(binary.unpack(data, compressed=iscomp), obj)

class TestNdict(ModuleTestCase):
    module = mapping

    def test_select(self) -> None:
        self.assertTrue(
            mapping.select({'a1': 1, 'a2': 2, 'b1': 3}, pattern='a*') \
            == {'a1': 1, 'a2': 2})

    def test_groupby(self) -> None:
        self.assertEqual(
            mapping.groupby(
                {1: {'a': 0}, 2: {'a': 0}, 3: {'a': 1}, 4: {}}, key='a'),
            {
                0: {1: {'a': 0}, 2: {'a': 0}},
                1: {3: {'a': 1}}, None: {4: {}}})

    def test_flatten(self) -> None:
        self.assertEqual(
            mapping.flatten({1: {'a': {}}, 2: {'b': {}}}),
            {'a': {}, 'b': {}})
        self.assertEqual(
            mapping.flatten({1: {'a': {}}, 2: {'b': {}}}, group='id'),
            {'a': {'id': 1}, 'b': {'id': 2}})

    def test_merge(self) -> None:
        self.assertEqual(
            mapping.merge({'a': 1}, {'a': 2, 'b': 2}, {'c': 3}),
            {'a': 1, 'b': 2, 'c': 3})

    def test_crop(self) -> None:
        self.assertEqual(
            mapping.crop({'a1': 1, 'a2': 2, 'b1': 3}, 'a'),
            {'1': 1, '2': 2})

    def test_strkeys(self) -> None:
        self.assertEqual(
            mapping.strkeys({(1, 2): 3, None: {True: False}}),
            {('1', '2'): 3, 'None': {'True': False}})

    def test_sumjoin(self) -> None:
        self.assertEqual(
            mapping.sumjoin({'a': 1}, {'a': 2, 'b': 3}), {'a': 3, 'b': 3})
        self.assertEqual(
            mapping.sumjoin({1: 'a', 2: True}, {1: 'b', 2: True}),
            {1: 'ab', 2: 2})

class TestLiteral(ModuleTestCase):
    module = literal

    def test_as_path(self) -> None:
        self.assertAllEqual(literal.as_path, [
            Case(args=('a/b/c', ), value=Path('a/b/c')),
            Case(args=('%cwd%/test', ), value=Path.cwd() / 'test'),
            Case(args=('%home%/test', ), value=Path.home() / 'test')])

    def test_as_datetime(self) -> None:
        val = datetime.datetime.now()
        self.assertEqual(literal.as_datetime(str(val)), val)

    def test_as_list(self) -> None:
        self.assertAllEqual(literal.as_list, [
            Case(args=('a, 2, ()', ), value=['a', '2', '()']),
            Case(args=('[1, 2, 3]', ), value=[1, 2, 3])])

    def test_as_tuple(self) -> None:
        self.assertAllEqual(literal.as_tuple, [
            Case(args=('a, 2, ()', ), value=('a', '2', '()')),
            Case(args=('(1, 2, 3)', ), value=(1, 2, 3))])

    def test_as_set(self) -> None:
        self.assertAllEqual(literal.as_set, [
            Case(args=('a, 2, ()', ), value={'a', '2', '()'}),
            Case(args=('{1, 2, 3}', ), value={1, 2, 3})])

    def test_as_dict(self) -> None:
        self.assertAllEqual(literal.as_dict, [
            Case(args=("a = 'b', b = 1", ), value={'a': 'b', 'b': 1}),
            Case(args=("'a': 'b', 'b': 1", ), value={'a': 'b', 'b': 1})])

    def test_decode(self) -> None:
        self.assertAllEqual(literal.decode, [
            Case(args=('text', str), value='text'),
            Case(args=(repr(True), bool), value=True),
            Case(args=(repr(1), int), value=1),
            Case(args=(repr(.5), float), value=.5),
            Case(args=(repr(1+1j), complex), value=1+1j)])

    def test_from_str(self) -> None:
        self.assertAllEqual(literal.from_str, [
            Case(args=(chr(1) + 'a', 'printable'), value='a'),
            Case(args=('a, b', 'uax-31'), value='ab'),
            Case(args=('max(x)', 'uax-31'),
                kwds={'spacer': '_'}, value='max_x_')])

    def test_encode(self) -> None:
        self.assertAllEqual(literal.encode, [
            Case(args=(chr(1) + 'a', ),
                kwds={'charset': 'printable'}, value='a'),
            Case(args=('a, b', ),
                kwds={'charset': 'uax-31'}, value='ab')])

    def test_estimate(self) -> None:
        Date = datetime.datetime
        self.assertAllEqual(literal.estimate, [
            Case(args=('text', ), value=None),
            Case(args=(repr('text'), ), value=str),
            Case(args=(repr(True), ), value=bool),
            Case(args=(repr(1), ), value=int),
            Case(args=(repr(1.), ), value=float),
            Case(args=(repr(1j), ), value=complex),
            Case(args=(str(Date.now()), ), value=Date)])

class TestStack(ModuleTestCase):
    module = stack

    def test_get_caller_module_name(self) -> None:
        name = stack.get_caller_module_name()
        self.assertEqual(name, __name__)

    def test_get_caller_module(self) -> None:
        module = stack.get_caller_module()
        self.assertIsInstance(module, Module)

    def test_get_caller_name(self) -> None:
        thisname = stack.get_caller_name()
        self.assertEqual(thisname, __name__ + '.test_get_caller_name')


class TestPkg(ModuleTestCase):
    module = pkg

    def test_has_attr(self) -> None:
        pass # Function is testet in otree.get_module

    def test_call_attr(self) -> None:
        pass # Function is testet in otree.call_attr

    def test_get_attr(self) -> None:
        attr = pkg.get_attr('__name__')
        self.assertEqual(attr, __name__)

    def test_get_submodule(self) -> None:
        parent = pkg.get_parent(pkg)
        this = pkg.get_submodule(name='pkg', parent=parent)
        self.assertIsInstance(this, Module)

    def test_get_submodules(self) -> None:
        parent = pkg.get_parent(pkg)
        submodules = pkg.get_submodules(parent=parent)
        self.assertIn(__name__, submodules)

    def test_get_root(self) -> None:
        root = pkg.get_root()
        self.assertEqual(root.__name__, 'nemoa')

    def test_get_parent(self) -> None:
        parent = pkg.get_parent(pkg)
        self.assertEqual(parent.__name__, 'nemoa.base')

    def test_get_module(self) -> None:
        this = pkg.get_module()
        self.assertEqual(this.__name__, __name__) # type: ignore

    def test_crop_functions(self) -> None:
        name = pkg.crop_functions.__name__
        fullname = pkg.crop_functions.__module__ + '.' + name
        cropped = pkg.crop_functions(prefix='crop_', module=pkg)
        self.assertIn('functions', cropped)

    def test_search(self) -> None:
        count = len(pkg.search(module=pkg, name='search'))
        self.assertEqual(count, 1)
