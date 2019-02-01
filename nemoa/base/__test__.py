# -*- coding: utf-8 -*-
"""Unittests for package 'nemoa.base'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from collections import OrderedDict
import datetime
import math
from unittest import mock
from pathlib import Path
from typing import Any, Callable, Union
import numpy as np
from nemoa.base import abc, array, attrib, binary, call, catalog, check, env
from nemoa.base import literal, mapping, otree, parser, pkg, stack, stype
from nemoa.base import nbase
from nemoa.test import ModuleTestCase, Case
from nemoa.types import AnyOp, Module, PathLikeList, StrList, NaN, Method
from nemoa.types import Function

#
# Test Cases
#

class TestAbc(ModuleTestCase):
    module = abc

    def test_SingletonMeta(self) -> None:
        pass # Implicitly tested by test_Singleton()

    def test_Singleton(self) -> None:
        T = type('Singleton', (abc.Singleton, ), {})

        self.assertTrue(T() is T())
        self.assertTrue(T(1) is T(2))

    def test_IsolatedMeta(self) -> None:
        pass # Implicitly tested by test_Isolated()

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
        pass # Implicitly tested by test_Multiton()

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

    def test_cast(self) -> None:
        x = np.array([[NaN, 1.], [NaN, NaN]])
        with self.subTest(x=x):
            self.assertNotRaises(TypeError, array.cast, x)
            self.assertIsInstance(array.cast(x), np.ndarray)

        x = list(range(1000))
        with self.subTest(x=x):
            self.assertNotRaises(TypeError, array.cast, x)
            self.assertIsInstance(array.cast(x), np.ndarray)

        x = set()
        with self.subTest(x=x):
            self.assertRaises(TypeError, array.cast, x)
            self.assertNotRaises(TypeError, array.cast, x, otype=True)

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

    def test_Content(self) -> None:
        Group = type('Group', (attrib.Group, ), {'data': attrib.Content()})
        group = Group()
        group.data = 'test'
        self.assertEqual(group._attr_group_data['data'], 'test')

    def test_MetaData(self) -> None:
        Group = type('Group', (attrib.Group, ), {'meta': attrib.MetaData()})
        group = Group()
        group.meta = 'test'
        self.assertEqual(group._attr_group_meta['meta'], 'test')

    def test_Temporary(self) -> None:
        Group = type('Group', (attrib.Group, ), {'temp': attrib.Temporary()})
        group = Group()
        group.temp = 'test'
        self.assertEqual(group._attr_group_temp['temp'], 'test')

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

        with self.subTest(default= 'ok'):
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
            attrs = group._get_attr_names(category='test')
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

class TestCatalog(ModuleTestCase):
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

        @catalog.register(Reg, name='euclid')
        def euclid_norm(x: float, y: float) -> float:
            return math.sqrt(x ** 2 + y ** 2)

        man = catalog.Manager()
        card = man.get(euclid_norm)
        self.assertEqual(card.category, Reg)
        self.assertEqual(card.reference, euclid_norm)
        self.assertEqual(card.data, {'name': 'euclid'})

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

class TestParser(ModuleTestCase):
    module = parser

    def test_PyCore(self) -> None:
        # The individual operators are tested within seperate tests. Here the
        # operator associativity and precedence is tested
        p = parser.Parser(grammar=parser.PyCore())
        peval: AnyOp = lambda expr, val: p.parse(expr).eval(val)

        # Boolean Operators
        with self.subTest():
            self.assertCaseEqual(peval, [
                Case(('x and not(y)', {'x': 1, 'y': 0}), {}, True),
                Case(('not(x and y)', {'x': 1, 'y': 0}), {}, True),
                Case(('x or y and z', {'x': 1, 'y': 0, 'z': 0}), {}, True),
                Case(('(x or y) and z', {'x': 1, 'y': 0, 'z': 0}), {}, False)])

        # Bitwise Operators
        with self.subTest():
            self.assertCaseEqual(peval, [
                Case(('x | (~y)', {'x': 1, 'y': 0}), {}, -1),
                Case(('~(x | y)', {'x': 1, 'y': 0}), {}, -2),
                Case(('x | y ^ z', {'x': 1, 'y': 0, 'z': 3}), {}, 3),
                Case(('(x | y) ^ z', {'x': 1, 'y': 0, 'z': 3}), {}, 2),
                Case(('x ^ y ^ z', {'x': 1, 'y': 0, 'z': 3}), {}, 2),
                Case(('x ^ y & z', {'x': 3, 'y': 1, 'z': 0}), {}, 3),
                Case(('(x ^ y) & z', {'x': 3, 'y': 1, 'z': 0}), {}, 0),
                Case(('x & y >> z', {'x': 2, 'y': 4, 'z': 1}), {}, 2),
                Case(('(x & y) >> z', {'x': 2, 'y': 4, 'z': 1}), {}, 0)])

        # Arithmetic Operators
        with self.subTest():
            self.assertCaseEqual(peval, [
                Case(('x + (-y)', {'x': 1, 'y': 1}), {}, 0),
                Case(('-(x + y)', {'x': 1, 'y': 1}), {}, -2),
                Case(('x + y * z', {'x': 1, 'y': 0, 'z': 0}), {}, 1),
                Case(('(x + y) * z', {'x': 1, 'y': 0, 'z': 0}), {}, 0),
                Case(('x * y ** z', {'x': 2, 'y': 2, 'z': 2}), {}, 8),
                Case(('(x * y) ** z', {'x': 2, 'y': 2, 'z': 2}), {}, 16)])

        # Mixed Operators
        with self.subTest():
            self.assertCaseEqual(peval, [
                Case(('x and y | z', {'x': 0, 'y': 2, 'z': 3}), {}, 0),
                Case(('(x and y) | z', {'x': 0, 'y': 2, 'z': 3}), {}, 3),
                Case(('x << y + z', {'x': 1, 'y': 2, 'z': 3}), {}, 32),
                Case(('(x << y) + z', {'x': 1, 'y': 2, 'z': 3}), {}, 7)])

    def test_PyCore_boolean(self) -> None:
        p = parser.Parser(grammar=parser.PyCore())
        peval: AnyOp = lambda expr, val: p.parse(expr).eval(val)

        # Boolean OR
        with self.subTest(symbol='or'):
            self.assertCaseEqual(peval, [
                Case(('x or y', {'x': True, 'y': False}), {}, True),
                Case(('x or y', {'x': False, 'y': True}), {}, True),
                Case(('x or y', {'x': False, 'y': False}), {}, False),
                Case(('x or y', {'x': True, 'y': True}), {}, True)])

        # Boolean AND
        with self.subTest(symbol='and'):
            self.assertCaseEqual(peval, [
                Case(('x and y', {'x': True, 'y': False}), {}, False),
                Case(('x and y', {'x': False, 'y': True}), {}, False),
                Case(('x and y', {'x': False, 'y': False}), {}, False),
                Case(('x and y', {'x': True, 'y': True}), {}, True)])

        # Boolean NOT
        with self.subTest(symbol='not'):
            self.assertCaseEqual(peval, [
                Case(('not(x)', {'x': True}), {}, False),
                Case(('not(x)', {'x': False}), {}, True)])

    def test_PyCore_ordering(self) -> None:
        p = parser.Parser(grammar=parser.PyCore())
        peval: AnyOp = lambda expr, val: p.parse(expr).eval(val)

        # Equality
        with self.subTest(symbol='=='):
            self.assertCaseEqual(peval, [
                Case(('x == y', {'x': 1, 'y': 1}), {}, True),
                Case(('x == y', {'x': 1, 'y': 2}), {}, False),
                Case(('x == y', {'x': 'a', 'y': 'a'}), {}, True),
                Case(('x == y', {'x': 'a', 'y': 'b'}), {}, False)])

        # Inequality
        with self.subTest(symbol='!='):
            self.assertCaseEqual(peval, [
                Case(('x != y', {'x': 1, 'y': 1}), {}, False),
                Case(('x != y', {'x': 1, 'y': 2}), {}, True),
                Case(('x != y', {'x': 'a', 'y': 'a'}), {}, False),
                Case(('x != y', {'x': 'a', 'y': 'b'}), {}, True)])

        # Greater
        with self.subTest(symbol='>'):
            self.assertCaseEqual(peval, [
                Case(('x > y', {'x': 1, 'y': 1}), {}, False),
                Case(('x > y', {'x': 2, 'y': 1}), {}, True),
                Case(('x > y', {'x': 'a', 'y': 'a'}), {}, False),
                Case(('x > y', {'x': 'b', 'y': 'a'}), {}, True)])

        # Greater or Equal
        with self.subTest(symbol='>='):
            self.assertCaseEqual(peval, [
                Case(('x >= y', {'x': 1, 'y': 2}), {}, False),
                Case(('x >= y', {'x': 1, 'y': 1}), {}, True),
                Case(('x >= y', {'x': 'a', 'y': 'b'}), {}, False),
                Case(('x >= y', {'x': 'a', 'y': 'a'}), {}, True)])

        # Lower
        with self.subTest(symbol='<'):
            self.assertCaseEqual(peval, [
                Case(('x < y', {'x': 1, 'y': 1}), {}, False),
                Case(('x < y', {'x': 1, 'y': 2}), {}, True),
                Case(('x < y', {'x': 'a', 'y': 'a'}), {}, False),
                Case(('x < y', {'x': 'a', 'y': 'b'}), {}, True)])

        # Lower or Equal
        with self.subTest(symbol='<='):
            self.assertCaseEqual(peval, [
                Case(('x <= y', {'x': 2, 'y': 1}), {}, False),
                Case(('x <= y', {'x': 1, 'y': 1}), {}, True),
                Case(('x <= y', {'x': 'b', 'y': 'a'}), {}, False),
                Case(('x <= y', {'x': 'a', 'y': 'a'}), {}, True)])

        # Identity
        with self.subTest(symbol='is'):
            self.assertCaseEqual(peval, [
                Case(('x is y', {'x': True, 'y': True}), {}, True),
                Case(('x is y', {'x': True, 'y': False}), {}, False)])

        # Containment
        with self.subTest(symbol='in'):
            self.assertCaseEqual(peval, [
                Case(('x in y', {'x': 'a', 'y': 'a'}), {}, True),
                Case(('x in y', {'x': 'a', 'y': 'b'}), {}, False),
                Case(('x in y', {'x': 'a', 'y': 'ba'}), {}, True),
                Case(('x in y', {'x': 'ab', 'y': 'ba'}), {}, False)])

    def test_PyCore_bitwise(self) -> None:
        p = parser.Parser(grammar=parser.PyCore())
        peval: AnyOp = lambda expr, val: p.parse(expr).eval(val)

        # Bitwise Inversion
        with self.subTest(symbol='~'):
            self.assertCaseEqual(peval, [
                Case(('~x', {'x': 0}), {}, -1),
                Case(('~x', {'x': -1}), {}, 0),
                Case(('~x', {'x': 1}), {}, -2),
                Case(('~x', {'x': -2}), {}, 1),
                Case(('~(~x)', {'x': 3}), {}, 3)])

        # Bitwise Right Shift
        with self.subTest(symbol='>>'):
            self.assertCaseEqual(peval, [
                Case(('x >> y', {'x': 1, 'y': 1}), {}, 0),
                Case(('x >> y', {'x': 2, 'y': 2}), {}, 0),
                Case(('x >> y', {'x': 1, 'y': 2}), {}, 0),
                Case(('x >> y', {'x': 2, 'y': 1}), {}, 1)])

        # Bitwise Left Shift
        with self.subTest(symbol='>>'):
            self.assertCaseEqual(peval, [
                Case(('x << y', {'x': 1, 'y': 1}), {}, 2),
                Case(('x << y', {'x': 2, 'y': 2}), {}, 8),
                Case(('x << y', {'x': 1, 'y': 2}), {}, 4),
                Case(('x << y', {'x': 2, 'y': 1}), {}, 4)])

        # Bitwise AND
        with self.subTest(symbol='&'):
            self.assertCaseEqual(peval, [
                Case(('x & y', {'x': 2, 'y': 2}), {}, 2),
                Case(('x & y', {'x': 2, 'y': 3}), {}, 2),
                Case(('x & y', {'x': 1, 'y': 3}), {}, 1),
                Case(('x & y', {'x': 1, 'y': 2}), {}, 0)])

        # Bitwise XOR
        with self.subTest(symbol='^'):
            self.assertCaseEqual(peval, [
                Case(('x ^ y', {'x': 2, 'y': 2}), {}, 0),
                Case(('x ^ y', {'x': 2, 'y': 3}), {}, 1),
                Case(('x ^ y', {'x': 1, 'y': 3}), {}, 2),
                Case(('x ^ y', {'x': 1, 'y': 2}), {}, 3)])

        # Bitwise OR
        with self.subTest(symbol='|'):
            self.assertCaseEqual(peval, [
                Case(('x | y', {'x': 2, 'y': 2}), {}, 2),
                Case(('x | y', {'x': 2, 'y': 3}), {}, 3),
                Case(('x | y', {'x': 1, 'y': 3}), {}, 3),
                Case(('x | y', {'x': 1, 'y': 2}), {}, 3)])

    def test_PyCore_arithmetic(self) -> None:
        p = parser.Parser(grammar=parser.PyCore())
        peval: AnyOp = lambda expr, val: p.parse(expr).eval(val)

        # Unary Plus
        with self.subTest(symbol='+'):
            self.assertCaseEqual(peval, [
                Case(('+x', {'x': 1}), {}, 1),
                Case(('+x', {'x': -1}), {}, -1),
                Case(('+(+x)', {'x': 1}), {}, 1),
                Case(('+(+x)', {'x': -1}), {}, -1)])

        # Negation
        with self.subTest(symbol='-'):
            self.assertCaseEqual(peval, [
                Case(('-x', {'x': 1}), {}, -1),
                Case(('-x', {'x': -1}), {}, 1),
                Case(('-(-x)', {'x': 1}), {}, 1),
                Case(('-(-x)', {'x': -1}), {}, -1)])

        # Exponentiation
        with self.subTest(symbol='**'):
            self.assertCaseEqual(peval, [
                Case(('x ** y', {'x': 1, 'y': 1}), {}, 1),
                Case(('x ** y', {'x': 1., 'y': 1}), {}, 1.),
                Case(('x ** y', {'x': 4, 'y': .5}), {}, 2.),
                Case(('x ** y', {'x': 2, 'y': 2.}), {}, 4.)])

        # Division
        with self.subTest(symbol='/'):
            self.assertCaseEqual(peval, [
                Case(('x / y', {'x': 1, 'y': 1}), {}, 1.),
                Case(('x / y', {'x': 2, 'y': 1}), {}, 2.),
                Case(('x / y', {'x': 1, 'y': .2}), {}, 5.),
                Case(('x / y', {'x': 1, 'y': 2}), {}, .5)])

        # Floor Division
        with self.subTest(symbol='//'):
            self.assertCaseEqual(peval, [
                Case(('x // y', {'x': 1, 'y': 1}), {}, 1),
                Case(('x // y', {'x': 2, 'y': 1}), {}, 2),
                Case(('x // y', {'x': 1, 'y': .2}), {}, 4),
                Case(('x // y', {'x': 1, 'y': 2}), {}, 0)])

        # Remainder
        with self.subTest(symbol='%'):
            self.assertCaseEqual(peval, [
                Case(('x % y', {'x': 2, 'y': 3}), {}, 2),
                Case(('x % y', {'x': 3, 'y': 2}), {}, 1),
                Case(('x % y', {'x': 2, 'y': 1}), {}, 0),
                Case(('x % y', {'x': .1, 'y': .5}), {}, .1)])

        # Multiplication
        with self.subTest(symbol='*'):
            self.assertCaseEqual(peval, [
                Case(('x * y', {'x': -1, 'y': -1}), {}, 1),
                Case(('x * y', {'x': 2, 'y': .5}), {}, 1),
                Case(('x * y', {'x': 2, 'y': 2}), {}, 4),
                Case(('x * y', {'x': -.5, 'y': .5}), {}, -.25)])

        # Addition
        with self.subTest(symbol='+'):
            self.assertCaseEqual(peval, [
                Case(('x + y', {'x': 0, 'y': 1}), {}, 1),
                Case(('x + y', {'x': -1, 'y': 1}), {}, 0),
                Case(('x + y', {'x': 2, 'y': 2}), {}, 4),
                Case(('x + y', {'x': .5, 'y': .5}), {}, 1)])

        # Subtraction
        with self.subTest(symbol='-'):
            self.assertCaseEqual(peval, [
                Case(('x - y', {'x': 0, 'y': 1}), {}, -1),
                Case(('x - y', {'x': -1, 'y': 1}), {}, -2),
                Case(('x - y', {'x': 2, 'y': 2}), {}, 0),
                Case(('x - y', {'x': .5, 'y': .5}), {}, 0)])

        # Matrix Product
        with self.subTest(symbol='@'):
            zero = np.matrix([(0, 0), (0, 0)]) # Zero Projection
            idem = np.matrix([(1, 0), (0, 1)]) # Identity
            exch = np.matrix([(0, 1), (1, 0)]) # Exchange
            prj1 = np.matrix([(1, 0), (0, 0)]) # Projection 1
            prj2 = np.matrix([(0, 0), (0, 1)]) # Projection 2

            self.assertCaseEqual(peval, [
                Case(('x @ y', {'x': idem, 'y': idem}), {}, idem),
                Case(('x @ y', {'x': idem, 'y': prj1}), {}, prj1),
                Case(('x @ y', {'x': prj2, 'y': idem}), {}, prj2),
                Case(('x @ y', {'x': zero, 'y': idem}), {}, zero),
                Case(('x @ y', {'x': prj1, 'y': zero}), {}, zero),
                Case(('x @ y', {'x': exch, 'y': exch}), {}, idem),
                Case(('x @ y', {'x': prj1, 'y': prj2}), {}, zero)])

    def test_Expression(self) -> None:
        pass # Implicitely tested by test_Parser

    def test_Parser(self) -> None:
        pass # Implicitely tested within grammars PyCore and PyExprEval

    def test_PyExprEval(self) -> None:
        p = parser.Parser(grammar=parser.PyExprEval())
        peval: AnyOp = lambda expr, val: p.parse(expr).eval(val)

        self.assertEqual(peval("Ee1", {"Ee1": 2}), 2)
        self.assertEqual(peval("Ee1+1", {"Ee1": 1}), 2)
        self.assertEqual(peval('2^x', {'x': 3}), 8.0)
        self.assertEqual(peval('2-3^x', {'x': 4}), -79.0)
        self.assertEqual(peval('-2-3^x', {'x': 4}), -83.0)
        self.assertEqual(peval('-3^x', {'x': 4}), -81.0)
        self.assertEqual(peval('(-3)^x', {'x': 4}), 81.0)
        self.assertEqual(peval('2*x+y', {'x': 4, 'y': 1}), 9)
        self.assertEqual(peval("'x'=='x'", {}), True)
        self.assertEqual(peval("(a+b)==c", {'a': 1, 'b': 2, 'c': 3}), True)
        self.assertEqual(peval("(a+b)!=c", {'a': 1, 'b': 2, 'c': 3}), False)
        self.assertEqual(peval("x||y", {'x': 'hi ', 'y': 'u'}), 'hi u')
        self.assertEqual(peval("'x'||'y'", {}), 'xy')
        self.assertEqual(peval("concat('hi',' ','u')", {}), 'hi u')
        self.assertEqual(peval('if(a>b,5,6)', {'a':8, 'b':3}), 5)
        self.assertEqual(peval('if(a,b,c)', {'a':None, 'b':1, 'c':3}), 3)
        self.assertEqual(peval('a,3', {'a': [1, 2]}), [1, 2, 3])
        self.assertEqual(peval(".1", {}), peval("0.1", {}))
        self.assertEqual(peval(".1*.2", {}), peval("0.1*0.2", {}))
        self.assertEqual(peval(".5^3", {}), .125)
        self.assertEqual(peval("16^.5", {}), 4.)
        self.assertEqual(peval("8300*.8", {}), 6640.)
        self.assertEqual(peval('"a b"*2', {'"a b"': 2}), 4)

        self.assertEqual(
            peval("(a^2-b^2)==((a+b)*(a-b))", {'a': 4859, 'b': 13150}), True)
        self.assertEqual(
            peval("(a^2-b^2+1)==((a+b)*(a-b))", {'a': 4859, 'b': 13150}), False)

        self.assertRaises(ValueError, peval, "..5", {})

    def test_Parser_subst(self) -> None:
        p = parser.Parser(grammar=parser.PyExprEval())

        expr = p.parse('2*x+1').subst('x', '4*x')
        self.assertExactEqual(expr({'x': 3}), 25)

    def test_Parser_simplify(self) -> None:
        p = parser.Parser(grammar=parser.PyExprEval())
        f: AnyOp = lambda expr, d: p.parse(expr).simplify(d)

        # expr = p.parse('x * (y * atan(1))').simplify({'y': 4})
        # self.assertIn('x*3.141592', expr.to_string())
        self.assertExactEqual(f("x/((x+y))", {})({'x': 1, 'y': 1}), 0.5)
        self.assertExactEqual(
            f('x*(y*atan(1))', {'y': 4})({'x': 2}), 6.283185307179586)
        self.assertEqual(f('x*(y*atan(1))', {'y': 4}).variables, ['x'])

    def test_Parser_to_string(self) -> None:
        p = parser.Parser(grammar=parser.PyExprEval())

        expr = p.parse("'a'=='b'")
        self.assertEqual("'a'=='b'", str(expr))
        self.assertEqual("'a'=='b'", str(expr))

        expr = p.parse("concat('a\n','\n','\rb')=='a\n\n\rb'")
        self.assertEqual(expr.eval({}), True)

        expr = p.parse("a==''")
        self.assertEqual(expr.eval({'a':''}), True)

        expr = p.parse("func(a,1.51,'ok')")
        self.assertEqual(str(expr.subst('a', 'b')), "func(b, 1.51, 'ok')")

    def test_Parser_variables(self) -> None:
        p = parser.Parser(grammar=parser.PyExprEval())
        getvars: AnyOp = lambda expr: p.parse(expr).variables
        # TODO: use assertCaseEqual

        self.assertEqual(getvars('x * (y * atan(1))'), ['x', 'y'])
        self.assertEqual(getvars('pow(x,y)'), ['x', 'y'])

        # constants: E and PI
        self.assertEqual(getvars("PI"), [])
        self.assertEqual(getvars("PI "), [])
        self.assertEqual(getvars("E "), [])
        self.assertEqual(getvars(" E"), [])
        self.assertEqual(getvars("E"), [])
        self.assertEqual(getvars("E+1"), [])
        self.assertEqual(getvars("E / 1"), [])
        self.assertEqual(getvars("sin(PI)+E"), [])
        self.assertEqual(getvars('Pie'), ["Pie"])
        self.assertEqual(getvars('PIe'), ["PIe"])
        self.assertEqual(getvars('Eval'), ["Eval"])
        self.assertEqual(getvars('Eval1'), ["Eval1"])
        self.assertEqual(getvars('EPI'), ["EPI"])
        self.assertEqual(getvars('PIE'), ["PIE"])
        self.assertEqual(getvars('Engage'), ["Engage"])
        self.assertEqual(getvars('Engage * PIE'), ["Engage", "PIE"])
        self.assertEqual(getvars('Engage_'), ["Engage_"])
        self.assertEqual(getvars('Engage1'), ["Engage1"])
        self.assertEqual(getvars('E1'), ["E1"])
        self.assertEqual(getvars('PI2'), ["PI2"])
        self.assertEqual(getvars('(E1 + PI)'), ["E1"])
        self.assertEqual(getvars('E1_'), ["E1_"])
        self.assertEqual(getvars('E_'), ["E_"])

    def test_Parser_symbols(self) -> None:
        p = parser.Parser(grammar=parser.PyExprEval())

        self.assertEqual(p.parse('pow(x,y)').symbols, ['pow', 'x', 'y'])

    def test_Parser_functions(self) -> None:
        p = parser.Parser(grammar=parser.PyExprEval())

        def testFunction0() -> Any:
            return 13

        def testFunction1(a: Any) -> Any:
            return 2 * a + 9

        def testFunction2(a: Any, b: Any) -> Any:
            return 2 * a + 3 * b

        def mean(*xs: Any) -> Any:
            return sum(xs) / len(xs)

        def counter(initial: Any) -> Any:
            class nonlocals:
                x: Any = initial
            def count(increment: Any) -> Any:
                nonlocals.x += increment
                return nonlocals.x
            return count

        self.assertExactEqual(
            p.parse('testFunction(x)').eval(
                {"x":2, "testFunction": testFunction1}), 13)

        self.assertExactEqual(
            p.parse('testFunction(x , y)').eval(
                {"x":2, "y":3, "testFunction": testFunction2}), 13)

        p.grammar.add(parser.Symbol(parser.FUNCTION, 'mean', mean))
        p.grammar.add(parser.Symbol(parser.FUNCTION, 'count', counter(0)))

        self.assertEqual(p.parse("mean(xs)").variables, ["xs"])
        self.assertEqual(p.parse("mean(xs)").symbols, ["mean", "xs"])
        self.assertEqual(p.eval("mean(xs)", variables={"xs": [1, 2, 3]}), 2)
        self.assertExactEqual(p.eval("count(inc)", variables={"inc": 5}), 5)
        self.assertExactEqual(p.eval("count(inc)", variables={"inc": 5}), 10)

    def test_Token(self) -> None:
        pass # Implicitely tested by test_Parser

class TestStype(ModuleTestCase):
    module = stype

    def test_Field(self) -> None:
        pass # Implicitly tested by test_create_domain()

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
        pass # Implicitly tested by test_create_domain()

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

class TestCall(ModuleTestCase):
    module = call

    def test_safe_call(self) -> None:
        f = call.parameters
        self.assertCaseEqual(call.safe_call, [
            Case(args=(f, list), value=OrderedDict()),
            Case(args=(f, list), kwds={'test': True}, value=OrderedDict())])

    def test_parameters(self) -> None:
        f = call.parameters
        self.assertCaseEqual(call.parameters, [
            Case(args=(f, ), value=OrderedDict()),
            Case(args=(f, list), value=OrderedDict([('op', list)])),
            Case(args=(f, list), kwds={'test': True},
                value=OrderedDict([('op', list), ('test', True)]))])

    def test_parse(self) -> None:
        self.assertEqual(call.parse("f(1., 'a', b = 2)"),
            ('f', (1.0, 'a'), {'b': 2}))

class TestOtree(ModuleTestCase):
    module = otree

    def test_has_base(self) -> None:
        self.assertCaseEqual(otree.has_base, [
            Case(args=(object, object), value=True),
            Case(args=(object, 'object'), value=True),
            Case(args=('object', object), value=True),
            Case(args=('object', str), value=True),
            Case(args=(object, 'str'), value=False),
            Case(args=(object, type), value=False),
            Case(args=('object', type), value=False)])

    def test_get_members(self) -> None:
        self.assertCaseContain(otree.get_members, [
            Case(args=(object, ), value='__class__'),
            Case(args=(otree, ), value='get_members'),
            Case(args=(otree, ), kwds={'classinfo': Function},
                value='get_members'),
            Case(args=(otree, ), kwds={'name': 'get_members'},
                value='get_members'),
            Case(args=(otree, ), kwds={
                'rules': {'about': lambda arg, attr: arg in attr},
                'about': 'members'}, value='get_members')])

        self.assertCaseNotContain(otree.get_members, [
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
        self.assertCaseContain(otree.get_members_dict, [
            Case(args=(object, ), value='object.__class__'),
            Case(args=(otree, ), value='nemoa.base.otree.get_members'),
            Case(args=(otree, ), kwds={'classinfo': Function},
                value='nemoa.base.otree.get_members'),
            Case(args=(otree, ), kwds={'name': 'get_members'},
                value='nemoa.base.otree.get_members'),
            Case(args=(otree, ), kwds={
                'rules': {'about': lambda arg, attr: arg in attr},
                'about': 'members'}, value='nemoa.base.otree.get_members')])

        self.assertCaseNotContain(otree.get_members_dict, [
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
        self.assertCaseEqual(otree.get_name, [
            Case(args=('', ), value='str'),
            Case(args=(0, ), value='int'),
            Case(args=(object, ), value='object'),
            Case(args=(object(), ), value='object'),
            Case(args=(otree.get_name, ), value='get_name'),
            Case(args=(otree, ), value='nemoa.base.otree')])

    def test_get_lang_repr(self) -> None:
        self.assertCaseEqual(otree.get_lang_repr, [
            Case(args=(set(), ), value='no elements'),
            Case(args=([], ), value='no items'),
            Case(args=(['a'], ), value="item 'a'"),
            Case(args=([1, 2], ), value="items '1' and '2'"),
            Case(args=(['a', 'b'], 'or'), value="items 'a' or 'b'")])

    def test_get_summary(self) -> None:
        self.assertCaseEqual(otree.get_summary, [
            Case(args=(object, ), value=otree.get_summary(object())),
            Case(args=('summary.\n', ), value='summary')])

    def test_call_attr(self) -> None:
        self.assertCaseEqual(otree.call_attr, [
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
        self.assertCaseNotRaises(TypeError, check.has_type, [
            Case(args=('', 0, int)),
            Case(args=('', '', str)),
            Case(args=('', list(), list)),
            Case(args=('', dict(), dict)),
            Case(args=('', object, Callable)),
            Case(args=('', object, Any))])

        self.assertCaseRaises(TypeError, check.has_type, [
            Case(args=('', '', int)),
            Case(args=('', 1., int)),
            Case(args=('', 1, float)),
            Case(args=('', dict(), list)),
            Case(args=('', None, Callable))])

    def test_is_identifier(self) -> None:
        self.assertCaseNotRaises(ValueError, check.is_identifier, [
            Case(args=('', 'id')),
            Case(args=('', 'ID')),
            Case(args=('', 'Table')),
            Case(args=('', 'Table1'))])

        self.assertCaseRaises(ValueError, check.is_identifier, [
            Case(args=('', '')),
            Case(args=('', '1')),
            Case(args=('', 'a b')),
            Case(args=('', 'a.b'))])

    def test_has_opt_type(self) -> None:
        self.assertCaseNotRaises(TypeError, check.has_opt_type, [
            Case(args=('', None, int)),
            Case(args=('', None, str)),
            Case(args=('', list(), list)),
            Case(args=('', dict(), dict))])

        self.assertCaseRaises(TypeError, check.has_opt_type, [
            Case(args=('', '', int)),
            Case(args=('', 1., int)),
            Case(args=('', 1, float)),
            Case(args=('', dict(), list))])

    def test_is_callable(self) -> None:
        self.assertCaseNotRaises(TypeError, check.is_callable, [
            Case(args=('', int)),
            Case(args=('', dict)),
            Case(args=('', list)),
            Case(args=('', str))])

        self.assertCaseRaises(TypeError, check.has_type, [
            Case(args=('', None)),
            Case(args=('', 0)),
            Case(args=('', '')),
            Case(args=('', set()))])

    def test_is_typehint(self) -> None:
        self.assertCaseNotRaises(TypeError, check.is_typehint, [
            Case(args=('', str)),
            Case(args=('', (int, float))),
            Case(args=('', Any)),
            Case(args=('', Callable))])

        self.assertCaseRaises(TypeError, check.is_typehint, [
            Case(args=('', None)),
            Case(args=('', 0)),
            Case(args=('', '')),
            Case(args=('', Union))])

    def test_is_class(self) -> None:
        self.assertCaseNotRaises(TypeError, check.is_class, [
            Case(args=('', int)),
            Case(args=('', dict)),
            Case(args=('', list)),
            Case(args=('', str))])

        self.assertCaseRaises(TypeError, check.is_class, [
            Case(args=('', None)),
            Case(args=('', 0)),
            Case(args=('', '')),
            Case(args=('', set()))])

    def test_is_subclass(self) -> None:
        self.assertCaseNotRaises(TypeError, check.is_subclass, [
            Case(args=('', int, object)),
            Case(args=('', dict, dict)),
            Case(args=('', list, object)),
            Case(args=('', str, str))])

        self.assertCaseRaises(TypeError, check.is_subclass, [
            Case(args=('', int, str)),
            Case(args=('', dict, list)),
            Case(args=('', object, float)),
            Case(args=('', str, complex))])

    def test_is_subset(self) -> None:
        self.assertCaseNotRaises(ValueError, check.is_subset, [
            Case(args=('', set(), '', set())),
            Case(args=('', {1}, '', {1, 2})),
            Case(args=('', {2}, '', {1, 2})),
            Case(args=('', {2, 1}, '', {1, 2}))])

        self.assertCaseRaises(ValueError, check.is_subset, [
            Case(args=('', {1}, '', set())),
            Case(args=('', {2}, '', {1})),
            Case(args=('', {1, 2}, '', {1})),
            Case(args=('', {1, 2, 3}, '', set()))])

    def test_no_dublicates(self) -> None:
        self.assertCaseNotRaises(ValueError, check.no_dublicates, [
            Case(args=('', set())),
            Case(args=('', {1, 1, 2, 3})),
            Case(args=('', [1, 2, 3])),
            Case(args=('', {1: 1, 2: 2}))])

        self.assertCaseRaises(ValueError, check.no_dublicates, [
            Case(args=('', (1, 1))),
            Case(args=('', [1, 2, 2]))])

    def test_is_positive(self) -> None:
        self.assertCaseNotRaises(ValueError, check.is_positive, [
            Case(args=('', 1)),
            Case(args=('', 1.))])

        self.assertCaseRaises(ValueError, check.is_positive, [
            Case(args=('', 0)),
            Case(args=('', -1)),
            Case(args=('', -1.))])

    def test_is_negative(self) -> None:
        self.assertCaseNotRaises(ValueError, check.is_negative, [
            Case(args=('', -1)),
            Case(args=('', -1.))])

        self.assertCaseRaises(ValueError, check.is_negative, [
            Case(args=('', 0)),
            Case(args=('', 1)),
            Case(args=('', 1.))])

    def test_is_not_positive(self) -> None:
        self.assertCaseNotRaises(ValueError, check.is_not_positive, [
            Case(args=('', 0)),
            Case(args=('', -1)),
            Case(args=('', -1.))])

        self.assertCaseRaises(ValueError, check.is_not_positive, [
            Case(args=('', 1)),
            Case(args=('', 1.))])

    def test_is_not_negative(self) -> None:
        self.assertCaseNotRaises(ValueError, check.is_not_negative, [
            Case(args=('', 0)),
            Case(args=('', 1)),
            Case(args=('', 1.))])

        self.assertCaseRaises(ValueError, check.is_not_negative, [
            Case(args=('', -1)),
            Case(args=('', -1.))])

    def test_has_attr(self) -> None:
        self.assertCaseNotRaises(AttributeError, check.has_attr, [
            Case(args=('', 'format')),
            Case(args=(0, 'real')),
            Case(args=(1j, 'imag'))])

        self.assertCaseRaises(AttributeError, check.has_attr, [
            Case(args=(list(), 'keys')),
            Case(args=(0, ''))])

    def test_has_size(self) -> None:
        self.assertCaseNotRaises(ValueError, check.has_size, [
            Case(args=('', set()), kwds={'size': 0}),
            Case(args=('', set()), kwds={'min_size': 0}),
            Case(args=('', tuple([1])), kwds={'max_size': 1}),
            Case(args=('', [1, 2]), kwds={'min_size': 1, 'max_size': 3})])

        self.assertCaseRaises(ValueError, check.has_size, [
            Case(args=('', set()), kwds={'size': 1}),
            Case(args=('', tuple()), kwds={'min_size': 1}),
            Case(args=('', set([1])), kwds={'max_size': 0}),
            Case(args=('', [1, 2]), kwds={'min_size': 3, 'max_size': 5})])

    def test_not_empty(self) -> None:
        self.assertCaseNotRaises(ValueError, check.not_empty, [
            Case(args=('', 'x')),
            Case(args=('', {1})),
            Case(args=('', [1])),
            Case(args=('', {1: 1}))])

        self.assertCaseRaises(ValueError, check.not_empty, [
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
        self.assertCaseTrue(env.get_var, cases)

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
        self.assertCaseEqual(literal.as_path, [
            Case(args=('a/b/c', ), value=Path('a/b/c')),
            Case(args=('%cwd%/test', ), value=Path.cwd() / 'test'),
            Case(args=('%home%/test', ), value=Path.home() / 'test')])

    def test_as_datetime(self) -> None:
        val = datetime.datetime.now()
        self.assertEqual(literal.as_datetime(str(val)), val)

    def test_as_list(self) -> None:
        self.assertCaseEqual(literal.as_list, [
            Case(args=('a, 2, ()', ), value=['a', '2', '()']),
            Case(args=('[1, 2, 3]', ), value=[1, 2, 3])])

    def test_as_tuple(self) -> None:
        self.assertCaseEqual(literal.as_tuple, [
            Case(args=('a, 2, ()', ), value=('a', '2', '()')),
            Case(args=('(1, 2, 3)', ), value=(1, 2, 3))])

    def test_as_set(self) -> None:
        self.assertCaseEqual(literal.as_set, [
            Case(args=('a, 2, ()', ), value={'a', '2', '()'}),
            Case(args=('{1, 2, 3}', ), value={1, 2, 3})])

    def test_as_dict(self) -> None:
        self.assertCaseEqual(literal.as_dict, [
            Case(args=("a = 'b', b = 1", ), value={'a': 'b', 'b': 1}),
            Case(args=("'a': 'b', 'b': 1", ), value={'a': 'b', 'b': 1})])

    def test_decode(self) -> None:
        self.assertCaseEqual(literal.decode, [
            Case(args=('text', str), value='text'),
            Case(args=(repr(True), bool), value=True),
            Case(args=(repr(1), int), value=1),
            Case(args=(repr(.5), float), value=.5),
            Case(args=(repr(1+1j), complex), value=1+1j)])

    def test_from_str(self) -> None:
        self.assertCaseEqual(literal.from_str, [
            Case(args=(chr(1) + 'a', 'printable'), value='a'),
            Case(args=('a, b', 'uax-31'), value='ab'),
            Case(args=('max(x)', 'uax-31'),
                kwds={'spacer': '_'}, value='max_x_')])

    def test_encode(self) -> None:
        self.assertCaseEqual(literal.encode, [
            Case(args=(chr(1) + 'a', ),
                kwds={'charset': 'printable'}, value='a'),
            Case(args=('a, b', ),
                kwds={'charset': 'uax-31'}, value='ab')])

    def test_estimate(self) -> None:
        Date = datetime.datetime
        self.assertCaseEqual(literal.estimate, [
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
