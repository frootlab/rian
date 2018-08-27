# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa

from nemoa.common.unittest import TestSuite as NmTestSuite

class TestSuite(NmTestSuite):

    def test_common_iozip(self):
        from nemoa.common import iozip

        import os
        import tempfile

        d = {True: 'a', 2: {None: 0.5}}
        s = b'eNprYK4tZNDoiGBkYGBILGT0ZqotZPJzt3/AAAbFpXoAgyIHVQ=='
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

    def test_common_iocsv(self):
        from nemoa.common import iocsv

        import numpy
        import os
        import tempfile

        f = tempfile.NamedTemporaryFile().name + '.csv'

        header = '-*- coding: utf-8 -*-'
        data = numpy.array(
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
            test = isinstance(rval, numpy.ndarray) \
                and (rval['col1'] == data['col1']).any() \
                and (rval['col2'] == data['col2']).any()
            self.assertTrue(test)

        if os.path.exists(f): os.remove(f)

    def test_common_dict(self):
        import nemoa.common.dict

        import numpy

        d = {('a', 'b'): 1.}
        a = numpy.array([[0., 1.], [0., 0.]])
        axes = [['a', 'b'], ['a', 'b']]
        na = 0.

        with self.subTest(function = "dict_to_array"):
            func = nemoa.common.dict.dict_to_array
            rval = func(d, axes = axes, na = na)
            test = (rval == a).any()
            self.assertTrue(test)
        with self.subTest(function = "array_to_dict"):
            func = nemoa.common.dict.array_to_dict
            rval = func(a, axes = axes, na = na)
            test = rval == d
            self.assertTrue(test)
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
            4: {'layer': 'o', 'layer_id': 1 , 'layer_sub_id': 1} })
        networkx.set_edge_attributes(G, {
            (1, 3): {'weight': 0.1}, (1, 4): {'weight': 0.9},
            (2, 3): {'weight': 0.9}, (2, 4): {'weight': 0.1} })
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

    def test_common_module(self):
        from nemoa.common import module

        with self.subTest(function = "get_curname"):
            test = module.get_curname() == 'nemoa.common.__test__'
            self.assertTrue(test)
        with self.subTest(function = "get_submodules"):
            test = 'nemoa.common.module' in module.get_submodules(nemoa.common)
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
