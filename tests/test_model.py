# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 Frootlab
# Copyright (C) 2013-2019 Patrick Michl
#
# This file is part of Frootlab Rian, https://www.frootlab.org/rian
#
#  Rian is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rian is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with
#  Rian. If not, see <http://www.gnu.org/licenses/>.
#

__copyright__ = '2019 Frootlab'
__license__ = 'GPLv3'
__docformat__ = 'google'
__author__ = 'Frootlab Developers'
__email__ = 'contact@frootlab.org'
__authors__ = ['Patrick Michl <patrick.michl@frootlab.org>']

import rian
from hup.base import otree
from hup.base import test

class TestCase(test.GenericTest):
    def setUp(self) -> None:
        self.mode = rian.get('mode')
        self.workspace = rian.get('workspace')
        rian.set('mode', 'silent')
        # open workspace 'testsuite'
        rian.open('testsuite', base='site')

    def tearDown(self) -> None:
        # open previous workspace
        if rian.get('workspace') != self.workspace:
            rian.open(self.workspace)
        rian.set('mode', self.mode)

    def test_model_import(self) -> None:
        with self.subTest(filetype='npz'):
            model = rian.model.open('test', workspace='testsuite')
            self.assertTrue(otree.has_base(model, 'Model'))

    def test_model_ann(self) -> None:
        with self.subTest(step='create shallow ann'):
            model = rian.model.create(
                dataset='linear', network='shallow', system='ann')
            self.assertTrue(otree.has_base(model, 'Model'))

        with self.subTest(step='optimize shallow ann'):
            model.optimize()
            test = model.error < 0.1
            self.assertTrue(test)

    def test_model_dbn(self) -> None:
        with self.subTest(step='create dbn'):
            model = rian.model.create(
                dataset='linear', network='deep', system='dbn')
            self.assertTrue(otree.has_base(model, 'Model'))

        with self.subTest(step='optimize dbn'):
            model.optimize()
            test = model.error < 0.5
            self.assertTrue(test)
