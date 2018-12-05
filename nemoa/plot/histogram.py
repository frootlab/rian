# -*- coding: utf-8 -*-
"""Plot Histogram."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from nemoa.plot import Plot

class Histogram(Plot):
    """ """

    _config = {
        'bins': 100,
        'facecolor': 'lightgrey',
        'edgecolor': 'black',
        'histtype': 'bar',
        'linewidth': 0.5,
        'grid': True
    }

    def plot(self, array):
        """ """

        # plot grid
        self._axes.grid(self._config['grid'])

        # plot histogram
        self._axes.hist(
            array,
            bins=self._config['bins'],
            facecolor=self._config['facecolor'],
            histtype=self._config['histtype'],
            linewidth=self._config['linewidth'],
            edgecolor=self._config['edgecolor'])

        # (optional) plot title
        self.plot_title()

        return True
