# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

import nemoa
from nemoa.base import entity
from nemoa.test import BaseTestCase

class TestCase(BaseTestCase):
    def setUp(self):
        self.mode = nemoa.get('mode')
        self.workspace = nemoa.get('workspace')
        nemoa.set('mode', 'silent')
        # open workspace 'testsuite'
        nemoa.open('testsuite', base='site')

    def tearDown(self):
        # open previous workspace
        if nemoa.get('workspace') != self.workspace:
            nemoa.open(self.workspace)
        nemoa.set('mode', self.mode)

    def test_model_import(self):
        with self.subTest(filetype='npz'):
            model = nemoa.model.open('test', workspace='testsuite')
            self.assertTrue(entity.has_base(model, 'Model'))

    def test_model_ann(self):
        with self.subTest(step='create shallow ann'):
            model = nemoa.model.create(
                dataset='linear', network='shallow', system='ann')
            self.assertTrue(entity.has_base(model, 'Model'))

        with self.subTest(step='optimize shallow ann'):
            model.optimize()
            test = model.error < 0.1
            self.assertTrue(test)

    def test_model_dbn(self):
        with self.subTest(step='create dbn'):
            model = nemoa.model.create(
                dataset='linear', network='deep', system='dbn')
            self.assertTrue(entity.has_base(model, 'Model'))

        with self.subTest(step='optimize dbn'):
            model.optimize()
            test = model.error < 0.5
            self.assertTrue(test)
