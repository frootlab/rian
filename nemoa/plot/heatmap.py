# -*- coding: utf-8 -*-
"""Plot Heatmap."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import numpy as np
from matplotlib.cm import hot_r
from nemoa.plot import Plot

class Heatmap(Plot):
    """ """

    _config = {
        'interpolation': 'nearest',
        'grid': True
    }

    def plot(self, array):
        """ """

        # plot grid
        self._axes.grid(self._config['grid'])

        # plot heatmap
        cax = self._axes.imshow(
            array,
            cmap=hot_r,
            interpolation=self._config['interpolation'],
            extent=(0, array.shape[1], 0, array.shape[0]))

        # create labels for axis
        max_font_size = 12.
        x_labels = []
        for label in self._config['x_labels']:
            if ':' in label:
                label = label.split(':', 1)[1]
            x_labels.append(self.get_texlabel(label))
        y_labels = []
        for label in self._config['y_labels']:
            if ':' in label:
                label = label.split(':', 1)[1]
            y_labels.append(self.get_texlabel(label))
        fontsize = min(max_font_size, \
            400. / float(max(len(x_labels), len(y_labels))))
        self._plt.xticks(
            np.arange(len(x_labels)) + 0.5,
            tuple(x_labels), fontsize=fontsize, rotation=65)
        self._plt.yticks(
            len(y_labels) - np.arange(len(y_labels)) - 0.5,
            tuple(y_labels), fontsize=fontsize)

        # create colorbar
        cbar = self._fig.colorbar(cax)
        for tick in cbar.ax.get_yticklabels():
            tick.set_fontsize(9)

        # (optional) plot title
        self.plot_title()

        return True