# -*- coding: utf-8 -*-
"""Unittests for submodules of package 'nemoa.math'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import networkx as nx
import numpy as np

from nemoa.math import algo, curve, graph, matrix, regr, vector
from nemoa.test import GenericTestCase, ModuleTestCase
from nemoa.types import Any, Callable, NpArray, NaN

class MathTestCase(GenericTestCase):
    """Additional asserts for math tests."""

    def assertCheckSum(self, func: Callable, x: NpArray, val: float) -> None:
        vsum = func(x).sum()
        self.assertTrue(np.isclose(vsum, val, atol=1e-4))

    def assertNotNegative(self, f: Callable, **kwds: Any) -> None:
        x = 5. * np.random.rand(3, 3, 3) - 5.
        self.assertTrue(np.all(f(x, **kwds) >= 0.),
            f"function '{f.__name__}' contains negative target values")

    def assertNotPositive(self, f: Callable, **kwds: Any) -> None:
        x = 5. * np.random.rand(3, 3, 3) - 5.
        self.assertTrue(np.all(f(x, **kwds) <= 0.),
            f"function '{f.__name__}' contains positive target values")

    def assertIncreasing(self, f: Callable, **kwds: Any) -> None:
        x = np.linspace(-10., 10., num=20)
        self.assertTrue(np.all(np.diff(f(x, **kwds)) >= 0.),
            f"function '{f.__name__}' is not monotonically increasing")

    def assertDecreasing(self, f: Callable, **kwds: Any) -> None:
        x = np.linspace(-10., 10., num=20)
        self.assertTrue(np.all(np.diff(f(x, **kwds)) <= 0.),
            f"function '{f.__name__}' is not monotonically decreasing")

    def assertSingleExtremalPoint(self, f: Callable, **kwds: Any) -> None:
        x = np.linspace(-10., 10., num=20)
        s = np.sign(np.diff(f(x, **kwds)))
        d_s = np.diff(s[s[:] != 0.])
        count = d_s[d_s[:] != 0.].size
        self.assertTrue(count == 1,
            f"function '{f.__name__}' has {count} extremal points")

    def assertSingleInflectionPoint(self, f: Callable, **kwds: Any) -> None:
        x = np.linspace(-10., 10., num=20)
        s = np.sign(np.diff(np.diff(f(x, **kwds))))
        d_s = np.diff(s[s[:] != 0.])
        count = d_s[d_s[:] != 0.].size
        self.assertTrue(count == 1,
            f"function '{f.__name__}' has {count} inflection points")

    def assertIsSigmoid(self, f: Callable, **kwds: Any) -> None:
        # Test monotonicity
        self.assertIncreasing(f, **kwds)
        # Test number of inflection points
        self.assertSingleInflectionPoint(f, **kwds)

    def assertIsBell(self, f: Callable, **kwds: Any) -> None:
        # Test that bell function is not negative
        self.assertNotNegative(f, **kwds)
        # Test number of extremal points
        self.assertSingleExtremalPoint(f, **kwds)

    def assertCoDim(self, f: Callable, codim: int = 0, **kwds: Any) -> None:
        x = np.zeros((3, 3, 3))
        self.assertEqual(x.ndim - f(x, **kwds).ndim, codim)

    def assertConserveZero(self, f: Callable, **kwds: Any) -> None:
        x = np.zeros((3, 3, 3))
        self.assertTrue(np.allclose(f(x, **kwds), 0.))

    def assertSubadditivity(self, f: Callable, **kwds: Any) -> None:
        x = 5. * np.random.rand(3, 3, 3) - 5.
        y = 5. * np.random.rand(3, 3, 3) - 5.
        f_x, f_y = f(x, **kwds), f(y, **kwds)
        f_xy = f(x + y, **kwds)
        self.assertTrue(np.all(f_xy < f_x + f_y + 1e-05))

    def assertAbsoluteHomogeneity(self, f: Callable, **kwds: Any) -> None:
        x = 5. * np.random.rand(3, 3, 3) - 5.
        f_x = f(x, **kwds)
        for alpha in np.linspace(0., 10., num=5):
            f_ax = f(alpha * x, **kwds)
            self.assertTrue(np.allclose(f_ax, float(alpha) * f_x))

    def assertIsNorm(self, f: Callable, **kwds: Any) -> None:
        # Test if norm is negative
        self.assertNotNegative(f, **kwds)
        # Test if norm of zero value is zero
        self.assertConserveZero(f, **kwds)
        # Test subadditivity
        self.assertSubadditivity(f, **kwds)
        # Test absolute homogeneity
        self.assertAbsoluteHomogeneity(f, **kwds)

    def assertIsVectorNorm(self, f: Callable, **kwds: Any) -> None:
        # Test codimension of function
        self.assertCoDim(f, codim=1, **kwds)
        # Test if function is norm
        self.assertIsNorm(f, **kwds)

    def assertIsMatrixNorm(self, f: Callable, **kwds: Any) -> None:
        # Test codimension of function
        self.assertCoDim(f, codim=2, **kwds)
        # Test if function is norm
        self.assertIsNorm(f, **kwds)

    #
    # Binary Functions
    #

    def assertBiNotNegative(self, f: Callable, **kwds: Any) -> None:
        x = 5. * np.random.rand(3, 3, 3) - 5.
        y = 5. * np.random.rand(3, 3, 3) - 5.
        self.assertTrue(np.all(f(x, y, **kwds) >= 0.),
            f"function '{f.__name__}' contains negative target values")

    def assertBinFuncCoDim(
            self, f: Callable, codim: int = 0, **kwds: Any) -> None:
        x = np.zeros((3, 3, 3))
        self.assertEqual(x.ndim - f(x, x, **kwds).ndim, codim)

    def assertTriangleInequality(self, f: Callable, **kwds: Any) -> None:
        x = 5. * np.random.rand(3, 3, 3) - 5.
        y = 5. * np.random.rand(3, 3, 3) - 5.
        z = 5. * np.random.rand(3, 3, 3) - 5.
        f_xy = f(x, y, **kwds)
        f_yz = f(y, z, **kwds)
        f_xz = f(x, z, **kwds)
        self.assertTrue(np.all(f_xz < f_xy + f_yz + 1e-05))

    def assertSymmetric(self, f: Callable, **kwds: Any) -> None:
        x = 5. * np.random.rand(3, 3, 3) - 5.
        y = 5. * np.random.rand(3, 3, 3) - 5.
        f_xy, f_yx = f(x, y, **kwds), f(y, x, **kwds)
        self.assertTrue(np.allclose(f_xy, f_yx),
            f"function '{f.__name__}' is not symmetric")

    def assertIndiscernibilityOfIdenticals(
            self, f: Callable, **kwds: Any) -> None:
        x = 5. * np.random.rand(3, 3, 3) - 5.
        f_xx = f(x, x, **kwds)
        self.assertTrue(np.allclose(f_xx, 0.))

    def assertIsSemiMetric(self, f: Callable, **kwds: Any) -> None:
        # Test if function is not negative
        self.assertBiNotNegative(f, **kwds)
        # Test indiscernibility of identicals
        self.assertIndiscernibilityOfIdenticals(f, **kwds)
        # Test if function is symmetric
        self.assertSymmetric(f, **kwds)

    def assertIsMetric(self, f: Callable, **kwds: Any) -> None:
        # Test if function is semi metric
        self.assertIsSemiMetric(f, **kwds)
        # Test triangle inequality
        self.assertTriangleInequality(f, **kwds)

    def assertIsVectorMetric(self, f: Callable, **kwds: Any) -> None:
        # Test of codimension of function is 1
        self.assertBinFuncCoDim(f, codim=1, **kwds)
        # Test if function is metric
        self.assertIsMetric(f, **kwds)

    def assertIsMatrixMetric(self, f: Callable, **kwds: Any) -> None:
        # Test of codimension of function is 2
        self.assertBinFuncCoDim(f, codim=2, **kwds)
        # Test if function is metric
        self.assertIsMetric(f, **kwds)

class TestAlgo(ModuleTestCase):
    """Testcase for the module nemoa.math.algo."""

    module = 'nemoa.math.algo'

    def test_search(self) -> None:
        self.assertEqual(
            len(algo.search(algo, name='search')), 1)

    def test_custom(self) -> None:
        @algo.custom(category='custom')
        def test_custom() -> None:
            pass
        self.assertEqual(
            getattr(test_custom, 'name', None), 'test_custom')
        self.assertEqual(
            getattr(test_custom, 'category', None), 'custom')

    def test_objective(self) -> None:
        @algo.objective()
        def test_objective() -> None:
            pass
        self.assertEqual(
            getattr(test_objective, 'name', None), 'test_objective')
        self.assertEqual(
            getattr(test_objective, 'category', None), 'objective')

    def test_sampler(self) -> None:
        @algo.sampler()
        def test_sampler() -> None:
            pass
        self.assertEqual(
            getattr(test_sampler, 'name', None), 'test_sampler')
        self.assertEqual(
            getattr(test_sampler, 'category', None), 'sampler')

    def test_statistic(self) -> None:
        @algo.statistic()
        def test_statistic() -> None:
            pass
        self.assertEqual(
            getattr(test_statistic, 'name', None), 'test_statistic')
        self.assertEqual(
            getattr(test_statistic, 'category', None), 'statistic')

    def test_association(self) -> None:
        @algo.association()
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
        for p in range(1, 10):
            with self.subTest(p=p):
                self.assertIsVectorNorm(vector.norm_p, p=p)

    def test_norm_1(self) -> None:
        self.assertIsVectorNorm(vector.norm_1)

    def test_norm_euclid(self) -> None:
        self.assertIsVectorNorm(vector.norm_euclid)

    def test_norm_max(self) -> None:
        self.assertIsVectorNorm(vector.norm_max)

    def test_norm_pmean(self) -> None:
        for p in range(1, 10):
            with self.subTest(p=p):
                self.assertIsVectorNorm(vector.norm_pmean, p=p)

    def test_norm_amean(self) -> None:
        self.assertIsVectorNorm(vector.norm_amean)

    def test_norm_qmean(self) -> None:
        self.assertIsVectorNorm(vector.norm_qmean)

    def test_norm_sd(self) -> None:
        self.assertIsVectorNorm(vector.norm_sd)

    def test_metrices(self) -> None:
        metrices = vector.metrices()
        self.assertIsInstance(metrices, list)
        self.assertTrue(metrices)

    def test_distance(self) -> None:
        for metric in vector.metrices():
            with self.subTest(metric=metric):
                self.assertIsVectorMetric(vector.distance, metric=metric)

    def test_dist_chebyshev(self) -> None:
        self.assertIsVectorMetric(vector.dist_chebyshev)

    def test_dist_manhatten(self) -> None:
        self.assertIsVectorMetric(vector.dist_manhatten)

    def test_dist_minkowski(self) -> None:
        self.assertIsVectorMetric(vector.dist_minkowski)

    def test_dist_amean(self) -> None:
        self.assertIsVectorMetric(vector.dist_amean)

    def test_dist_qmean(self) -> None:
        self.assertIsVectorMetric(vector.dist_qmean)

    def test_dist_pmean(self) -> None:
        for p in range(1, 10):
            with self.subTest(p=p):
                self.assertIsVectorMetric(vector.dist_pmean, p=p)

    def test_dist_euclid(self) -> None:
        self.assertIsVectorMetric(vector.dist_euclid)

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
        for p in range(1, 10):
            for q in range(1, 10):
                with self.subTest(p=p, q=q):
                    self.assertIsMatrixNorm(matrix.norm_pq, p=p, q=q)

    def test_metrices(self) -> None:
        metrices = matrix.metrices()
        self.assertIsInstance(metrices, list)
        self.assertTrue(metrices)

    def test_distance(self) -> None:
        for metric in matrix.metrices():
            with self.subTest(metric=metric):
                self.assertIsMatrixMetric(matrix.distance, metric=metric)

    def test_dist_frobenius(self) -> None:
        self.assertIsMatrixMetric(matrix.dist_frobenius)

class TestRegr(MathTestCase, ModuleTestCase):
    """Testcase for the module nemoa.math.regr."""

    module = 'nemoa.math.regr'

    def test_errors(self) -> None:
        errors = regr.errors()
        self.assertIsInstance(errors, list)
        self.assertTrue(errors)

    def test_error(self) -> None:
        for error in regr.errors():
            with self.subTest(name=error):
                self.assertIsSemiMetric(regr.error, name=error)

    def test_error_mae(self) -> None:
        self.assertIsSemiMetric(regr.error_mae)

    def test_error_mse(self) -> None:
        self.assertIsSemiMetric(regr.error_mse)

    def test_error_rmse(self) -> None:
        self.assertIsSemiMetric(regr.error_rmse)

    def test_error_rss(self) -> None:
        self.assertIsSemiMetric(regr.error_rss)

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
