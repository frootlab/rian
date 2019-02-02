# -*- coding: utf-8 -*-
# Copyright (c) 2013-2019 Patrick Michl
#
# This file is part of nemoa, https://frootlab.github.io/nemoa
#
#  nemoa is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  nemoa is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with
#  nemoa. If not, see <http://www.gnu.org/licenses/>.
#
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
