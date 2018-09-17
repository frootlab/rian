# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa

from nemoa.common import ntest

class TestSuite(ntest.TestSuite):

    def test_model_import(self):
        from nemoa.common import nclass

        with self.subTest(filetype = 'npz'):
            model = nemoa.model.open('test', workspace = 'testsuite')
            self.assertTrue(nclass.hasbase(model, 'Model'))

    def test_model_ann(self):
        from nemoa.common import nclass

        with self.subTest(step = 'create shallow ann'):
            model = nemoa.model.create(
                dataset = 'linear', network = 'shallow', system = 'ann')
            self.assertTrue(nclass.hasbase(model, 'Model'))

        with self.subTest(step = 'optimize shallow ann'):
            model.optimize()
            test = model.error < 0.1
            self.assertTrue(test)

    def test_model_dbn(self):
        from nemoa.common import nclass

        with self.subTest(step = 'create dbn'):
            model = nemoa.model.create(
                dataset = 'linear', network = 'deep', system = 'dbn')
            self.assertTrue(nclass.hasbase(model, 'Model'))

        with self.subTest(step = 'optimize dbn'):
            model.optimize()
            test = model.error < 0.5
            self.assertTrue(test)
