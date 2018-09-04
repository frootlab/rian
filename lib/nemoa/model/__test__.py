# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa

from nemoa.common import classes, unittest

class TestSuite(unittest.TestSuite):

    def test_model_import(self):

        with self.subTest(filetype = 'npz'):
            model = nemoa.model.open('test', workspace = 'testsuite')
            self.assertTrue(classes.hasbase(model, 'Model'))

    def test_model_ann(self):

        with self.subTest(step = 'create shallow ann'):
            model = nemoa.model.create(
                dataset = 'linear', network = 'shallow', system = 'ann')
            self.assertTrue(classes.hasbase(model, 'Model'))

        with self.subTest(step = 'optimize shallow ann'):
            model.optimize()
            test = model.error < 0.1
            self.assertTrue(test)

    def test_model_dbn(self):

        with self.subTest(step = 'create dbn'):
            model = nemoa.model.create(
                dataset = 'linear', network = 'deep', system = 'dbn')
            self.assertTrue(classes.hasbase(model, 'Model'))

        with self.subTest(step = 'optimize dbn'):
            model.optimize()
            test = model.error < 0.5
            self.assertTrue(test)
