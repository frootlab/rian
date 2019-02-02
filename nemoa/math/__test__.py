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
"""Unittests for submodules of package 'nemoa.math'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import networkx as nx
import numpy as np
from typing import Any
from unittest import mock
from nemoa import errors
from nemoa.math import curve, graph, matrix, operator, regression
from nemoa.math import vector
from nemoa.types import AnyOp
from nemoa.test import ModuleTestCase, MathTestCase

class TestCurve(MathTestCase, ModuleTestCase):
    module = curve

    def setUp(self) -> None:
        self.x = np.array([[0.0, 0.5], [1.0, -1.0]])

    def test_Curve(self) -> None:
        pass # Testing is not required for Catalog Categories

    def test_Bell(self) -> None:
        pass # Testing is not required for Catalog Categories

    def test_SoftStep(self) -> None:
        pass # Testing is not required for Catalog Categories

    def test_Sigmoid(self) -> None:
        pass # Testing is not required for Catalog Categories

    def test_sigmoids(self) -> None:
        funcs = curve.sigmoids()
        self.assertIsInstance(funcs, list)
        self.assertTrue(funcs)

    def test_sigmoid(self) -> None:
        for func in curve.sigmoids():
            with self.subTest(name=func):
                self.assertIsSigmoid(curve.sigmoid, name=func)

    def test_logistic(self) -> None:
        self.assertIsSigmoid(curve.logistic)
        self.assertCheckSum(curve.logistic, self.x, 2.122459)

    def test_tanh(self) -> None:
        self.assertIsSigmoid(curve.tanh)
        self.assertCheckSum(curve.tanh, self.x, 0.462117)

    def test_tanh_lecun(self) -> None:
        self.assertIsSigmoid(curve.tanh_lecun)
        self.assertCheckSum(curve.tanh_lecun, self.x, 0.551632)

    def test_elliot(self) -> None:
        self.assertIsSigmoid(curve.elliot)
        self.assertCheckSum(curve.elliot, self.x, 0.333333)

    def test_hill(self) -> None:
        self.assertCheckSum(curve.hill, self.x, 0.447213)
        for n in range(2, 10, 2):
            with self.subTest(n=n):
                self.assertIsSigmoid(curve.hill, n=n)

    def test_arctan(self) -> None:
        self.assertIsSigmoid(curve.arctan)
        self.assertCheckSum(curve.arctan, self.x, 0.463647)

    def test_bells(self) -> None:
        funcs = curve.bells()
        self.assertIsInstance(funcs, list)
        self.assertTrue(funcs)

    def test_bell(self) -> None:
        for name in curve.bells():
            with self.subTest(name=name):
                self.assertIsBell(curve.bell, name=name)

    def test_gauss(self) -> None:
        self.assertIsBell(curve.gauss)
        self.assertCheckSum(curve.gauss, self.x, 1.234949)

    def test_dlogistic(self) -> None:
        self.assertIsBell(curve.dlogistic)
        self.assertCheckSum(curve.dlogistic, self.x, 0.878227)

    def test_delliot(self) -> None:
        self.assertIsBell(curve.delliot)
        self.assertCheckSum(curve.delliot, self.x, 1.944444)

    def test_dhill(self) -> None:
        self.assertIsBell(curve.dhill)
        self.assertCheckSum(curve.dhill, self.x, 2.422648)

    def test_dtanh_lecun(self) -> None:
        self.assertIsBell(curve.dtanh_lecun)
        self.assertCheckSum(curve.dtanh_lecun, self.x, 3.680217)

    def test_dtanh(self) -> None:
        self.assertIsBell(curve.dtanh)
        self.assertCheckSum(curve.dtanh, self.x, 2.626396)

    def test_darctan(self) -> None:
        self.assertIsBell(curve.darctan)
        self.assertCheckSum(curve.darctan, self.x, 2.800000)

    def test_dialogistic(self) -> None:
        self.assertIncreasing(curve.dialogistic)
        self.assertCheckSum(curve.dialogistic, self.x, 0.251661)

    def test_softstep(self) -> None:
        self.assertIncreasing(curve.softstep)
        self.assertCheckSum(curve.softstep, self.x, 0.323637)

    def test_multi_logistic(self) -> None:
        self.assertIncreasing(curve.multi_logistic)
        self.assertCheckSum(curve.multi_logistic, self.x, 0.500091)

class TestVector(MathTestCase, ModuleTestCase):
    module = vector

    def test_Norm(self) -> None:
        pass # Data Class

    def test_Distance(self) -> None:
        pass # Data Class

    def test_norms(self) -> None:
        norms = vector.norms()
        self.assertIsInstance(norms, list)
        self.assertTrue(norms)

    def test_length(self) -> None:
        for norm in vector.norms():
            with self.subTest(norm=norm):
                self.assertIsVectorNorm(vector.length, norm=norm)

    def test_p_norm(self) -> None:
        for p in range(1, 5):
            with self.subTest(p=p):
                self.assertIsVectorNorm(vector.p_norm, p=p)

    def test_norm_1(self) -> None:
        self.assertIsVectorNorm(vector.norm_1)

    def test_euclid_norm(self) -> None:
        self.assertIsVectorNorm(vector.euclid_norm)

    def test_max_norm(self) -> None:
        self.assertIsVectorNorm(vector.max_norm)

    def test_pmean_norm(self) -> None:
        for p in range(1, 5):
            with self.subTest(p=p):
                self.assertIsVectorNorm(vector.pmean_norm, p=p)

    def test_amean_norm(self) -> None:
        self.assertIsVectorNorm(vector.amean_norm)

    def test_qmean_norm(self) -> None:
        self.assertIsVectorNorm(vector.qmean_norm)

    def test_distances(self) -> None:
        distances = vector.distances()
        self.assertIsInstance(distances, list)
        self.assertTrue(distances)

    def test_distance(self) -> None:
        for name in vector.distances():
            with self.subTest(name=name):
                self.assertIsVectorDistance(vector.distance, name=name)

    def test_chebyshev(self) -> None:
        self.assertIsVectorDistance(vector.chebyshev)

    def test_manhattan(self) -> None:
        self.assertIsVectorDistance(vector.manhattan)

    def test_minkowski(self) -> None:
        self.assertIsVectorDistance(vector.minkowski)

    def test_amean_dist(self) -> None:
        self.assertIsVectorDistance(vector.amean_dist)

    def test_qmean_dist(self) -> None:
        self.assertIsVectorDistance(vector.qmean_dist)

    def test_pmean_dist(self) -> None:
        for p in range(1, 5):
            with self.subTest(p=p):
                self.assertIsVectorDistance(vector.pmean_dist, p=p)

    def test_euclid_dist(self) -> None:
        self.assertIsVectorDistance(vector.euclid_dist)

class TestMatrix(MathTestCase, ModuleTestCase):
    module = matrix

    def test_Norm(self) -> None:
        pass # Not required

    def test_Distance(self) -> None:
        pass # Not required

    def test_norms(self) -> None:
        norms = matrix.norms()
        self.assertIsInstance(norms, list)
        self.assertTrue(norms)

    def test_norm(self) -> None:
        for name in matrix.norms():
            with self.subTest(name=name):
                self.assertIsMatrixNorm(matrix.norm, name=name)

    def test_frob_norm(self) -> None:
        self.assertIsMatrixNorm(matrix.frob_norm)

    def test_pq_norm(self) -> None:
        for p in range(1, 5):
            for q in range(1, 5):
                with self.subTest(p=p, q=q):
                    self.assertIsMatrixNorm(matrix.pq_norm, p=p, q=q)

    def test_distances(self) -> None:
        distances = matrix.distances()
        self.assertIsInstance(distances, list)
        self.assertTrue(distances)

    def test_distance(self) -> None:
        for name in matrix.distances():
            with self.subTest(name=name):
                self.assertIsMatrixDistance(matrix.distance, name=name)

    def test_frob_dist(self) -> None:
        self.assertIsMatrixDistance(matrix.frob_dist)

    def test_pq_dist(self) -> None:
        for p in range(1, 5):
            for q in range(1, 5):
                with self.subTest(p=p, q=q):
                    self.assertIsMatrixDistance(matrix.pq_dist, p=p, q=q)

class TestOperator(ModuleTestCase):
    module = operator

    def test_Variable(self) -> None:
        pass # Implicitly tested by test_create_variable()

    def test_create_variable(self) -> None:
        create = operator.create_variable

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

    def test_Operator(self) -> None:
        pass # Already tested within subclasses

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
                errors.NoSubsetError, create, '{x}**2 + y', variables=('{x}', ))

        with self.subTest(args=('{x}**2 + y', ), variables=('{x}', 'y')):
            op = create('{x}**2 + y', variables=('{x}', 'y'))
            self.assertIsInstance(op, operator.Lambda)
            self.assertRaises(TypeError, op, 1)
            self.assertEqual(int(op(2, -4)), 0)

        with self.subTest(
                args=('{x}**2 + y', ), variables=('{x}', 'y'),
                domain=(None, ('{x}', '{y}'))):
            self.assertRaises(
                errors.NoSubsetError, create, '{x}**2 + y', variables=('{x}', ),
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

    def test_create_setter(self) -> Any:
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

class TestRegr(MathTestCase, ModuleTestCase):
    module = regression

    def test_Error(self) -> None:
        pass # Not required to test

    def test_errors(self) -> None:
        errors = regression.errors()
        self.assertIsInstance(errors, list)
        self.assertTrue(errors)

    def test_error(self) -> None:
        for name in regression.errors():
            with self.subTest(name=name):
                self.assertIsSemiMetric(regression.error, name=name)

    def test_sad(self) -> None:
        self.assertIsSemiMetric(regression.sad)

    def test_rss(self) -> None:
        self.assertIsSemiMetric(regression.rss)

    def test_mae(self) -> None:
        self.assertIsSemiMetric(regression.mae)

    def test_mse(self) -> None:
        self.assertIsSemiMetric(regression.mse)

    def test_rmse(self) -> None:
        self.assertIsSemiMetric(regression.rmse)

class TestGraph(ModuleTestCase):
    """Testsuite for modules within the package 'nemoa.math.graph'."""

    def setUp(self) -> None:
        self.G = nx.DiGraph([(1, 3), (1, 4), (2, 3), (2, 4)], directed=True)
        nx.set_node_attributes(self.G, {
            1: {'layer': 'i', 'layer_id': 0, 'layer_sub_id': 0},
            2: {'layer': 'i', 'layer_id': 0, 'layer_sub_id': 1},
            3: {'layer': 'o', 'layer_id': 1, 'layer_sub_id': 0},
            4: {'layer': 'o', 'layer_id': 1, 'layer_sub_id': 1}})
        nx.set_edge_attributes(self.G, {
            (1, 3): {'weight': 0.1}, (1, 4): {'weight': 0.9},
            (2, 3): {'weight': 0.9}, (2, 4): {'weight': 0.1}})

    def test_is_directed(self) -> None:
        self.assertTrue(graph.is_directed(self.G))

    def test_is_layered(self) -> None:
        self.assertTrue(graph.is_layered(self.G))

    def test_get_layers(self) -> None:
        layers = graph.get_layers(self.G)
        self.assertEqual(layers, [[1, 2], [3, 4]])

    def test_get_groups(self) -> None:
        groups = graph.get_groups(self.G, attribute='layer')
        self.assertEqual(groups, {'': [], 'i': [1, 2], 'o': [3, 4]})
