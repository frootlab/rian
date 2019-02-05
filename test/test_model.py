# -*- coding: utf-8 -*-
# Copyright (c) 2013-2019 Patrick Michl
#
# This file is part of nemoa, https://frootlab.github.io/nemoa
#
#  nemoa is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  nemoa is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with
#  nemoa. If not, see <http://www.gnu.org/licenses/>.
#

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

import nemoa
from nemoa.base import otree
import test

class TestCase(test.GenericTest):
    def setUp(self) -> None:
        self.mode = nemoa.get('mode')
        self.workspace = nemoa.get('workspace')
        nemoa.set('mode', 'silent')
        # open workspace 'testsuite'
        nemoa.open('testsuite', base='site')

    def tearDown(self) -> None:
        # open previous workspace
        if nemoa.get('workspace') != self.workspace:
            nemoa.open(self.workspace)
        nemoa.set('mode', self.mode)

    def test_model_import(self) -> None:
        with self.subTest(filetype='npz'):
            model = nemoa.model.open('test', workspace='testsuite')
            self.assertTrue(otree.has_base(model, 'Model'))

    def test_model_ann(self) -> None:
        with self.subTest(step='create shallow ann'):
            model = nemoa.model.create(
                dataset='linear', network='shallow', system='ann')
            self.assertTrue(otree.has_base(model, 'Model'))

        with self.subTest(step='optimize shallow ann'):
            model.optimize()
            test = model.error < 0.1
            self.assertTrue(test)

    def test_model_dbn(self) -> None:
        with self.subTest(step='create dbn'):
            model = nemoa.model.create(
                dataset='linear', network='deep', system='dbn')
            self.assertTrue(otree.has_base(model, 'Model'))

        with self.subTest(step='optimize dbn'):
            model.optimize()
            test = model.error < 0.5
            self.assertTrue(test)
