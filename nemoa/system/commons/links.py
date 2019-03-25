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
import numpy

class Links:
    """Class to unify common ann link attributes."""

    params = {}

    def __init__(self): pass

    @staticmethod
    def energy(dSrc, dTgt, src, tgt, links, calc = 'mean'):
        """Return link energy as numpy array."""

        if src['class'] == 'gauss':
            M = - links['A'] * links['W'] \
                / numpy.sqrt(numpy.exp(src['lvar'])).T
        elif src['class'] == 'sigmoid':
            M = - links['A'] * links['W']
        else: raise ValueError('unsupported unit class')

        return numpy.einsum('ij,ik,jk->ijk', dSrc, dTgt, M)

    @staticmethod
    def get_updates(data, model):
        """Return weight updates of a link layer."""

        D = numpy.dot(data[0].T, data[1]) / float(data[1].size)
        M = numpy.dot(model[0].T, model[1]) / float(data[1].size)

        return { 'W': D - M }

    @staticmethod
    def get_updates_delta(data, delta):

        return { 'W': -numpy.dot(data.T, delta) / float(data.size) }
