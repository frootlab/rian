# -*- coding: utf-8 -*-
"""Unittests for submodules of package 'nemoa.math'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import networkx as nx
import numpy as np
from nemoa.math import curve, graph, matrix, meta, regression, vector
from nemoa.test import ModuleTestCase, MathTestCase
from nemoa.types import NaN

class TestAlgo(ModuleTestCase):
    """Testcase for the module nemoa.math.meta."""

    module = 'nemoa.math.meta'

    def test_search(self) -> None:
        self.assertEqual(
            len(meta.search(meta, name='search')), 1)

    def test_custom(self) -> None:
        @meta.custom(category='custom')
        def test_custom() -> None:
            pass
        self.assertEqual(
            getattr(test_custom, 'name', None), 'test_custom')
        self.assertEqual(
            getattr(test_custom, 'category', None), 'custom')

    def test_objective(self) -> None:
        @meta.objective()
        def test_objective() -> None:
            pass
        self.assertEqual(
            getattr(test_objective, 'name', None), 'test_objective')
        self.assertEqual(
            getattr(test_objective, 'category', None), 'objective')

    def test_sampler(self) -> None:
        @meta.sampler()
        def test_sampler() -> None:
            pass
        self.assertEqual(
            getattr(test_sampler, 'name', None), 'test_sampler')
        self.assertEqual(
            getattr(test_sampler, 'category', None), 'sampler')

    def test_statistic(self) -> None:
        @meta.statistic()
        def test_statistic() -> None:
            pass
        self.assertEqual(
            getattr(test_statistic, 'name', None), 'test_statistic')
        self.assertEqual(
            getattr(test_statistic, 'category', None), 'statistic')

    def test_association(self) -> None:
        @meta.association()
        def test_association() -> None:
            pass
        self.assertEqual(
            getattr(test_association, 'name', None), 'test_association')
        self.assertEqual(
            getattr(test_association, 'category', None), 'association')

class TestCurve(MathTestCase, ModuleTestCase):
    """Testcase for the module nemoa.math.curve."""

    module = 'nemoa.math.curve'

    def setUp(self) -> None:
        self.x = np.array([[0.0, 0.5], [1.0, -1.0]])

    def test_sigmoids(self) -> None:
        funcs = curve.sigmoids()
        self.assertIsInstance(funcs, list)
        self.assertTrue(funcs)

    def test_sigmoid(self) -> None:
        for func in curve.sigmoids():
            with self.subTest(name=func):
                self.assertIsSigmoid(curve.sigmoid, name=func)

    def test_sigm_logistic(self) -> None:
        self.assertIsSigmoid(curve.sigm_logistic)
        self.assertCheckSum(curve.sigm_logistic, self.x, 2.122459)

    def test_sigm_tanh(self) -> None:
        self.assertIsSigmoid(curve.sigm_tanh)
        self.assertCheckSum(curve.sigm_tanh, self.x, 0.462117)

    def test_sigm_lecun(self) -> None:
        self.assertIsSigmoid(curve.sigm_lecun)
        self.assertCheckSum(curve.sigm_lecun, self.x, 0.551632)

    def test_sigm_elliot(self) -> None:
        self.assertIsSigmoid(curve.sigm_elliot)
        self.assertCheckSum(curve.sigm_elliot, self.x, 0.333333)

    def test_sigm_hill(self) -> None:
        self.assertCheckSum(curve.sigm_hill, self.x, 0.447213)
        for n in range(2, 10, 2):
            with self.subTest(n=n):
                self.assertIsSigmoid(curve.sigm_hill, n=n)

    def test_sigm_arctan(self) -> None:
        self.assertIsSigmoid(curve.sigm_arctan)
        self.assertCheckSum(curve.sigm_arctan, self.x, 0.463647)

    def test_bells(self) -> None:
        funcs = curve.bells()
        self.assertIsInstance(funcs, list)
        self.assertTrue(funcs)

    def test_bell(self) -> None:
        for func in curve.bells():
            with self.subTest(name=func):
                self.assertIsBell(curve.bell, name=func)

    def test_bell_gauss(self) -> None:
        self.assertIsBell(curve.bell_gauss)
        self.assertCheckSum(curve.bell_gauss, self.x, 1.234949)

    def test_bell_d_logistic(self) -> None:
        self.assertIsBell(curve.bell_d_logistic)
        self.assertCheckSum(curve.bell_d_logistic, self.x, 0.878227)

    def test_bell_d_elliot(self) -> None:
        self.assertIsBell(curve.bell_d_elliot)
        self.assertCheckSum(curve.bell_d_elliot, self.x, 1.944444)

    def test_bell_d_hill(self) -> None:
        self.assertIsBell(curve.bell_d_hill)
        self.assertCheckSum(curve.bell_d_hill, self.x, 2.422648)

    def test_bell_d_lecun(self) -> None:
        self.assertIsBell(curve.bell_d_lecun)
        self.assertCheckSum(curve.bell_d_lecun, self.x, 3.680217)

    def test_bell_d_tanh(self) -> None:
        self.assertIsBell(curve.bell_d_tanh)
        self.assertCheckSum(curve.bell_d_tanh, self.x, 2.626396)

    def test_bell_d_arctan(self) -> None:
        self.assertIsBell(curve.bell_d_arctan)
        self.assertCheckSum(curve.bell_d_arctan, self.x, 2.800000)

    def test_dialogistic(self) -> None:
        self.assertIncreasing(curve.dialogistic)
        self.assertCheckSum(curve.dialogistic, self.x, 0.251661)

    def test_softstep(self) -> None:
        self.assertIncreasing(curve.softstep)
        self.assertCheckSum(curve.softstep, self.x, 0.323637)

    def test_multilogistic(self) -> None:
        self.assertIncreasing(curve.multilogistic)
        self.assertCheckSum(curve.multilogistic, self.x, 0.500091)

class TestVector(MathTestCase, ModuleTestCase):
    """Testcase for the module nemoa.math.vector."""

    module = 'nemoa.math.vector'

    def test_norms(self) -> None:
        norms = vector.norms()
        self.assertIsInstance(norms, list)
        self.assertTrue(norms)

    def test_length(self) -> None:
        for norm in vector.norms():
            with self.subTest(norm=norm):
                self.assertIsVectorNorm(vector.length, norm=norm)

    def test_norm_p(self) -> None:
        for p in range(1, 5):
            with self.subTest(p=p):
                self.assertIsVectorNorm(vector.norm_p, p=p)

    def test_norm_1(self) -> None:
        self.assertIsVectorNorm(vector.norm_1)

    def test_norm_euclid(self) -> None:
        self.assertIsVectorNorm(vector.norm_euclid)

    def test_norm_max(self) -> None:
        self.assertIsVectorNorm(vector.norm_max)

    def test_norm_pmean(self) -> None:
        for p in range(1, 5):
            with self.subTest(p=p):
                self.assertIsVectorNorm(vector.norm_pmean, p=p)

    def test_norm_amean(self) -> None:
        self.assertIsVectorNorm(vector.norm_amean)

    def test_norm_qmean(self) -> None:
        self.assertIsVectorNorm(vector.norm_qmean)

    def test_distances(self) -> None:
        distances = vector.distances()
        self.assertIsInstance(distances, list)
        self.assertTrue(distances)

    def test_distance(self) -> None:
        for name in vector.distances():
            with self.subTest(name=name):
                self.assertIsVectorDistance(vector.distance, name=name)

    def test_dist_chebyshev(self) -> None:
        self.assertIsVectorDistance(vector.dist_chebyshev)

    def test_dist_manhattan(self) -> None:
        self.assertIsVectorDistance(vector.dist_manhattan)

    def test_dist_minkowski(self) -> None:
        self.assertIsVectorDistance(vector.dist_minkowski)

    def test_dist_amean(self) -> None:
        self.assertIsVectorDistance(vector.dist_amean)

    def test_dist_qmean(self) -> None:
        self.assertIsVectorDistance(vector.dist_qmean)

    def test_dist_pmean(self) -> None:
        for p in range(1, 5):
            with self.subTest(p=p):
                self.assertIsVectorDistance(vector.dist_pmean, p=p)

    def test_dist_euclid(self) -> None:
        self.assertIsVectorDistance(vector.dist_euclid)

class TestMatrix(MathTestCase, ModuleTestCase):
    """Testcase for the module nemoa.math.matrix."""

    module = 'nemoa.math.matrix'

    def setUp(self) -> None:
        self.x = np.array([[NaN, 1.], [NaN, NaN]])
        self.d = {('a', 'b'): 1.}
        self.labels = (['a', 'b'], ['a', 'b'])

    def test_from_dict(self) -> None:
        x = matrix.from_dict(self.d, labels=self.labels)
        self.assertTrue(np.allclose(x, self.x, equal_nan=True))

    def test_as_dict(self) -> None:
        d = matrix.as_dict(self.x, labels=self.labels)
        self.assertEqual(d, self.d)

    def test_norms(self) -> None:
        norms = matrix.norms()
        self.assertIsInstance(norms, list)
        self.assertTrue(norms)

    def test_norm(self) -> None:
        for name in matrix.norms():
            with self.subTest(name=name):
                self.assertIsMatrixNorm(matrix.norm, name=name)

    def test_norm_frobenius(self) -> None:
        self.assertIsMatrixNorm(matrix.norm_frobenius)

    def test_norm_pq(self) -> None:
        for p in range(1, 5):
            for q in range(1, 5):
                with self.subTest(p=p, q=q):
                    self.assertIsMatrixNorm(matrix.norm_pq, p=p, q=q)

    def test_distances(self) -> None:
        distances = matrix.distances()
        self.assertIsInstance(distances, list)
        self.assertTrue(distances)

    def test_distance(self) -> None:
        for name in matrix.distances():
            with self.subTest(name=name):
                self.assertIsMatrixDistance(matrix.distance, name=name)

    def test_dist_frobenius(self) -> None:
        self.assertIsMatrixDistance(matrix.dist_frobenius)

    def test_dist_pq(self) -> None:
        for p in range(1, 5):
            for q in range(1, 5):
                with self.subTest(p=p, q=q):
                    self.assertIsMatrixDistance(matrix.dist_pq, p=p, q=q)

class TestRegr(MathTestCase, ModuleTestCase):
    """Testcase for the module nemoa.math.regression."""

    module = 'nemoa.math.regression'

    def test_errors(self) -> None:
        errors = regression.errors()
        self.assertIsInstance(errors, list)
        self.assertTrue(errors)

    def test_error(self) -> None:
        for name in regression.errors():
            with self.subTest(name=name):
                self.assertIsSemiMetric(regression.error, name=name)

    def test_error_sad(self) -> None:
        self.assertIsSemiMetric(regression.error_sad)

    def test_error_rss(self) -> None:
        self.assertIsSemiMetric(regression.error_rss)

    def test_error_mae(self) -> None:
        self.assertIsSemiMetric(regression.error_mae)

    def test_error_mse(self) -> None:
        self.assertIsSemiMetric(regression.error_mse)

    def test_error_rmse(self) -> None:
        self.assertIsSemiMetric(regression.error_rmse)

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
        self.pos1 = {1: (.0, .25), 2: (.0, .75), 4: (1., .25), 3: (1., .75)}
        self.pos2 = {1: (.25, 1.), 2: (.75, 1.), 4: (.25, .0), 3: (.75, .0)}
        self.pos3 = {1: (4., 2.), 2: (4., 16.), 4: (32., 2.), 3: (32., 16.)}

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

    def test_get_layer_layout(self) -> None:
        layout = graph.get_layer_layout(self.G, direction='right')
        self.assertEqual(layout, self.pos1)
        layout = graph.get_layer_layout(self.G, direction='down')
        self.assertEqual(layout, self.pos2)

    def test_rescale_layout(self) -> None:
        layout = graph.rescale_layout(
            self.pos1, size=(40, 20), padding=(.2, .2, .1, .1))
        self.assertEqual(layout, self.pos3)

    def test_get_scaling_factor(self) -> None:
        scaling = int(graph.get_scaling_factor(self.pos3))
        self.assertEqual(scaling, 9)

    def test_get_layout_normsize(self) -> None:
        normsize = graph.get_layout_normsize(self.pos3)
        self.assertEqual(int(normsize['node_size']), 4)

    def test_get_node_layout(self) -> None:
        color = graph.get_node_layout('observable')['color']
        self.assertIsInstance(color, str)

    def test_get_layout(self) -> None:
        layout = graph.get_layout(self.G, 'layer', direction='right')
        self.assertEqual(layout, self.pos1)
