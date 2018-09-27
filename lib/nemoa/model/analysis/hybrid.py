# -*- coding: utf-8 -*-
"""Hybrid Propabilistic Graphical Model analysis.

This module includes various functions for the analysis of hybrid probabilistic
graphical models with directed and undirected dependencies.
These models include Chain Graph Models [1].

[1] Drton (2009), "Discrete chain graph models"

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

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

import nemoa
import numpy
