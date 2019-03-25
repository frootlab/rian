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
"""Markov Random Field (MRF) analysis.

This module includes various functions for the analysis of undirected graphical
models, which are known as Markov Random Fields or Markov Networks. These
models include recurrent neural networks (RNN), restricted Boltzmann Machines
(RBM) and Deep Boltzmann Machines (DBM).

The supported categories of analysis functions are:

    (1) "Sampler": Matrix valued statistical inference functions
        Return numpy ndarray of shape (d, n), where d is the size of the sample
        and n the number of observables within the model.
    (2) "Sample statistics": Vectorial statistical inference functions
        Return numpy array of shape (1, n), where n is the number of
        observables within the model.
    (3) "Objective functions": Scalar statistical inference functions, that can
        be used for the determination of local optima.
        Return scalar value
    (4) "Association measures": Matrix valued statistical association measures
        Return numpy ndarray of shape (n, n), where n is the number of
        observables within the model.

"""
__copyright__ = '2019 Frootlab'
__license__ = 'GPLv3'
__docformat__ = 'google'
__author__ = 'Frootlab Developers'
__email__ = 'contact@frootlab.org'
__authors__ = ['Patrick Michl <patrick.michl@frootlab.org>']

import numpy
import nemoa
from flib.base import catalog

#
# (1) Sampler for Markov Random Fields
#

@catalog.objective(
    name     = 'error',
    title    = 'Average Reconstruction Error',
    category = 'model',
    args     = 'all',
    formater = lambda val: '%.3f' % (val),
    optimum  = 'min'
)
def modelerror(model, *args, **kwds):
    """Mean data reconstruction error of output units."""
    return numpy.mean(uniterror(model, *args, **kwds))

@catalog.custom(
    name     = 'energy',
    category = 'model',
    args     = 'all',
    formater = lambda val: '%.3f' % (val),
    optimum  = 'min'
)
def modelenergy(model, data, *args, **kwds):
    """Sum of local link and unit energies."""

    mapping = list(model._get_mapping())
    energy = 0.

    # sum local unit energies
    for i in range(1, len(mapping) + 1):
        energy += unitenergy(model, data[0],
            mapping = tuple(mapping[:i])).sum(axis = 1)

    # sum local link energies
    for i in range(1, len(mapping)):
        energy += linksenergy(model, data[0],
            mapping = tuple(mapping[:i + 1])).sum(axis = (1, 2))

    # calculate (pseudo) energy of system
    return numpy.log(1. + numpy.exp(-energy).sum())

@catalog.custom(
    name     = 'energy',
    category = 'units',
    args     = 'input',
    retfmt   = 'scalar',
    formater = lambda val: '%.3f' % (val),
    plot     = 'diagram'
)
def unitenergy(model, data, mapping = None):
    """Unit energies of target units.

    Args:
        data: numpy array containing source data corresponding to
            the source unit layer (first argument of the mapping)
        mapping: n-tuple of strings containing the mapping
            from source unit layer (first argument of tuple)
            to target unit layer (last argument of tuple)

    Returns:
        Numpy array of shape (data, targets).

    """

    # set mapping from input layer to output layer (if not set)
    if mapping is None: mapping = model.system._get_mapping()
    data = unitexpect(model, data, mapping)
    return model.system._units[mapping[-1]].energy(data)

@catalog.custom(
    name     = 'links_energy',
    category = ('system', 'links', 'evaluation'),
    args     = 'input',
    retfmt   = 'scalar',
    formater = lambda val: '%.3f' % (val),
    plot     = 'diagram'
)
def linksenergy(model, data, mapping = None, **kwds):
    """Return link energies of a layer.

    Args:
        mapping: tuple of strings containing the mapping
            from source unit layer (first argument of tuple)
            to target unit layer (last argument of tuple)

    """

    if len(mapping) == 1:
        # TODO
        raise ValueError("""sorry: bad implementation of
            links_energy""")
    elif len(mapping) == 2:
        sdata = data
        tdata = unitvalues(model, sdata, mapping)
    else:
        sdata = unitexpect(model, data, mapping[0:-1])
        tdata = unitvalues(model, sdata, mapping[-2:])

    fullmapping = model.system._get_mapping()
    sid = fullmapping.index(mapping[-2])
    tid = fullmapping.index(mapping[-1])
    src = self._units[mapping[-2]].params
    tgt = self._units[mapping[-1]].params

    if (sid, tid) in model.system._params['links']:
        links = model.system._params['links'][(sid, tid)]
        return nemoa.system.commons.links.Links.energy(
            sdata, tdata, src, tgt, links)
    elif (tid, sid) in model.system._params['links']:
        links = model.system._params['links'][(tid, sid)]
        return nemoa.system.commons.links.Links.energy(
            tdata, sdata, tgt, src, links)
