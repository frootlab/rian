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

    def test_common_module(self):
        with self.subTest(function = "get_curname"):
            from nemoa.common.module import get_curname
            test = get_curname() == 'nemoa.common.__test__'
            self.assertTrue(test)
        with self.subTest(function = "get_submodules"):
            from nemoa.common.module import get_submodules
            mlist = get_submodules(nemoa.common)
            test = 'nemoa.common.module' in mlist
            self.assertTrue(test)
        with self.subTest(function = "get_module"):
            from nemoa.common.module import get_module
            minst = get_module('nemoa.common.module')
            test = hasattr(minst, '__name__') \
                and minst.__name__ == 'nemoa.common.module'
            self.assertTrue(test)
        with self.subTest(function = "get_functions"):
            from nemoa.common.module import get_functions
            funcs = get_functions(minst)
            fname = 'nemoa.common.module.get_functions'
            test = fname in funcs
            test &= len(get_functions(minst, name = 'get_functions')) == 1
            test &= len(get_functions(minst, name = '')) == 0
        with self.subTest(function = "get_function"):
            from nemoa.common.module import get_function
            finst = get_function(fname)
            test = type(finst).__name__ == 'function'
            self.assertTrue(test)
        with self.subTest(function = "get_kwargs"):
            from nemoa.common.module import get_kwargs
            fargs = get_kwargs(finst)
            test = 'details' in fargs
            self.assertTrue(test)
            self.assertTrue(test)
        with self.subTest(function = "locate_functions"):
            from nemoa.common.module import locate_functions
            funcs = locate_functions(get_module('nemoa.common'),
                name = 'locate_functions')
            test = len(funcs) == 1
            self.assertTrue(test)

    def test_common_dict(self):
        with self.subTest(function = "merge"):
            d1, d2, d3 = {'a': 1}, {'a': 2, 'b': 2}, {'c': 3}
            test = nemoa.common.dict.merge(d1, d2, d3)['a'] == 1
            test &= len(d3) == 1
            self.assertTrue(test)
