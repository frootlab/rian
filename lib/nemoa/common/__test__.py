# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa

class TestSuite(nemoa.common.unittest.TestSuite):

    def test_common_module(self):
        """Test functions in nemoa.common.module."""

        with self.subTest(function = "getcurname"):
            from nemoa.common.module import getcurname
            test = getcurname() == 'nemoa.common.__test__'
            self.assertTrue(test)
        with self.subTest(function = "getsubmodules"):
            from nemoa.common.module import getsubmodules
            mlist = getsubmodules(nemoa.common)
            test = 'nemoa.common.module' in mlist
            self.assertTrue(test)
        with self.subTest(function = "getmodule"):
            from nemoa.common.module import getmodule
            minst = getmodule('nemoa.common.module')
            test = hasattr(minst, '__name__') \
                and minst.__name__ == 'nemoa.common.module'
            self.assertTrue(test)
        with self.subTest(function = "getfunctions"):
            from nemoa.common.module import getfunctions
            funcs = getfunctions(minst)
            fname = 'nemoa.common.module.getfunctions'
            test = fname in funcs
            test &= len(getfunctions(minst, name = 'getfunctions')) == 1
            test &= len(getfunctions(minst, name = '')) == 0
            self.assertTrue(test)
        with self.subTest(function = "getfunction"):
            from nemoa.common.module import getfunction
            finst = getfunction(fname)
            test = type(finst).__name__ == 'function'
            self.assertTrue(test)
        with self.subTest(function = "getfunckwargs"):
            from nemoa.common.module import getfunckwargs
            fargs = getfunckwargs(finst)
            test = 'details' in fargs
            self.assertTrue(test)

    def test_common_dict(self):
        with self.subTest(function = "merge"):
            d1, d2, d3 = {'a': 1}, {'a': 2, 'b': 2}, {'c': 3}
            test = nemoa.common.dict.merge(d1, d2, d3)['a'] == 1
            test &= len(d3) == 1
            self.assertTrue(test)
