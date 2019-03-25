# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 Frootlab
# Copyright (C) 2013-2019 Patrick Michl
#
# This file is part of Nemoa, https://www.frootlab.org/nemoa
#
#  Nemoa is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Nemoa is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with
#  Nemoa. If not, see <http://www.gnu.org/licenses/>.
#

__copyright__ = '2019 Frootlab'
__license__ = 'GPLv3'
__docformat__ = 'google'
__author__ = 'Frootlab Developers'
__email__ = 'contact@frootlab.org'
__authors__ = ['Patrick Michl <patrick.michl@frootlab.org>']

import nemoa
from flib.base import otree
from flib.base import test

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
