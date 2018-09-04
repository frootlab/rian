# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa

from nemoa.common import unittest

class TestSuite(unittest.TestSuite):

    def test_common_appinfo(self):
        from nemoa.common import appinfo

        dirs = ['user_cache_dir', 'user_config_dir', 'user_data_dir',
            'user_log_dir', 'site_config_dir', 'site_data_dir']
        vars = ['name', 'author', 'version', 'license']

        for key in dirs:
            with self.subTest(function = f"path('{key}')"):
                self.assertTrue(appinfo.path(key))

        for key in vars:
            with self.subTest(function = f"get('{key}')"):
                self.assertTrue(appinfo.get(key))

    def test_common_array(self):
        from nemoa.common import array

        import numpy as np

        a = np.array([[.1, -.9], [.3, .2], [-.4, -.9]])
        b = np.array([[0., 1.], [0., 0.]])
        t = lambda x, y: np.isclose(x.sum(), y, atol = 1e-3)
        d = {('a', 'b'): 1.}
        labels = (['a', 'b'], ['a', 'b'])
        na = 0.

        with self.subTest(function = "fromdict"):
            rval = array.fromdict(d, labels = labels, na = na)
            self.assertTrue((rval == b).any())

        with self.subTest(function = "asdict"):
            rval = array.asdict(b, labels = labels, na = na)
            self.assertTrue(rval == d)

        with self.subTest(function = "sumnorm"):
            self.assertTrue(t(array.sumnorm(a), -1.6))

        with self.subTest(function = "meannorm"):
            self.assertTrue(t(array.meannorm(a), -0.5333))

        with self.subTest(function = "devnorm"):
            self.assertTrue(t(array.devnorm(a), 0.8129))

    def test_common_calc(self):
        from nemoa.common import calc

        import numpy as np

        x = np.array([[0.0, 0.5], [1.0, -1.0]])
        t = lambda x, y: np.isclose(x.sum(), y, atol = 1e-3)

        with self.subTest(function = "logistic"):
            self.assertTrue(t(calc.logistic(x), 2.122459))

        with self.subTest(function = "tanh"):
            self.assertTrue(t(calc.tanh(x), 0.462117))

        with self.subTest(function = "lecun"):
            self.assertTrue(t(calc.lecun(x), 0.551632))

        with self.subTest(function = "elliot"):
            self.assertTrue(t(calc.elliot(x), 0.333333))

        with self.subTest(function = "hill"):
            self.assertTrue(t(calc.hill(x), 0.447213))

        with self.subTest(function = "arctan"):
            self.assertTrue(t(calc.arctan(x), 0.463647))

        with self.subTest(function = "d_logistic"):
            self.assertTrue(t(calc.d_logistic(x), 0.878227))

        with self.subTest(function = "d_elliot"):
            self.assertTrue(t(calc.d_elliot(x), 1.944444))

        with self.subTest(function = "d_hill"):
            self.assertTrue(t(calc.d_hill(x), 2.422648))

        with self.subTest(function = "d_lecun"):
            self.assertTrue(t(calc.d_lecun(x), 3.680217))

        with self.subTest(function = "d_tanh"):
            self.assertTrue(t(calc.d_tanh(x), 2.626396))

        with self.subTest(function = "d_arctan"):
            self.assertTrue(t(calc.d_arctan(x), 2.800000))

        with self.subTest(function = "dialogistic"):
            self.assertTrue(t(calc.dialogistic(x), 0.251661))

        with self.subTest(function = "softstep"):
            self.assertTrue(t(calc.softstep(x), 0.323637))

        with self.subTest(function = "multilogistic"):
            self.assertTrue(t(calc.multilogistic(x), 0.500272))

    def test_common_classes(self):
        from nemoa.common import classes

        class t:
            def mm(self): pass
            def nn(self): pass

        obj = t()

        with self.subTest(function = 'hasbase'):
            self.assertTrue(classes.hasbase(None, 'object'))

        with self.subTest(function = 'methods'):
            self.assertTrue(len(classes.methods(obj, prefix = 'm')) == 1)

    def test_common_dict(self):
        import nemoa.common.dict

        import numpy as np

        with self.subTest(function = "merge"):
            func = nemoa.common.dict.merge
            rval = func({'a': 1}, {'a': 2, 'b': 2}, {'c': 3})
            test = rval == {'a': 1, 'b': 2, 'c': 3}
            self.assertTrue(test)

        with self.subTest(function = "section"):
            func = nemoa.common.dict.section
            rval = func({'a1': 1, 'a2': 2, 'b1': 3}, 'a')
            test = rval == {'1': 1, '2': 2}
            self.assertTrue(test)

        with self.subTest(function = "strkeys"):
            func = nemoa.common.dict.strkeys
            rval = func({(1, 2): 3, None: {True: False}})
            test = rval == {('1', '2'): 3, 'None': {'True': False}}
            self.assertTrue(test)

        with self.subTest(function = "sumjoin"):
            func = nemoa.common.dict.sumjoin
            rval = func({'a': 1}, {'a': 2, 'b': 3})
            test = rval == {'a': 3, 'b': 3}
            self.assertTrue(test)

    def test_common_graph(self):
        from nemoa.common import graph

        import networkx

        l = [(1, 3), (1, 4), (2, 3), (2, 4)]
        G = networkx.DiGraph(l, directed = True)
        networkx.set_node_attributes(G, {
            1: {'layer': 'i', 'layer_id': 0 , 'layer_sub_id': 0},
            2: {'layer': 'i', 'layer_id': 0 , 'layer_sub_id': 1},
            3: {'layer': 'o', 'layer_id': 1 , 'layer_sub_id': 0},
            4: {'layer': 'o', 'layer_id': 1 , 'layer_sub_id': 1}
        })

        networkx.set_edge_attributes(G, {
            (1, 3): {'weight': 0.1}, (1, 4): {'weight': 0.9},
            (2, 3): {'weight': 0.9}, (2, 4): {'weight': 0.1}
        })

        pos1 = {1: (.0, .25), 2: (.0, .75), 4: (1., .25), 3: (1., .75)}
        pos2 = {1: (.25, 1.), 2: (.75, 1.), 4: (.25, .0), 3: (.75, .0)}
        pos3 = {1: (4., 2.), 2: (4., 16.), 4: (32., 2.), 3: (32., 16.)}

        with self.subTest(function = "is_directed"):
            test = graph.is_directed(G)
            self.assertTrue(test)

        with self.subTest(function = "is_layered"):
            test = graph.is_layered(G)
            self.assertTrue(test)

        with self.subTest(function = "get_layers"):
            test = graph.get_layers(G) == [[1, 2], [3, 4]]
            self.assertTrue(test)

        with self.subTest(function = "get_groups"):
            test = graph.get_groups(G, attribute = 'layer') \
                == {'': [], 'i': [1, 2], 'o': [3, 4]}
            self.assertTrue(test)

        with self.subTest(function = "get_layer_layout"):
            test = graph.get_layer_layout(G, direction = 'right') == pos1 \
                and graph.get_layer_layout(G, direction = 'down') == pos2
            self.assertTrue(test)

        with self.subTest(function = "rescale_layout"):
            test = graph.rescale_layout(pos1, size = (40, 20), \
                padding = (.2, .2, .1, .1)) == pos3
            self.assertTrue(test)

        with self.subTest(function = "get_scaling_factor"):
            test = int(graph.get_scaling_factor(pos3)) == 9
            self.assertTrue(test)

        with self.subTest(function = "get_layout_normsize"):
            test = int(graph.get_layout_normsize(pos3)['node_size']) == 4
            self.assertTrue(test)

        with self.subTest(function = "get_node_layout"):
            test = isinstance(graph.get_node_layout('observable')['color'], str)
            self.assertTrue(test)

        with self.subTest(function = "get_layout"):
            test = graph.get_layout(G, 'layer', direction = 'right') == pos1
            self.assertTrue(test)

    def test_common_iocsv(self):
        from nemoa.common import iocsv

        import numpy as np
        import os
        import tempfile

        f = tempfile.NamedTemporaryFile().name + '.csv'

        header = '-*- coding: utf-8 -*-'
        data = np.array(
            [("row1", 1.1, 1.2), ("row2", 2.1, 2.2), ("row3", 3.1, 3.2)],
            dtype=[('label', 'U8'), ('col1', 'f8'), ('col2', 'f8')])
        delim = ','
        labels = ["", "col1", "col2"]

        with self.subTest(function = "save"):
            self.assertTrue(iocsv.save(f, data, header = header,
                labels = labels, delim = delim))

        with self.subTest(function = "get_header"):
            self.assertTrue(iocsv.get_header(f) == header)

        with self.subTest(function = "get_delim"):
            self.assertTrue(iocsv.get_delim(f) == delim)

        with self.subTest(function = "get_labels"):
            self.assertTrue(iocsv.get_labels(f) == labels)

        with self.subTest(function = "get_labelcolumn"):
            self.assertTrue(iocsv.get_labelcolumn(f) == 0)

        with self.subTest(function = "load"):
            rval = iocsv.load(f)
            test = isinstance(rval, np.ndarray) \
                and (rval['col1'] == data['col1']).any() \
                and (rval['col2'] == data['col2']).any()
            self.assertTrue(test)

        if os.path.exists(f): os.remove(f)

    def test_common_ioini(self):
        from nemoa.common import ioini

        import os
        import tempfile

        f = tempfile.NamedTemporaryFile().name + '.ini'
        d = {'n': {'a': 's', 'b': True, 'c': 1 },
            'l1': {'a': 1}, 'l2': {'a': 2} }
        struct = { 'n': {'a': 'str', 'b': 'bool', 'c': 'int' },
            'l[0-9]*': {'a': 'int' }}
        header = '-*- coding: utf-8 -*-'
        s = ("# -*- coding: utf-8 -*-\n\n"
            "[n]\na = s\nb = True\nc = 1\n\n"
            "[l1]\na = 1\n\n[l2]\na = 2\n\n")

        with self.subTest(function = "dumps"):
            self.assertTrue(ioini.dumps(d, header = header) == s)

        with self.subTest(function = "loads"):
            self.assertTrue(ioini.loads(s, structure = struct) == d)

        with self.subTest(function = "save"):
            self.assertTrue(ioini.save(d, f, header = header))

        with self.subTest(function = "load"):
            self.assertTrue(ioini.load(f, structure = struct) == d)

        with self.subTest(function = "header"):
            self.assertTrue(ioini.header(f) == header)

        if os.path.exists(f): os.remove(f)

    def test_common_iozip(self):
        from nemoa.common import iozip

        import os
        import tempfile

        d = {True: 'a', 2: {None: .5}}
        s = b'eJxrYK4tZNDoiGBkYGBILGT0ZqotZPJzt3/AAAbFpXoAgyIHVQ=='
        f = tempfile.NamedTemporaryFile().name

        with self.subTest(function = "dumps"):
            self.assertTrue(iozip.dumps(d) == s)

        with self.subTest(function = "loads"):
            self.assertTrue(iozip.loads(s) == d)

        with self.subTest(function = "dump"):
            iozip.dump(d, f)
            self.assertTrue(os.path.exists(f))

        with self.subTest(function = "load"):
            self.assertTrue(iozip.load(f) == d)

        if os.path.exists(f): os.remove(f)

    def test_common_module(self):
        from nemoa.common import module

        with self.subTest(function = "curname"):
            test = module.curname() == 'nemoa.common.__test__'
            self.assertTrue(test)

        with self.subTest(function = "caller"):
            test = module.caller() == 'nemoa.common.__test__.test_common_module'
            self.assertTrue(test)

        with self.subTest(function = "submodules"):
            test = 'nemoa.common.module' in module.submodules(nemoa.common)
            self.assertTrue(test)

        with self.subTest(function = "get_module"):
            minst = module.get_module('nemoa.common.module')
            test = hasattr(minst, '__name__') \
                and minst.__name__ == 'nemoa.common.module'
            self.assertTrue(test)

        with self.subTest(function = "get_functions"):
            funcs = module.get_functions(minst)
            fname = 'nemoa.common.module.get_functions'
            test = fname in funcs
            test = test and len(module.get_functions(minst,
                name = 'get_functions')) == 1
            test = test and len(module.get_functions(minst, name = '')) == 0
            self.assertTrue(test)

        with self.subTest(function = "get_function"):
            finst = module.get_function(fname)
            test = type(finst).__name__ == 'function'
            self.assertTrue(test)

        with self.subTest(function = "get_kwargs"):
            fargs = module.get_kwargs(finst)
            test = 'details' in fargs
            self.assertTrue(test)

        with self.subTest(function = "locate_functions"):
            minst = module.get_module('nemoa.common')
            funcs = module.locate_functions(minst, name = 'locate_functions')
            test = len(funcs) == 1
            self.assertTrue(test)

    def test_common_ospath(self):
        from nemoa.common import ospath

        import os
        import tempfile
        import pathlib

        dname = str(pathlib.Path('a', 'b', 'c', 'd'))
        plike = (('a', ('b', 'c')), 'd', 'base.ext')
        stdir = tempfile.TemporaryDirectory().name

        with self.subTest(function = "cwd"):
            self.assertTrue(ospath.cwd())

        with self.subTest(function = "home"):
            self.assertTrue(ospath.home())

        with self.subTest(function = "clear"):
            self.assertTrue(ospath.clear('3/\nE{$5}.e') == '3E5.e')

        with self.subTest(function = "join"):
            val = ospath.join(('a', ('b', 'c')), 'd')
            self.assertTrue(val == dname)

        with self.subTest(function = "expand"):
            val = ospath.expand('%var1%/c', 'd',
                udict = {'var1': 'a/%var2%', 'var2': 'b'})
            self.assertTrue(val == dname)

        with self.subTest(function = "dirname"):
            self.assertTrue(ospath.dirname(*plike) == dname)

        with self.subTest(function = "filename"):
            self.assertTrue(ospath.filename(*plike) == 'base.ext')

        with self.subTest(function = "basename"):
            self.assertTrue(ospath.basename(*plike) == 'base')

        with self.subTest(function = "fileext"):
            self.assertTrue(ospath.fileext(*plike) == 'ext')

        with self.subTest(function = "mkdir"):
            self.assertTrue(ospath.mkdir(stdir))

        with self.subTest(function = "rmdir"):
            self.assertTrue(ospath.rmdir(stdir))

        with self.subTest(function = "cp"):
            self.assertTrue(True)

    def test_common_sysinfo(self):
        from nemoa.common import sysinfo

        with self.subTest(function = "hostname"):
            self.assertTrue(sysinfo.hostname())

        with self.subTest(function = "osname"):
            self.assertTrue(sysinfo.osname())

    def test_common_table(self):
        from nemoa.common import table

        import numpy as np

        a = np.array([(1., 2), (3., 4)], dtype=[('x', float), ('y', int)])
        b = np.array([('a'), ('b')], dtype=[('z', 'U4')])

        with self.subTest(function = "addcols"):
            self.assertTrue(table.addcols(a, b, 'z')['z'][0] == 'a')

    def test_common_text(self):
        from nemoa.common import text

        l = [('t', 'str'), (True, 'bool'), (1, 'int'), (.5, 'float'),
            ((1+1j), 'complex')]

        with self.subTest(function = "splitargs"):
            test = text.splitargs("f(1., 'a', b = 2)") \
                == ('f', (1.0, 'a'), {'b': 2})
            self.assertTrue(test)

        with self.subTest(function = "aslist"):
            test = text.aslist('a, 2, ()') == ['a', '2', '()'] \
                and text.aslist('[1, 2, 3]') == [1, 2, 3]
            self.assertTrue(test)

        with self.subTest(function = "astuple"):
            test = text.astuple('a, 2, ()') == ('a', '2', '()') \
                and text.astuple('(1, 2, 3)') == (1, 2, 3)
            self.assertTrue(test)

        with self.subTest(function = "asset"):
            test = text.asset('a, 2, ()') == {'a', '2', '()'} \
                and text.asset('{1, 2, 3}') == {1, 2, 3}
            self.assertTrue(test)

        with self.subTest(function = "asdict"):
            test = text.asdict("a = 'b', b = 1") == {'a': 'b', 'b': 1} \
                and text.asdict("'a': 'b', 'b': 1") == {'a': 'b', 'b': 1}
            self.assertTrue(test)

        for var, typ in l:
            with self.subTest(function = f"astype({str(var)}, {typ})"):
                test = text.astype(str(var), typ) == var
                self.assertTrue(test)
