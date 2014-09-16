#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'patrick.michl@gmail.com'

import nemoa
import nemoa.plot.base
import numpy

class histogram(nemoa.plot.base.plot):

    @staticmethod
    def _settings(): return {
        'path': ('dataset', ),
        'units': (None, None),
        'transform': None,
        'statistics': 10000,
        'layer': None,
        'bins': 120,
        'facecolor': 'lightgrey',
        'edgecolor': 'black',
        'histtype': 'bar',
        'linewidth': 0.5 }

    def _create(self, model):

        # create data (numpy 1-d array)
        data = numpy.hstack(model.getData(
            layer = self.settings['layer'],
            transform = self.settings['transform'])).flatten()

        # create plot
        return nemoa.common.plot.histogram(data, **self.settings)
