# -*- coding: utf-8 -*-
"""Restricted Boltzmann Machine (RBM) Evaluation.

This module includes various implementations for quantifying structural
and statistical values of whole restricted boltzmann machines and parts
of it. These methods include:

    (a) data based methods like data manipulation tests
    (b) graphical methods on weighted graphs
    (c) unit function based methods like

"""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

from nemoa.model.evaluation.ann import ANN as EvalationOfANN

class RBM(EvalationOfANN):
    pass

class GRBM(RBM):
    pass
