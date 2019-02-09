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
"""Unittests for module 'nemoa.math.vector'."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from nemoa.math import vector, test

#
# Test Cases
#

class TestVector(test.MathModule):
    module = vector

    def test_Norm(self) -> None:
        pass # Data Class

    def test_Distance(self) -> None:
        pass # Data Class

    def test_norms(self) -> None:
        norms = vector.norms()
        self.assertIsInstance(norms, list)
        self.assertTrue(norms)

    def test_length(self) -> None:
        for norm in vector.norms():
            with self.subTest(norm=norm):
                self.assertIsVectorNorm(vector.length, norm=norm)

    def test_p_norm(self) -> None:
        for p in range(1, 5):
            with self.subTest(p=p):
                self.assertIsVectorNorm(vector.p_norm, p=p)

    def test_norm_1(self) -> None:
        self.assertIsVectorNorm(vector.norm_1)

    def test_euclid_norm(self) -> None:
        self.assertIsVectorNorm(vector.euclid_norm)

    def test_max_norm(self) -> None:
        self.assertIsVectorNorm(vector.max_norm)

    def test_pmean_norm(self) -> None:
        for p in range(1, 5):
            with self.subTest(p=p):
                self.assertIsVectorNorm(vector.pmean_norm, p=p)

    def test_amean_norm(self) -> None:
        self.assertIsVectorNorm(vector.amean_norm)

    def test_qmean_norm(self) -> None:
        self.assertIsVectorNorm(vector.qmean_norm)

    def test_distances(self) -> None:
        distances = vector.distances()
        self.assertIsInstance(distances, list)
        self.assertTrue(distances)

    def test_distance(self) -> None:
        for name in vector.distances():
            with self.subTest(name=name):
                self.assertIsVectorDistance(vector.distance, name=name)

    def test_chebyshev(self) -> None:
        self.assertIsVectorDistance(vector.chebyshev)

    def test_manhattan(self) -> None:
        self.assertIsVectorDistance(vector.manhattan)

    def test_minkowski(self) -> None:
        self.assertIsVectorDistance(vector.minkowski)

    def test_amean_dist(self) -> None:
        self.assertIsVectorDistance(vector.amean_dist)

    def test_qmean_dist(self) -> None:
        self.assertIsVectorDistance(vector.qmean_dist)

    def test_pmean_dist(self) -> None:
        for p in range(1, 5):
            with self.subTest(p=p):
                self.assertIsVectorDistance(vector.pmean_dist, p=p)

    def test_euclid_dist(self) -> None:
        self.assertIsVectorDistance(vector.euclid_dist)
