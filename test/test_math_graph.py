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
"""Unittests for module 'nemoa.math.graph'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import networkx as nx
from nemoa.math import graph
import test

#
# Test Cases
#

class TestGraph(test.ModuleTest):
    """Testsuite for modules within the package 'nemoa.math.graph'."""

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

    def test_is_directed(self) -> None:
        self.assertTrue(graph.is_directed(self.G))

    def test_is_layered(self) -> None:
        self.assertTrue(graph.is_layered(self.G))

    def test_get_layers(self) -> None:
        layers = graph.get_layers(self.G)
        self.assertEqual(layers, [[1, 2], [3, 4]])

    def test_get_groups(self) -> None:
        groups = graph.get_groups(self.G, attribute='layer')
        self.assertEqual(groups, {'': [], 'i': [1, 2], 'o': [3, 4]})
