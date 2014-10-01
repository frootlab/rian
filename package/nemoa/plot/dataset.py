# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import numpy

class histogram(nemoa.plot.base.plot):

    @staticmethod
    def _settings(): return {
        'path': ('dataset', ),
        'units': (None, None),
        'bins': 120,
        'facecolor': 'lightgrey',
        'edgecolor': 'black',
        'histtype': 'bar',
        'linewidth': 0.5 }

    def _create(self, model):

        # create data (numpy 1-d array)
        data = model.dataset.data().flatten()

        # create plot
        return nemoa.common.plot.histogram(data, **self.settings)
