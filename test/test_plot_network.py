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
"""Unittests for module 'nemoa.plot.network'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import networkx as nx
from nemoa.plot import network
import test

#
# Test Cases
#

class TestNetwork(test.ModuleTest):
    module = network

    def setUp(self) -> None:
        self.G = nx.DiGraph([(1, 3), (1, 4), (2, 3), (2, 4)], directed=True)
        nx.set_node_attributes(self.G, {
            1: {'layer': 'i', 'layer_id': 0, 'layer_sub_id': 0},
            2: {'layer': 'i', 'layer_id': 0, 'layer_sub_id': 1},
            3: {'layer': 'o', 'layer_id': 1, 'layer_sub_id': 0},
            4: {'layer': 'o', 'layer_id': 1, 'layer_sub_id': 1}})
        nx.set_edge_attributes(self.G, {
            (1, 3): {'weight': 0.1}, (1, 4): {'weight': 0.9},
            (2, 3): {'weight': 0.9}, (2, 4): {'weight': 0.1}})
        self.pos1 = {1: (.0, .25), 2: (.0, .75), 4: (1., .25), 3: (1., .75)}
        self.pos2 = {1: (.25, 1.), 2: (.75, 1.), 4: (.25, .0), 3: (.75, .0)}
        self.pos3 = {1: (4., 2.), 2: (4., 16.), 4: (32., 2.), 3: (32., 16.)}

    def test_Graph2D(self) -> None:
        # TODO (patrick.michl@gmail.com): Write unittest for completeness
        # of classes
        pass

    def test_Graph2D_get_node_layout(self) -> None:
        color = network.Graph2D.get_node_layout('observable')['color']
        self.assertIsInstance(color, str)

    def test_Graph2D_get_layout_normsize(self) -> None:
        normsize = network.Graph2D.get_layout_normsize(self.pos3)
        self.assertEqual(int(normsize['node_size']), 4)

    def test_Graph2D_get_scaling_factor(self) -> None:
        scaling = int(network.Graph2D.get_scaling_factor(self.pos3))
        self.assertEqual(scaling, 9)

    def test_Graph2D_rescale_layout(self) -> None:
        layout = network.Graph2D.rescale_layout(
            self.pos1, size=(40, 20), padding=(.2, .2, .1, .1))
        self.assertEqual(layout, self.pos3)

    def test_Graph2D_get_layout(self) -> None:
        layout = network.Graph2D.get_layout(self.G, 'layer', direction='right')
        self.assertEqual(layout, self.pos1)

    def test_Graph2D_get_layer_layout(self) -> None:
        layout = network.Graph2D.get_layer_layout(self.G, direction='right')
        self.assertEqual(layout, self.pos1)
        layout = network.Graph2D.get_layer_layout(self.G, direction='down')
        self.assertEqual(layout, self.pos2)
