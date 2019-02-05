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
"""Unittests for module 'nemoa.math.matrix'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from nemoa.math import matrix
import test

#
# Test Cases
#

class TestMatrix(test.MathTest, test.ModuleTest):
    module = matrix

    def test_Norm(self) -> None:
        pass # Not required

    def test_Distance(self) -> None:
        pass # Not required

    def test_norms(self) -> None:
        norms = matrix.norms()
        self.assertIsInstance(norms, list)
        self.assertTrue(norms)

    def test_norm(self) -> None:
        for name in matrix.norms():
            with self.subTest(name=name):
                self.assertIsMatrixNorm(matrix.norm, name=name)

    def test_frob_norm(self) -> None:
        self.assertIsMatrixNorm(matrix.frob_norm)

    def test_pq_norm(self) -> None:
        for p in range(1, 5):
            for q in range(1, 5):
                with self.subTest(p=p, q=q):
                    self.assertIsMatrixNorm(matrix.pq_norm, p=p, q=q)

    def test_distances(self) -> None:
        distances = matrix.distances()
        self.assertIsInstance(distances, list)
        self.assertTrue(distances)

    def test_distance(self) -> None:
        for name in matrix.distances():
            with self.subTest(name=name):
                self.assertIsMatrixDistance(matrix.distance, name=name)

    def test_frob_dist(self) -> None:
        self.assertIsMatrixDistance(matrix.frob_dist)

    def test_pq_dist(self) -> None:
        for p in range(1, 5):
            for q in range(1, 5):
                with self.subTest(p=p, q=q):
                    self.assertIsMatrixDistance(matrix.pq_dist, p=p, q=q)
