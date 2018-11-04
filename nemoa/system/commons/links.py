# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

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
