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
"""Propabilistic Graphical Model (PGM) analysis.

This module includes generic functions for the analysis of probabilistic
graphical models.

The supported categories of analysis functions are:

    (1) Sampler: Matrix valued statistical inference functions
        Returns numpy arrays of shape (d, n), where n is the number of
        target observables and d the size of the sample.
    (2) Sample statistics: Vectorial statistical inference functions
        Returns numpy arrays of shape (1, n), where n is the number of
        target observables
    (3) Objective functions: Scalar statistical inference functions
        Returns scalar value, that can be used to determin local optima
    (4) Association measures: Matrix valued statistical association measures
        Returns numpy arrays of shape (n, n), where n is the number of
        observables

"""
__copyright__ = '2019 Frootlab'
__license__ = 'GPLv3'
__docformat__ = 'google'
__author__ = 'Frootlab Developers'
__email__ = 'contact@frootlab.org'
__authors__ = ['Patrick Michl <patrick.michl@frootlab.org>']

import nemoa
import numpy
