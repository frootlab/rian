# -*- coding: utf-8 -*-
"""Unittests for submodules of package 'nemoa.common'."""

__author__ = 'Patrick Michl'
__email__ = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

from nemoa.common import ntest

class TestSuite(ntest.TestSuite):
    """Testsuite for modules within the package 'nemoa.common'."""

    def test_common_nalgo(self) -> None:
        """Test module 'nemoa.common.nalgo'."""
        from nemoa.common import nalgo

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

    def test_common_napp(self) -> None:
        """Test module 'nemoa.common.napp'."""
        from nemoa.common import napp

        dirs = [
            'user_cache_dir', 'user_config_dir', 'user_data_dir',
            'user_log_dir', 'site_config_dir', 'site_data_dir']
        for key in dirs:
            with self.subTest(f"path('{key}')"):
                self.assertTrue(napp.getdir(key))

        for key in ['name', 'author', 'version', 'license']:
            with self.subTest(f"get('{key}')"):
                self.assertTrue(napp.getvar(key))

    def test_common_narray(self) -> None:
        """Test module 'nemoa.common.narray'."""
        from nemoa.common import narray
        from nemoa.types import NaN
        import numpy as np

        arr = np.array([[NaN, 1.], [NaN, NaN]])
        dic = {('a', 'b'): 1.}
        labels = (['a', 'b'], ['a', 'b'])

        with self.subTest("fromdict"):
            self.assertTrue(
                np.allclose(
                    narray.fromdict(dic, labels=labels), arr,
                    equal_nan=True))

        with self.subTest("asdict"):
            self.assertTrue(
                narray.asdict(arr, labels=labels) == {('a', 'b'): 1.})

    def test_common_nregr(self) -> None:
        """Test module 'nemoa.common.nregr'."""
        from nemoa.common import nregr
        import numpy as np

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

    def test_common_nvector(self) -> None:
        """Test module 'nemoa.common.nvector'."""
        from nemoa.common import nvector
        import numpy as np

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

    def test_common_nbase(self) -> None:
        """Test module 'nemoa.common.nbase'."""
        from nemoa.common import nbase

        with self.subTest("ObjectIP"):
            obj = nbase.ObjectIP()
            obj.name = 'test'
            self.assertTrue(
                obj.get('config') == {'name': 'test'})
            obj.path = ('%site_data_dir%', 'test')
            self.assertNotIn('%', obj.path)

    def test_common_ncurve(self) -> None:
        """Test module 'nemoa.common.ncurve'."""
        from nemoa.common import ncurve
        import numpy as np

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

    def test_common_nconsole(self) -> None:
        """Test module 'nemoa.common.nconsole'."""
        from nemoa.common import nconsole

        with self.subTest("getch"):
            getch = nconsole.getch()
            self.assertTrue(
                hasattr(getch, 'get'))
            self.assertIsInstance(
                getattr(getch, 'get')(), str)

    def test_common_nclass(self) -> None:
        """Test module 'nemoa.common.nclass'."""
        from nemoa.common import nclass

        class Base:
            @nclass.attributes(name='a', group=1)
            def geta(self) -> None:
                pass
            @nclass.attributes(name='b', group=2)
            def getb(self) -> None:
                pass
            @nclass.attributes(name='b', group=2)
            def setb(self) -> None:
                pass
        obj = Base()

        with self.subTest('hasbase'):
            self.assertTrue(nclass.hasbase(None, 'object'))
            self.assertTrue(nclass.hasbase(obj, 'Base'))

        with self.subTest('attributes'):
            self.assertEqual(getattr(obj.geta, 'name', None), 'a')
            self.assertEqual(getattr(obj.getb, 'name', None), 'b')

        with self.subTest('methods'):
            self.assertEqual(
                nclass.methods(obj, pattern='get*').keys(), {'geta', 'getb'})
            self.assertEqual(
                nclass.methods(obj, pattern='*b').keys(), {'getb', 'setb'})

    def test_common_ngraph(self) -> None:
        """Test module 'nemoa.common.ngraph'."""
        from nemoa.common import ngraph

        import networkx as nx

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

    def test_common_ncsv(self) -> None:
        """Test module 'nemoa.common.ncsv'."""
        from nemoa.common import ncsv

        import numpy as np
        import os
        import tempfile

        filename = tempfile.NamedTemporaryFile().name + '.csv'
        header = '-*- coding: utf-8 -*-'
        data = np.array(
            [('row1', 1.1, 1.2), ('row2', 2.1, 2.2), ('row3', 3.1, 3.2)],
            dtype=[('label', 'U8'), ('col1', 'f8'), ('col2', 'f8')])
        delim = ','
        labels = ['', 'col1', 'col2']

        with self.subTest("save"):
            self.assertTrue(
                ncsv.save(
                    filename, data, header=header, labels=labels, delim=delim))

        with self.subTest("getheader"):
            self.assertEqual(ncsv.getheader(filename), header)

        with self.subTest("getdelim"):
            self.assertEqual(ncsv.getdelim(filename), delim)

        with self.subTest("getlabels"):
            self.assertEqual(ncsv.getlabels(filename), labels)

        with self.subTest("getacolid"):
            self.assertEqual(ncsv.getacolid(filename), 0)

        with self.subTest("load"):
            rval = ncsv.load(filename)
            self.assertTrue(
                isinstance(rval, np.ndarray))
            self.assertTrue(
                np.all(np.array(rval)['col1'] == data['col1']))
            self.assertTrue(
                np.all(np.array(rval)['col2'] == data['col2']))

        if os.path.exists(filename):
            os.remove(filename)

    def test_common_nini(self) -> None:
        """Test module 'nemoa.common.nini'."""
        from nemoa.common import nini

        import os
        import tempfile
        from typing import cast

        filename = tempfile.NamedTemporaryFile().name + '.ini'
        header = '-*- coding: utf-8 -*-'
        obj = {
            'n': {'a': 's', 'b': True, 'c': 1},
            'l1': {'a': 1}, 'l2': {'a': 2}}
        structure = {
            'n': {'a': 'str', 'b': 'bool', 'c': 'int'},
            'l[0-9]*': {'a': 'int'}}
        string = (
            "# -*- coding: utf-8 -*-\n\n"
            "[n]\na = s\nb = True\nc = 1\n\n"
            "[l1]\na = 1\n\n[l2]\na = 2\n\n")

        with self.subTest("dumps"):
            self.assertEqual(
                nini.dumps(obj, header=header), string)

        with self.subTest("loads"):
            self.assertEqual(
                nini.loads(string, structure=cast(dict, structure)), obj)

        with self.subTest("save"):
            self.assertTrue(
                nini.save(obj, filename, header=header))

        with self.subTest("load"):
            self.assertEqual(
                nini.load(filename, structure=cast(dict, structure)), obj)

        with self.subTest("getheader"):
            self.assertEqual(nini.getheader(filename), header)

        if os.path.exists(filename):
            os.remove(filename)

    def test_common_nzip(self) -> None:
        """Test module 'nemoa.common.nzip'."""
        from nemoa.common import nzip

        import os
        import tempfile

        obj = {True: 'a', 2: {None: .5}}
        blob = b'eJxrYK4tZNDoiGBkYGBILGT0ZqotZPJzt3/AAAbFpXoAgyIHVQ=='
        filename = tempfile.NamedTemporaryFile().name

        with self.subTest("dumps"):
            self.assertEqual(nzip.dumps(obj), blob)

        with self.subTest("loads"):
            self.assertEqual(nzip.loads(blob), obj)

        with self.subTest("dump"):
            self.assertTrue(nzip.dump(obj, filename))
            self.assertTrue(os.path.exists(filename))

        with self.subTest("load"):
            self.assertEqual(nzip.load(filename), obj)

        if os.path.exists(filename):
            os.remove(filename)

    def test_common_nmodule(self) -> None:
        """Test module 'nemoa.common.nmodule'."""
        from nemoa.common import nmodule
        from nemoa.types import Module
        from typing import cast

        with self.subTest("curname"):
            self.assertEqual(nmodule.curname(), __name__)

        with self.subTest("caller"):
            self.assertEqual(
                nmodule.caller(), __name__ + '.test_common_nmodule')

        with self.subTest("submodules"):
            self.assertIn(
                nmodule.__name__,
                nmodule.submodules(nmodule.inst('nemoa.common')))

        with self.subTest("inst"):
            self.assertTrue(
                hasattr(
                    nmodule.inst(nmodule.__name__), '__name__'))
            self.assertEqual(
                cast(Module, nmodule.inst(nmodule.__name__)).__name__,
                nmodule.__name__)

        with self.subTest("functions"):
            self.assertIn(
                nmodule.__name__ + '.functions',
                nmodule.functions(nmodule))
            self.assertEqual(
                len(nmodule.functions(nmodule, name='')), 0)
            self.assertEqual(
                len(nmodule.functions(nmodule, name='functions')), 1)

        with self.subTest("search"):
            self.assertEqual(
                len(nmodule.search(nmodule, name='search')), 1)

    def test_common_nfunc(self) -> None:
        """Test module 'nemoa.common.nfunc'."""
        from nemoa.common import nfunc

        with self.subTest("about"):
            self.assertEqual(
                nfunc.about(nfunc.about), 'Summary about a function')

        with self.subTest("inst"):
            self.assertEqual(
                type(nfunc.inst(nfunc.__name__ + '.inst')).__name__,
                'function')

        with self.subTest("kwargs"):
            self.assertEqual(
                nfunc.kwargs(nfunc.kwargs), {'default': None})
            self.assertEqual(
                nfunc.kwargs(nfunc.kwargs, default={}), {})
            self.assertEqual(
                nfunc.kwargs(nfunc.kwargs, default={'default': True}),
                {'default': True})

    def test_common_ndict(self) -> None:
        """Test module 'nemoa.common.ndict'."""
        from nemoa.common import ndict

        with self.subTest("select"):
            self.assertTrue(
                ndict.select({'a1': 1, 'a2': 2, 'b1': 3}, pattern='a*') \
                == {'a1': 1, 'a2': 2})

        with self.subTest("groupby"):
            self.assertEqual(
                ndict.groupby(
                    {1: {'a': 0}, 2: {'a': 0}, 3: {'a': 1}, 4: {}}, key='a'),
                {
                    0: {1: {'a': 0}, 2: {'a': 0}},
                    1: {3: {'a': 1}}, None: {4: {}}})

        with self.subTest("flatten"):
            self.assertEqual(
                ndict.flatten({1: {'a': {}}, 2: {'b': {}}}),
                {'a': {}, 'b': {}})
            self.assertEqual(
                ndict.flatten({1: {'a': {}}, 2: {'b': {}}}, group='id'),
                {'a': {'id': 1}, 'b': {'id': 2}})

        with self.subTest("merge"):
            self.assertEqual(
                ndict.merge({'a': 1}, {'a': 2, 'b': 2}, {'c': 3}),
                {'a': 1, 'b': 2, 'c': 3})

        with self.subTest("crop"):
            self.assertEqual(
                ndict.crop({'a1': 1, 'a2': 2, 'b1': 3}, 'a'),
                {'1': 1, '2': 2})

        with self.subTest("strkeys"):
            self.assertEqual(
                ndict.strkeys({(1, 2): 3, None: {True: False}}),
                {('1', '2'): 3, 'None': {'True': False}})

        with self.subTest("sumjoin"):
            self.assertEqual(
                ndict.sumjoin({'a': 1}, {'a': 2, 'b': 3}), {'a': 3, 'b': 3})
            self.assertEqual(
                ndict.sumjoin({1: 'a', 2: True}, {1: 'b', 2: True}),
                {1: 'ab', 2: 2})

    def test_common_npath(self) -> None:
        """Test module 'nemoa.common.npath'."""
        from nemoa.common import npath

        import tempfile
        import pathlib

        dname = str(pathlib.Path('a', 'b', 'c', 'd'))
        ptest = (('a', ('b', 'c')), 'd', 'base.ext')
        stdir = tempfile.TemporaryDirectory().name

        with self.subTest("cwd"):
            self.assertTrue(npath.cwd())

        with self.subTest("home"):
            self.assertTrue(npath.home())

        with self.subTest("clear"):
            self.assertEqual(npath.clear('3/\nE{$5}.e'), '3E5.e')

        with self.subTest("join"):
            self.assertEqual(npath.join(('a', ('b', 'c')), 'd'), dname)

        with self.subTest("expand"):
            self.assertEqual(
                npath.expand(
                    '%var1%/c', 'd',
                    udict={'var1': 'a/%var2%', 'var2': 'b'}), dname)

        with self.subTest("dirname"):
            self.assertEqual(npath.dirname(*ptest), dname)

        with self.subTest("filename"):
            self.assertEqual(npath.filename(*ptest), 'base.ext')

        with self.subTest("basename"):
            self.assertEqual(npath.basename(*ptest), 'base')

        with self.subTest("fileext"):
            self.assertEqual(npath.fileext(*ptest), 'ext')

        with self.subTest("mkdir"):
            self.assertTrue(npath.mkdir(stdir))

        with self.subTest("isdir"):
            self.assertTrue(npath.isdir(stdir))

        with self.subTest("isfile"):
            self.assertFalse(npath.isfile(stdir))

        with self.subTest("validfile"):
            self.assertIsNone(npath.validfile(stdir))

        with self.subTest("rmdir"):
            self.assertTrue(npath.rmdir(stdir))

        # with self.subTest("cp"):
        #     self.assertTrue(True)

    def test_common_nsysinfo(self) -> None:
        """Test module 'nemoa.common.nsysinfo'."""
        from nemoa.common import nsysinfo

        with self.subTest("hostname"):
            self.assertTrue(nsysinfo.hostname())

        with self.subTest("osname"):
            self.assertTrue(nsysinfo.osname())

        with self.subTest("ttylib"):
            self.assertTrue(nsysinfo.ttylib())

    def test_common_ntable(self) -> None:
        """Test module 'nemoa.common.ntable'."""
        from typing import cast
        from nemoa.common import ntable
        from nemoa.types import Any
        import numpy as np

        with self.subTest("addcols"):
            tgt = np.array(
                [(1., 2), (3., 4)], dtype=[('x', float), ('y', int)])
            src = np.array(
                [('a'), ('b')], dtype=[('z', 'U4')])
            self.assertEqual(
                cast(Any, ntable.addcols(tgt, src, 'z'))['z'][0], 'a')

    def test_common_ntext(self) -> None:
        """Test module 'nemoa.common.ntext'."""
        from nemoa.common import ntext

        with self.subTest("splitargs"):
            self.assertEqual(
                ntext.splitargs("f(1., 'a', b = 2)"),
                ('f', (1.0, 'a'), {'b': 2}))

        with self.subTest("aslist"):
            self.assertEqual(ntext.aslist('a, 2, ()'), ['a', '2', '()'])
            self.assertEqual(ntext.aslist('[1, 2, 3]'), [1, 2, 3])

        with self.subTest("astuple"):
            self.assertEqual(ntext.astuple('a, 2, ()'), ('a', '2', '()'))
            self.assertEqual(ntext.astuple('(1, 2, 3)'), (1, 2, 3))

        with self.subTest("asset"):
            self.assertEqual(ntext.asset('a, 2, ()'), {'a', '2', '()'})
            self.assertEqual(ntext.asset('{1, 2, 3}'), {1, 2, 3})

        with self.subTest("asdict"):
            self.assertEqual(
                ntext.asdict("a = 'b', b = 1"), {'a': 'b', 'b': 1})
            self.assertEqual(
                ntext.asdict("'a': 'b', 'b': 1"), {'a': 'b', 'b': 1})

        with self.subTest("astype"):
            examples = [
                ('t', 'str'), (True, 'bool'), (1, 'int'), (.5, 'float'),
                ((1+1j), 'complex')]
            for var, typ in examples:
                self.assertEqual(ntext.astype(str(var), typ), var)
