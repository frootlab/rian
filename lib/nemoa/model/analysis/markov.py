# -*- coding: utf-8 -*-
"""Markov random field analysis.

This module includes various implementations for quantifying structural
and statistical values for the evaluation of undirected graphical models.
These methods include:

    (a) data based methods like data manipulation tests
    (b) graphical methods on weighted graphs
    (c) unit function based methods like

"""

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import numpy

@nemoa.common.decorators.objective(
    name     = 'error',
    title    = 'Average Reconstruction Error',
    category = 'model',
    args     = 'all',
    formater = lambda val: '%.3f' % (val),
    optimum  = 'min'
)
def modelerror(model, *args, **kwargs):
    """Mean data reconstruction error of output units."""
    return numpy.mean(uniterror(model, *args, **kwargs))
