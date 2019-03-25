# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 Frootlab
# Copyright (C) 2013-2019 Patrick Michl
#
# This file is part of Nemoa, https://www.frootlab.org/nemoa
#
#  Nemoa is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Nemoa is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with
#  Nemoa. If not, see <http://www.gnu.org/licenses/>.
#
"""Plot Histogram."""

__copyright__ = '2019 Frootlab'
__license__ = 'GPLv3'
__docformat__ = 'google'
__author__ = 'Frootlab Developers'
__email__ = 'contact@frootlab.org'
__authors__ = ['Patrick Michl <patrick.michl@frootlab.org>']

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
