# -*- coding: utf-8 -*-
"""Unittests for submodules of package 'nemoa.common'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import networkx as nx
import numpy as np

from nemoa.common import ntest

class TestSuite(ntest.TestSuite):
    """Testsuite for modules within the package 'nemoa.common'."""

    def test_common_nalgo(self) -> None:
        """Test module 'nemoa.common.nalgo'."""
        from nemoa.math import nalgo

        with self.subTest('search'):
            self.assertEqual(
                len(nalgo.search(nalgo, name='search')), 1)

        with self.subTest('custom'):
            @nalgo.custom(category='custom')
            def test_custom() -> None:
                pass
            self.assertEqual(
                getattr(test_custom, 'name', None), 'test_custom')
            self.assertEqual(
                getattr(test_custom, 'category', None), 'custom')

        with self.subTest('objective'):
            @nalgo.objective()
            def test_objective() -> None:
                pass
            self.assertEqual(
                getattr(test_objective, 'name', None), 'test_objective')
            self.assertEqual(
                getattr(test_objective, 'category', None), 'objective')

        with self.subTest('sampler'):
            @nalgo.sampler()
            def test_sampler() -> None:
                pass
            self.assertEqual(
                getattr(test_sampler, 'name', None), 'test_sampler')
            self.assertEqual(
                getattr(test_sampler, 'category', None), 'sampler')

        with self.subTest('statistic'):
            @nalgo.statistic()
            def test_statistic() -> None:
                pass
            self.assertEqual(
                getattr(test_statistic, 'name', None), 'test_statistic')
            self.assertEqual(
                getattr(test_statistic, 'category', None), 'statistic')

        with self.subTest('association'):
            @nalgo.association()
            def test_association() -> None:
                pass
            self.assertEqual(
                getattr(test_association, 'name', None), 'test_association')
            self.assertEqual(
                getattr(test_association, 'category', None), 'association')

    def test_common_nregr(self) -> None:
        """Test module 'nemoa.common.nregr'."""
        from nemoa.math import nregr

        x = np.array([[0.1, -1.9], [1.3, 2.2], [-3.4, -7.9]])
        y = np.array([[5.1, 2.9], [2.4, 1.1], [-1.6, -5.9]])
        z = np.array([[-2.6, 1.3], [1.1, -2.6], [7.0, -3.9]])

        with self.subTest('errors'):
            dfuncs = nregr.errors()
            self.assertIsInstance(dfuncs, list)
            self.assertTrue(dfuncs)

        for dfunc in nregr.errors():
            with self.subTest(nregr.ERR_PREFIX  + dfunc):
                dxx = nregr.error(x, x, dfunc=dfunc)
                dxy = nregr.error(x, y, dfunc=dfunc)
                dyx = nregr.error(y, x, dfunc=dfunc)

                # test type
                self.assertIsInstance(dxy, np.ndarray)
                # test dimension
                self.assertEqual(dxy.ndim, x.ndim-1)
                # test if discrepancy is not negative
                self.assertTrue(np.all(dxy >= 0))
                # test if discrepancy of identical values is zero
                self.assertTrue(np.all(dxx == 0))
                # test if discrepancy is symmetric
                self.assertTrue(np.all(dxy == dyx))

    def test_common_nmatrix(self) -> None:
        """Test module 'nemoa.common.nmatrix'."""
        from nemoa.math import nmatrix

        x = np.array([[0.1, -1.9], [1.3, 2.2], [-3.4, -7.9]])
        y = np.array([[5.1, 2.9], [2.4, 1.1], [-1.6, -5.9]])
        z = np.array([[-2.6, 1.3], [1.1, -2.6], [7.0, -3.9]])

        with self.subTest('norms'):
            norms = nmatrix.norms()
            self.assertIsInstance(norms, list)
            self.assertTrue(norms)

        for norm in nmatrix.norms():
            with self.subTest(nmatrix.NORM_PREFIX  + norm):
                mx = nmatrix.magnitude(x, norm=norm)
                my = nmatrix.magnitude(y, norm=norm)
                mn = nmatrix.magnitude(x - x, norm=norm)
                mxy = nmatrix.magnitude(x + y, norm=norm)
                m2x = nmatrix.magnitude(2 * x, norm=norm)

                # test type (and dimension)
                self.assertIsInstance(mx, float)
                # test if norm is not negative
                self.assertTrue(mx >= 0)
                # test if norm of zero values is zero
                self.assertTrue(mn == 0.)
                # test triangle inequality
                self.assertTrue(mxy <= mx + my)
                # test absolute homogeneity
                self.assertTrue(m2x == 2 * mx)

    def test_common_nvector(self) -> None:
        """Test module 'nemoa.common.nvector'."""
        from nemoa.math import nvector

        x = np.array([[0.1, -1.9], [1.3, 2.2], [-3.4, -7.9]])
        y = np.array([[5.1, 2.9], [2.4, 1.1], [-1.6, -5.9]])
        z = np.array([[-2.6, 1.3], [1.1, -2.6], [7.0, -3.9]])

        with self.subTest('norms'):
            norms = nvector.norms()
            self.assertIsInstance(norms, list)
            self.assertTrue(norms)

        for norm in nvector.norms():
            with self.subTest(nvector.NORM_PREFIX  + norm):
                lx = nvector.length(x, norm=norm)
                ly = nvector.length(y, norm=norm)
                ln = nvector.length(x - x, norm=norm)
                lxy = nvector.length(x + y, norm=norm)
                l2x = nvector.length(2 * x, norm=norm)

                # test type
                self.assertIsInstance(lx, np.ndarray)
                # test dimension
                self.assertEqual(lx.ndim, x.ndim-1)
                # test if norm is not negative
                self.assertTrue(np.all(lx >= 0))
                # test if norm of zero values is zero
                self.assertTrue(np.all(ln == 0))
                # test triangle inequality
                self.assertTrue(np.all(lxy <= lx + ly))
                # test absolute homogeneity
                self.assertTrue(np.all(l2x == 2 * lx))

        with self.subTest("metrices"):
            metrices = nvector.metrices()
            self.assertIsInstance(metrices, list)
            self.assertTrue(metrices)

        for metric in nvector.metrices():
            with self.subTest(nvector.DIST_PREFIX + metric):
                dxx = nvector.distance(x, x, metric=metric)
                dxy = nvector.distance(x, y, metric=metric)
                dyx = nvector.distance(y, x, metric=metric)
                dyz = nvector.distance(y, z, metric=metric)
                dxz = nvector.distance(x, z, metric=metric)

                # test type
                self.assertIsInstance(dxy, np.ndarray)
                # test dimension
                self.assertEqual(dxy.ndim, x.ndim-1)
                # test if distance is not negative
                self.assertTrue(np.all(dxy >= 0))
                # test if distance of identical values is zero
                self.assertTrue(np.all(dxx == 0))
                # test if distance is symmetric
                self.assertTrue(np.all(dxy == dyx))
                # test triangle inequality
                self.assertTrue(np.all(dxz <= dxy + dyz))

    def test_common_ncurve(self) -> None:
        """Test module 'nemoa.common.ncurve'."""
        from nemoa.math import ncurve

        arr = np.array([[0.0, 0.5], [1.0, -1.0]])

        with self.subTest("logistic"):
            self.assertTrue(
                np.isclose(
                    ncurve.logistic(arr).sum(),
                    2.122459, atol=1e-3))

        with self.subTest("tanh"):
            self.assertTrue(
                np.isclose(
                    ncurve.tanh(arr).sum(),
                    0.462117, atol=1e-3))

        with self.subTest("lecun"):
            self.assertTrue(
                np.isclose(
                    ncurve.lecun(arr).sum(),
                    0.551632, atol=1e-3))

        with self.subTest("elliot"):
            self.assertTrue(
                np.isclose(
                    ncurve.elliot(arr).sum(),
                    0.333333, atol=1e-3))

        with self.subTest("hill"):
            self.assertTrue(
                np.isclose(
                    ncurve.hill(arr).sum(),
                    0.447213, atol=1e-3))

        with self.subTest("arctan"):
            self.assertTrue(
                np.isclose(
                    ncurve.arctan(arr).sum(),
                    0.463647, atol=1e-3))

        with self.subTest("d_logistic"):
            self.assertTrue(
                np.isclose(
                    ncurve.d_logistic(arr).sum(),
                    0.878227, atol=1e-3))

        with self.subTest("d_elliot"):
            self.assertTrue(
                np.isclose(
                    ncurve.d_elliot(arr).sum(),
                    1.944444, atol=1e-3))

        with self.subTest("d_hill"):
            self.assertTrue(
                np.isclose(
                    ncurve.d_hill(arr).sum(),
                    2.422648, atol=1e-3))

        with self.subTest("d_lecun"):
            self.assertTrue(
                np.isclose(
                    ncurve.d_lecun(arr).sum(),
                    3.680217, atol=1e-3))

        with self.subTest("d_tanh"):
            self.assertTrue(
                np.isclose(
                    ncurve.d_tanh(arr).sum(),
                    2.626396, atol=1e-3))

        with self.subTest("d_arctan"):
            self.assertTrue(
                np.isclose(
                    ncurve.d_arctan(arr).sum(),
                    2.800000, atol=1e-3))

        with self.subTest("dialogistic"):
            self.assertTrue(
                np.isclose(
                    ncurve.dialogistic(arr).sum(),
                    0.251661, atol=1e-3))

        with self.subTest("softstep"):
            self.assertTrue(
                np.isclose(
                    ncurve.softstep(arr).sum(),
                    0.323637, atol=1e-3))

        with self.subTest("multilogistic"):
            self.assertTrue(
                np.isclose(
                    ncurve.multilogistic(arr).sum(),
                    0.500272, atol=1e-3))

    def test_common_ngraph(self) -> None:
        """Test module 'nemoa.common.ngraph'."""
        from nemoa.math import ngraph

        G = nx.DiGraph([(1, 3), (1, 4), (2, 3), (2, 4)], directed=True)
        nx.set_node_attributes(G, {
            1: {'layer': 'i', 'layer_id': 0, 'layer_sub_id': 0},
            2: {'layer': 'i', 'layer_id': 0, 'layer_sub_id': 1},
            3: {'layer': 'o', 'layer_id': 1, 'layer_sub_id': 0},
            4: {'layer': 'o', 'layer_id': 1, 'layer_sub_id': 1}})
        nx.set_edge_attributes(G, {
            (1, 3): {'weight': 0.1}, (1, 4): {'weight': 0.9},
            (2, 3): {'weight': 0.9}, (2, 4): {'weight': 0.1}})

        pos1 = {1: (.0, .25), 2: (.0, .75), 4: (1., .25), 3: (1., .75)}
        pos2 = {1: (.25, 1.), 2: (.75, 1.), 4: (.25, .0), 3: (.75, .0)}
        pos3 = {1: (4., 2.), 2: (4., 16.), 4: (32., 2.), 3: (32., 16.)}

        with self.subTest("is_directed"):
            self.assertTrue(ngraph.is_directed(G))

        with self.subTest("is_layered"):
            self.assertTrue(ngraph.is_layered(G))

        with self.subTest("get_layers"):
            self.assertEqual(ngraph.get_layers(G), [[1, 2], [3, 4]])

        with self.subTest("get_groups"):
            self.assertEqual(
                ngraph.get_groups(G, attribute='layer'),
                {'': [], 'i': [1, 2], 'o': [3, 4]})

        with self.subTest("get_layer_layout"):
            self.assertEqual(
                ngraph.get_layer_layout(G, direction='right'), pos1)
            self.assertEqual(
                ngraph.get_layer_layout(G, direction='down'), pos2)

        with self.subTest("rescale_layout"):
            self.assertEqual(
                ngraph.rescale_layout(
                    pos1, size=(40, 20), padding=(.2, .2, .1, .1)), pos3)

        with self.subTest("get_scaling_factor"):
            self.assertEqual(
                int(ngraph.get_scaling_factor(pos3)), 9)

        with self.subTest("get_layout_normsize"):
            self.assertEqual(
                int(ngraph.get_layout_normsize(pos3)['node_size']), 4)

        with self.subTest("get_node_layout"):
            self.assertIsInstance(
                ngraph.get_node_layout('observable')['color'], str)

        with self.subTest("get_layout"):
            self.assertEqual(
                ngraph.getlayout(G, 'layer', direction='right'), pos1)
