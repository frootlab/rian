# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa

from nemoa.common.unittest import TestSuite as NmTestSuite

class TestSuite(NmTestSuite):

    def test_common_compress(self):
        import nemoa.common.compress

        import os
        import tempfile

        d = {True: 'a', 2: {None: 0.5}}
        s = b'eNprYK4tZNDoiGBkYGBILGT0ZqotZPJzt3/AAAbFpXoAgyIHVQ=='
        f = tempfile.NamedTemporaryFile().name

        with self.subTest(function = "dumps"):
            func = nemoa.common.compress.dumps
            test = func(d) == s
            self.assertTrue(test)
        with self.subTest(function = "loads"):
            func = nemoa.common.compress.loads
            test = func(s) == d
            self.assertTrue(test)
        with self.subTest(function = "dump"):
            func = nemoa.common.compress.dump
            func(d, f)
            test = os.path.exists(f)
            self.assertTrue(test)
        with self.subTest(function = "load"):
            func = nemoa.common.compress.load
            test = func(f) == d
            self.assertTrue(test)

        if os.path.exists(f): os.remove(f)

    def test_common_csvfile(self):
        import nemoa.common.csvfile

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
            func = nemoa.common.csvfile.save
            test = func(f, data, header = header,
                labels = labels, delim = delim)
            self.assertTrue(test)
        with self.subTest(function = "get_header"):
            func = nemoa.common.csvfile.get_header
            test = func(f) == header
            self.assertTrue(test)
        with self.subTest(function = "get_delim"):
            func = nemoa.common.csvfile.get_delim
            test = func(f) == delim
            self.assertTrue(test)
        with self.subTest(function = "get_labels"):
            func = nemoa.common.csvfile.get_labels
            test = func(f) == labels
            self.assertTrue(test)
        with self.subTest(function = "get_labelcolumn"):
            func = nemoa.common.csvfile.get_labelcolumn
            test = func(f) == 0
            self.assertTrue(test)
        with self.subTest(function = "load"):
            func = nemoa.common.csvfile.load
            rval = func(f)
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
        import nemoa.common.graph

        import networkx

        l1 = [(1, 3), (1, 4), (2, 3), (2, 4)]
        G1 = networkx.DiGraph(l1, directed = True)
        networkx.set_node_attributes(G1, {
            1: {'layer': 'i', 'layer_id': 0 , 'layer_sub_id': 0},
            2: {'layer': 'i', 'layer_id': 0 , 'layer_sub_id': 1},
            3: {'layer': 'o', 'layer_id': 1 , 'layer_sub_id': 0},
            4: {'layer': 'o', 'layer_id': 1 , 'layer_sub_id': 1} })
        networkx.set_edge_attributes(G1, {
            (1, 3): {'weight': 0.1}, (1, 4): {'weight': 0.9},
            (2, 3): {'weight': 0.9}, (2, 4): {'weight': 0.1} })
        pos1 = {1: (.0, .25), 2: (.0, .75), 4: (1., .25), 3: (1., .75)}
        pos2 = {1: (.25, 1.), 2: (.75, 1.), 4: (.25, .0), 3: (.75, .0)}
        pos3 = {1: (4., 2.), 2: (4., 16.), 4: (32., 2.), 3: (32., 16.)}
        l2 = [(1, 2), (2, 3), (3, 4), (4, 1)]
        G2 = networkx.DiGraph(l2)

        with self.subTest(function = "is_directed"):
            func = nemoa.common.graph.is_directed
            test = func(G1) and not func(G2)
            self.assertTrue(test)
        with self.subTest(function = "is_layered"):
            func = nemoa.common.graph.is_layered
            test = func(G1) and not func(G2)
            self.assertTrue(test)
        with self.subTest(function = "get_layers"):
            func = nemoa.common.graph.get_layers
            test = func(G1) == [[1, 2], [3, 4]]
            self.assertTrue(test)
        with self.subTest(function = "get_groups"):
            func = nemoa.common.graph.get_groups
            test = func(G1, attribute = 'layer') \
                == {'': [], 'i': [1, 2], 'o': [3, 4]}
            self.assertTrue(test)
        with self.subTest(function = "get_layer_layout"):
            func = nemoa.common.graph.get_layer_layout
            test = func(G1, direction = 'right') == pos1 \
                and func(G1, direction = 'down') == pos2
            self.assertTrue(test)
        with self.subTest(function = "rescale_layout"):
            func = nemoa.common.graph.rescale_layout
            test = func(pos1, size = (40, 20), \
                padding = (.2, .2, .1, .1)) == pos3
            self.assertTrue(test)
        with self.subTest(function = "get_scaling_factor"):
            func = nemoa.common.graph.get_scaling_factor
            test = int(func(pos3)) == 9
            self.assertTrue(test)
        with self.subTest(function = "get_layout_normsize"):
            func = nemoa.common.graph.get_layout_normsize
            test = int(func(pos3).get('node_size', 0.)) == 4
            self.assertTrue(test)
        with self.subTest(function = "get_node_layout"):
            func = nemoa.common.graph.get_node_layout
            test = isinstance(func('observable').get('color', None), str)
            self.assertTrue(test)
        with self.subTest(function = "get_layout"):
            func = nemoa.common.graph.get_layout
            test = func(G1).keys() == func(G2).keys()
            test = test and func(G1, 'layer', direction = 'right') == pos1
            test = test and func(G1, 'layer', direction = 'down') == pos2
            self.assertTrue(test)

    def test_common_module(self):
        import nemoa.common.module

        with self.subTest(function = "get_curname"):
            func = nemoa.common.module.get_curname
            test = func() == 'nemoa.common.__test__'
            self.assertTrue(test)
        with self.subTest(function = "get_submodules"):
            func = nemoa.common.module.get_submodules
            test = 'nemoa.common.module' in func(nemoa.common)
            self.assertTrue(test)
        with self.subTest(function = "get_module"):
            func = nemoa.common.module.get_module
            minst = func('nemoa.common.module')
            test = hasattr(minst, '__name__') \
                and minst.__name__ == 'nemoa.common.module'
            self.assertTrue(test)
        with self.subTest(function = "get_functions"):
            func = nemoa.common.module.get_functions
            funcs = func(minst)
            fname = 'nemoa.common.module.get_functions'
            test = fname in funcs
            test &= len(func(minst, name = 'get_functions')) == 1
            test &= len(func(minst, name = '')) == 0
            self.assertTrue(test)
        with self.subTest(function = "get_function"):
            func = nemoa.common.module.get_function
            finst = func(fname)
            test = type(finst).__name__ == 'function'
            self.assertTrue(test)
        with self.subTest(function = "get_kwargs"):
            func = nemoa.common.module.get_kwargs
            fargs = func(finst)
            test = 'details' in fargs
            self.assertTrue(test)
        with self.subTest(function = "locate_functions"):
            func = nemoa.common.module.locate_functions
            minst = nemoa.common.module.get_module('nemoa.common')
            funcs = func(minst, name = 'locate_functions')
            test = len(funcs) == 1
            self.assertTrue(test)
