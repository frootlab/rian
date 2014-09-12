#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nemoa, nemoa.plot.base, numpy

class histogram(nemoa.plot.base.plot):

    @staticmethod
    def _default(): return {
        'output': 'file',
        'fileformat': 'pdf',
        'path': ('dataset'),
        'dpi': 300,
        'backgroundColor': 'none',
        'graphCaption': True,
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

        # set title of plot
        if self.settings['graphCaption']: self.settings['title'] = \
            'Distribution'

        # create data (numpy 1-d array)
        data = numpy.hstack(model.getData(
            layer = self.settings['layer'],
            transform = self.settings['transform'])).flatten()

        # create plot
        return nemoa.common.plot.histogram(data, **self.settings)
