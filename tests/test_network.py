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
from flab.base import otree
from flab.base import test

class TestCase(test.GenericTest):
    def test_network_import(self) -> None:
        with self.subTest(filetype='ini'):
            network = nemoa.network.open('deep', workspace='testsuite')
            self.assertTrue(otree.has_base(network, 'Network'))

    def test_network_create(self) -> None:
        with self.subTest(create='autoencoder'):
            network = nemoa.network.create('autoencoder',
                columns=['v1', 'v2', 'v3'], shape=[6, 3, 6])
            self.assertTrue(otree.has_base(network, 'Network'))

        with self.subTest(create='factor'):
            network = nemoa.network.create('factor',
                visible_nodes=['v1', 'v2', 'v3'], visible_type='gauss',
                hidden_nodes=['h1', 'h2'], hidden_type='sigmoid')
            self.assertTrue(otree.has_base(network, 'Network'))
