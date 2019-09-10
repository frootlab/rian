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
    def test_network_import(self) -> None:
        with self.subTest(filetype='ini'):
            network = rian.network.open('deep', workspace='testsuite')
            self.assertTrue(otree.has_base(network, 'Network'))

    def test_network_create(self) -> None:
        with self.subTest(create='autoencoder'):
            network = rian.network.create('autoencoder',
                columns=['v1', 'v2', 'v3'], shape=[6, 3, 6])
            self.assertTrue(otree.has_base(network, 'Network'))

        with self.subTest(create='factor'):
            network = rian.network.create('factor',
                visible_nodes=['v1', 'v2', 'v3'], visible_type='gauss',
                hidden_nodes=['h1', 'h2'], hidden_type='sigmoid')
            self.assertTrue(otree.has_base(network, 'Network'))
