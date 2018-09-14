# -*- coding: utf-8 -*-
"""Unittests for submodules of package 'nemoa.common'."""

__author__ = 'Patrick Michl'
__email__ = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

from nemoa.common import ntest

class TestSuite(ntest.TestSuite):
    """Testsuite for modules in the package 'nemoa.common'."""

    def test_common_nalgorithm(self):
        from nemoa.common import nalgorithm

        with self.subTest('search'):
            self.assertTrue(
                len(nalgorithm.search(nalgorithm, name='search')) == 1)

        with self.subTest('custom'):
            @nalgorithm.custom(category='custom')
            def test_custom():
                pass
            self.assertTrue(
                test_custom.name == 'test_custom')
            self.assertTrue(
                test_custom.category == 'custom')

        with self.subTest('objective'):
            @nalgorithm.objective()
            def test_objective():
                pass
            self.assertTrue(
                test_objective.name == 'test_objective')
            self.assertTrue(
                test_objective.category == 'objective')

        with self.subTest('sampler'):
            @nalgorithm.sampler()
            def test_sampler():
                pass
            self.assertTrue(
                test_sampler.name == 'test_sampler')
            self.assertTrue(
                test_sampler.category == 'sampler')

        with self.subTest('statistic'):
            @nalgorithm.statistic()
            def test_statistic():
                pass
            self.assertTrue(
                test_statistic.name == 'test_statistic')
            self.assertTrue(
                test_statistic.category == 'statistic')

        with self.subTest('association'):
            @nalgorithm.association()
            def test_association():
                pass
            self.assertTrue(
                test_association.name == 'test_association')
            self.assertTrue(
                test_association.category == 'association')

    def test_common_nappinfo(self):
        from nemoa.common import nappinfo

        dirs = [
            'user_cache_dir', 'user_config_dir', 'user_data_dir',
            'user_log_dir', 'site_config_dir', 'site_data_dir']
        for key in dirs:
            with self.subTest(f"path('{key}')"):
                self.assertTrue(
                    nappinfo.path(key))

        for key in ['name', 'author', 'version', 'license']:
            with self.subTest(f"get('{key}')"):
                self.assertTrue(
                    nappinfo.get(key))

    def test_common_narray(self):
        from nemoa.common import narray

        import numpy as np

        x = np.array([[.1, -.9], [.3, .2], [-.4, -.9]])
        sumapprox = lambda x, y: np.isclose(x.sum(), y, atol=1e-3)

        with self.subTest("fromdict"):
            self.assertTrue(
                (
                    narray.fromdict(
                        {('a', 'b'): 1.},
                        labels=(['a', 'b'], ['a', 'b']), na=0.)
                    == np.array([[0., 1.], [0., 0.]])
                ).any())

        with self.subTest("asdict"):
            self.assertTrue(
                narray.asdict(
                    np.array([[0., 1.], [0., 0.]]),
                    labels=(['a', 'b'], ['a', 'b']), na=0.)
                == {('a', 'b'): 1.})

        with self.subTest("sumnorm"):
            self.assertTrue(
                sumapprox(narray.sumnorm(x), -1.6))

        with self.subTest("meannorm"):
            self.assertTrue(
                sumapprox(narray.meannorm(x), -0.5333))

        with self.subTest("devnorm"):
            self.assertTrue(
                sumapprox(narray.devnorm(x), 0.8129))

    def test_common_nbase(self):
        from nemoa.common import nbase

        with self.subTest("ObjectIP"):
            obj = nbase.ObjectIP()
            obj.name = 'test'
            self.assertTrue(
                obj.get('config') == {'name': 'test'})
            obj.path = ('%site_data_dir%', 'test')
            self.assertTrue(
                '%' not in obj.path)

    def test_common_ncalc(self):
        from nemoa.common import ncalc

        import numpy as np

        x = np.array([[0.0, 0.5], [1.0, -1.0]])
        sumapprox = lambda x, y: np.isclose(x.sum(), y, atol=1e-3)

        with self.subTest("logistic"):
            self.assertTrue(
                sumapprox(ncalc.logistic(x), 2.122459))

        with self.subTest("tanh"):
            self.assertTrue(
                sumapprox(ncalc.tanh(x), 0.462117))

        with self.subTest("lecun"):
            self.assertTrue(
                sumapprox(ncalc.lecun(x), 0.551632))

        with self.subTest("elliot"):
            self.assertTrue(
                sumapprox(ncalc.elliot(x), 0.333333))

        with self.subTest("hill"):
            self.assertTrue(
                sumapprox(ncalc.hill(x), 0.447213))

        with self.subTest("arctan"):
            self.assertTrue(
                sumapprox(ncalc.arctan(x), 0.463647))

        with self.subTest("d_logistic"):
            self.assertTrue(
                sumapprox(ncalc.d_logistic(x), 0.878227))

        with self.subTest("d_elliot"):
            self.assertTrue(
                sumapprox(ncalc.d_elliot(x), 1.944444))

        with self.subTest("d_hill"):
            self.assertTrue(
                sumapprox(ncalc.d_hill(x), 2.422648))

        with self.subTest("d_lecun"):
            self.assertTrue(
                sumapprox(ncalc.d_lecun(x), 3.680217))

        with self.subTest("d_tanh"):
            self.assertTrue(
                sumapprox(ncalc.d_tanh(x), 2.626396))

        with self.subTest("d_arctan"):
            self.assertTrue(
                sumapprox(ncalc.d_arctan(x), 2.800000))

        with self.subTest("dialogistic"):
            self.assertTrue(
                sumapprox(ncalc.dialogistic(x), 0.251661))

        with self.subTest("softstep"):
            self.assertTrue(
                sumapprox(ncalc.softstep(x), 0.323637))

        with self.subTest("multilogistic"):
            self.assertTrue(
                sumapprox(ncalc.multilogistic(x), 0.500272))

    def test_common_nconsole(self):
        from nemoa.common import nconsole

        with self.subTest("getch"):
            getch = nconsole.getch()
            self.assertTrue(hasattr(getch, 'get'))
            self.assertTrue(isinstance(getch.get(), str))

    def test_common_nclass(self):
        from nemoa.common import nclass

        class Base:
            @nclass.attributes(name='a', group=1)
            def geta(self):
                pass
            @nclass.attributes(name='b', group=2)
            def getb(self):
                pass
            @nclass.attributes(name='b', group=2)
            def setb(self):
                pass
        obj = Base()

        with self.subTest('hasbase'):
            self.assertTrue(
                nclass.hasbase(None, 'object'))
            self.assertTrue(
                nclass.hasbase(obj, 'Base'))

        with self.subTest('attributes'):
            self.assertTrue(
                getattr(obj.geta, 'name', None) == 'a')
            self.assertTrue(
                getattr(obj.getb, 'name', None) == 'b')

        with self.subTest('methods'):
            self.assertTrue(
                nclass.methods(obj, filter='get*').keys()
                == {'geta', 'getb'})
            self.assertTrue(
                nclass.methods(obj, filter='*b').keys()
                == {'getb', 'setb'})

    def test_common_ngraph(self):
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
            self.assertTrue(
                ngraph.is_directed(G))

        with self.subTest("is_layered"):
            self.assertTrue(
                ngraph.is_layered(G))

        with self.subTest("get_layers"):
            self.assertTrue(
                ngraph.get_layers(G) == [[1, 2], [3, 4]])

        with self.subTest("get_groups"):
            self.assertTrue(
                ngraph.get_groups(G, attribute='layer') == {
                    '': [], 'i': [1, 2], 'o': [3, 4]})

        with self.subTest("get_layer_layout"):
            self.assertTrue(
                ngraph.get_layer_layout(G, direction='right') == pos1)
            self.assertTrue(
                ngraph.get_layer_layout(G, direction='down') == pos2)

        with self.subTest("rescale_layout"):
            self.assertTrue(
                ngraph.rescale_layout(
                    pos1, size=(40, 20), padding=(.2, .2, .1, .1)) == pos3)

        with self.subTest("get_scaling_factor"):
            self.assertTrue(
                int(ngraph.get_scaling_factor(pos3)) == 9)

        with self.subTest("get_layout_normsize"):
            self.assertTrue(
                int(ngraph.get_layout_normsize(pos3)['node_size']) == 4)

        with self.subTest("get_node_layout"):
            self.assertTrue(
                isinstance(
                    ngraph.get_node_layout('observable')['color'], str))

        with self.subTest("get_layout"):
            self.assertTrue(
                ngraph.get_layout(G, 'layer', direction='right') == pos1)

    def test_common_ncsv(self):
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

        with self.subTest("get_header"):
            self.assertTrue(
                ncsv.get_header(filename) == header)

        with self.subTest("delimiter"):
            self.assertTrue(
                ncsv.delimiter(filename) == delim)

        with self.subTest("get_labels"):
            self.assertTrue(
                ncsv.get_labels(filename) == labels)

        with self.subTest("labelcolid"):
            self.assertTrue(
                ncsv.labelcolid(filename) == 0)

        with self.subTest("load"):
            rval = ncsv.load(filename)
            self.assertTrue(
                isinstance(rval, np.ndarray))
            self.assertTrue(
                (rval['col1'] == data['col1']).any())
            self.assertTrue(
                (rval['col2'] == data['col2']).any())

        if os.path.exists(filename):
            os.remove(filename)

    def test_common_nini(self):
        from nemoa.common import nini

        import os
        import tempfile

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
            self.assertTrue(
                nini.dumps(obj, header=header) == string)

        with self.subTest("loads"):
            self.assertTrue(
                nini.loads(string, structure=structure) == obj)

        with self.subTest("save"):
            self.assertTrue(
                nini.save(obj, filename, header=header))

        with self.subTest("load"):
            self.assertTrue(
                nini.load(filename, structure=structure) == obj)

        with self.subTest("header"):
            self.assertTrue(
                nini.header(filename) == header)

        if os.path.exists(filename):
            os.remove(filename)

    def test_common_nzip(self):
        from nemoa.common import nzip

        import os
        import tempfile

        obj = {True: 'a', 2: {None: .5}}
        blob = b'eJxrYK4tZNDoiGBkYGBILGT0ZqotZPJzt3/AAAbFpXoAgyIHVQ=='
        filename = tempfile.NamedTemporaryFile().name

        with self.subTest("dumps"):
            self.assertTrue(
                nzip.dumps(obj) == blob)

        with self.subTest("loads"):
            self.assertTrue(
                nzip.loads(blob) == obj)

        with self.subTest("dump"):
            self.assertTrue(
                nzip.dump(obj, filename) and os.path.exists(filename))

        with self.subTest("load"):
            self.assertTrue(nzip.load(filename) == obj)

        if os.path.exists(filename):
            os.remove(filename)

    def test_common_nmodule(self):
        from nemoa.common import nmodule

        with self.subTest("curname"):
            self.assertTrue(
                nmodule.curname() == __name__)

        with self.subTest("caller"):
            self.assertTrue(
                nmodule.caller() == __name__ + '.test_common_nmodule')

        with self.subTest("submodules"):
            self.assertTrue(
                nmodule.__name__
                in nmodule.submodules(nmodule.objectify('nemoa.common')))

        with self.subTest("objectify"):
            self.assertTrue(
                hasattr(nmodule.objectify(nmodule.__name__), '__name__'))
            self.assertTrue(
                nmodule.objectify(nmodule.__name__).__name__
                == nmodule.__name__)

        with self.subTest("functions"):
            self.assertTrue(
                nmodule.__name__ + '.functions'
                in nmodule.functions(nmodule))
            self.assertTrue(
                len(nmodule.functions(nmodule, name='')) == 0)
            self.assertTrue(
                len(nmodule.functions(nmodule, name='functions')) == 1)

        with self.subTest("search"):
            self.assertTrue(
                len(nmodule.search(nmodule, name='search')) == 1)

    def test_common_nfunc(self):
        from nemoa.common import nfunc

        with self.subTest("about"):
            self.assertTrue(
                nfunc.about(nfunc.about)
                == 'Summary about a function')

        with self.subTest("func"):
            self.assertTrue(
                type(nfunc.func(nfunc.__name__ + '.func')).__name__
                == 'function')

        with self.subTest("kwargs"):
            self.assertTrue(
                nfunc.kwargs(nfunc.kwargs) == {'default': None})
            self.assertTrue(
                nfunc.kwargs(nfunc.kwargs, default={}) == {})
            self.assertTrue(
                nfunc.kwargs(nfunc.kwargs, default={'default': True})
                == {'default': True})

    def test_common_ndict(self):
        from nemoa.common import ndict

        with self.subTest("filter"):
            self.assertTrue(
                ndict.filter({'a1': 1, 'a2': 2, 'b1': 3}, 'a*') \
                == {'a1': 1, 'a2': 2})

        with self.subTest("groupby"):
            self.assertTrue(
                ndict.groupby(
                    {1: {'a': 0}, 2: {'a': 0}, 3: {'a': 1}, 4: {}}, key='a')
                == {
                    0: {1: {'a': 0}, 2: {'a': 0}},
                    1: {3: {'a': 1}}, None: {4: {}}})

        with self.subTest("merge"):
            self.assertTrue(
                ndict.merge({'a': 1}, {'a': 2, 'b': 2}, {'c': 3})
                == {'a': 1, 'b': 2, 'c': 3})

        with self.subTest("reduce"):
            self.assertTrue(
                ndict.reduce({'a1': 1, 'a2': 2, 'b1': 3}, 'a')
                == {'1': 1, '2': 2})

        with self.subTest("strkeys"):
            self.assertTrue(
                ndict.strkeys({(1, 2): 3, None: {True: False}})
                == {('1', '2'): 3, 'None': {'True': False}})

        with self.subTest("sumjoin"):
            self.assertTrue(
                ndict.sumjoin({'a': 1}, {'a': 2, 'b': 3}) == {'a': 3, 'b': 3})
            self.assertTrue(
                ndict.sumjoin({1: 'a', 2: True}, {1: 'b', 2: True})
                == {1: 'ab', 2: 2})

    def test_common_npath(self):
        from nemoa.common import npath

        import tempfile
        import pathlib

        dname = str(pathlib.Path('a', 'b', 'c', 'd'))
        plike = (('a', ('b', 'c')), 'd', 'base.ext')
        stdir = tempfile.TemporaryDirectory().name

        with self.subTest("cwd"):
            self.assertTrue(
                npath.cwd())

        with self.subTest("home"):
            self.assertTrue(
                npath.home())

        with self.subTest("clear"):
            self.assertTrue(
                npath.clear('3/\nE{$5}.e') == '3E5.e')

        with self.subTest("join"):
            self.assertTrue(
                npath.join(('a', ('b', 'c')), 'd') == dname)

        with self.subTest("expand"):
            self.assertTrue(
                npath.expand(
                    '%var1%/c', 'd',
                    udict={'var1': 'a/%var2%', 'var2': 'b'}) == dname)

        with self.subTest("dirname"):
            self.assertTrue(
                npath.dirname(*plike) == dname)

        with self.subTest("filename"):
            self.assertTrue(
                npath.filename(*plike) == 'base.ext')

        with self.subTest("basename"):
            self.assertTrue(
                npath.basename(*plike) == 'base')

        with self.subTest("fileext"):
            self.assertTrue(
                npath.fileext(*plike) == 'ext')

        with self.subTest("mkdir"):
            self.assertTrue(
                npath.mkdir(stdir))

        with self.subTest("rmdir"):
            self.assertTrue(
                npath.rmdir(stdir))

        # with self.subTest("cp"):
        #     self.assertTrue(True)

    def test_common_nsysinfo(self):
        from nemoa.common import nsysinfo

        with self.subTest("hostname"):
            self.assertTrue(
                nsysinfo.hostname())

        with self.subTest("osname"):
            self.assertTrue(
                nsysinfo.osname())

        with self.subTest("ttylib"):
            self.assertTrue(
                nsysinfo.ttylib())

    def test_common_ntable(self):
        from nemoa.common import ntable

        import numpy as np

        with self.subTest("addcols"):
            tgt = np.array(
                [(1., 2), (3., 4)], dtype=[('x', float), ('y', int)])
            src = np.array(
                [('a'), ('b')], dtype=[('z', 'U4')])
            self.assertTrue(
                ntable.addcols(tgt, src, 'z')['z'][0] == 'a')

    def test_common_ntext(self):
        from nemoa.common import ntext

        with self.subTest("splitargs"):
            self.assertTrue(
                ntext.splitargs("f(1., 'a', b = 2)")
                == ('f', (1.0, 'a'), {'b': 2}))

        with self.subTest("aslist"):
            self.assertTrue(
                ntext.aslist('a, 2, ()') == ['a', '2', '()'])
            self.assertTrue(
                ntext.aslist('[1, 2, 3]') == [1, 2, 3])

        with self.subTest("astuple"):
            self.assertTrue(
                ntext.astuple('a, 2, ()') == ('a', '2', '()'))
            self.assertTrue(
                ntext.astuple('(1, 2, 3)') == (1, 2, 3))

        with self.subTest("asset"):
            self.assertTrue(
                ntext.asset('a, 2, ()') == {'a', '2', '()'})
            self.assertTrue(
                ntext.asset('{1, 2, 3}') == {1, 2, 3})

        with self.subTest("asdict"):
            self.assertTrue(
                ntext.asdict("a = 'b', b = 1") == {'a': 'b', 'b': 1})
            self.assertTrue(
                ntext.asdict("'a': 'b', 'b': 1") == {'a': 'b', 'b': 1})

        with self.subTest("astype"):
            examples = [
                ('t', 'str'), (True, 'bool'), (1, 'int'), (.5, 'float'),
                ((1+1j), 'complex')]
            for var, typ in examples:
                self.assertTrue(
                    ntext.astype(str(var), typ) == var)
