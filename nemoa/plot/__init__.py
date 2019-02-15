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
"""Plot modules."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

try:
    import matplotlib
except ImportError as err:
    raise ImportError(
        "requires package matplotlib: "
        "https://matplotlib.org") from err

import matplotlib.pyplot as plt
from flab.base.types import Any, OptDict

#
# Plot Class
#

class Plot:
    """Base class for matplotlib plots.

    Export classes like Histogram, Heatmap or Graph share a common
    interface to matplotlib, as well as certain plotting attributes.
    This base class is intended to provide a unified interface to access
    matplotlib and those attributes.

    Attributes:

    """

    _default: dict = {
        'fileformat': 'pdf',
        'figure_size': (10.0, 6.0),
        'dpi': None,
        'bg_color': 'none',
        'usetex': False,
        'font_family': 'sans-serif',
        'style': 'seaborn-white',
        'title': None,
        'show_title': True,
        'title_fontsize': 14.0
    }

    _config: dict = {}
    _kwds: dict = {}

    _plt = None
    _fig = None
    _axes = None

    def __init__(self, **kwds):
        """ """
        # merge config from defaults, current config and keyword arguments
        self._kwds = kwds
        self._config = {**self._default, **self._config, **kwds}

        # update global matplotlib settings
        matplotlib.rc('text', usetex=self._config['usetex'])
        matplotlib.rc('font', family=self._config['font_family'])

        # link matplotlib.pyplot
        self._plt = plt

        # close previous figures
        plt.close('all')

        # update plot settings
        plt.style.use(self._config['style'])

        # create figure
        self._fig = plt.figure(
            figsize=self._config['figure_size'],
            dpi=self._config['dpi'],
            facecolor=self._config['bg_color'])

        # create subplot (matplotlib.axes.Axes)
        self._axes = self._fig.add_subplot(111)

    def set_default(self, config: OptDict = None) -> bool:
        """Set default values."""
        self._config = {**self._config, **(config or {}), **self._kwds}

        return True

    def plot_title(self) -> bool:
        """Plot title."""
        if not self._config['show_title']:
            return False

        title = self._config['title'] or 'Unknown'
        fontsize = self._config['title_fontsize']

        getattr(self._plt, 'title')(title, fontsize=fontsize)
        return True

    def show(self) -> None:
        """Show plot."""
        getattr(self._plt, 'show')()

    def save(self, path, **kwds):
        """Save plot to file."""
        return self._fig.savefig(path, dpi=self._config['dpi'], **kwds)

    def release(self):
        """Clear current plot."""
        return self._fig.clear()

    @classmethod
    def get_texlabel(cls: type, string: str) -> str:
        """Return formated node label as used for plots."""
        lstr = string.rstrip('1234567890')
        if len(lstr) == len(string):
            return '${%s}$' % (string)
        rnum = int(string[len(lstr):])
        lstr = lstr.strip('_')
        return '${%s}_{%i}$' % (lstr, rnum)

    @classmethod
    def get_texlabel_width(cls: type, string: str) -> float:
        """Return estimated width for formated node labels."""
        lstr = string.rstrip('1234567890')
        if len(lstr) == len(string):
            return len(string)
        lstr = lstr.strip('_')
        rstr = str(int(string[len(lstr):]))
        return len(lstr) + 0.7 * len(rstr)

    @classmethod
    def filetypes(cls: type):
        """Return supported image filetypes."""
        return plt.gcf().canvas.get_supported_filetypes()

    @classmethod
    def get_color(cls: type, *args: Any):
        """Convert color name of XKCD color name survey to RGBA tuple.

        Args:
            List of color names. If the list is empty, a full list of
            available color names is returned. Otherwise the first valid
            color in the list is returned as RGBA tuple. If no color is
            valid None is returned.

        """
        if not args:
            clist = list(matplotlib.colors.get_named_colors_mapping().keys())
            return sorted([cname[5:].title() \
                for cname in clist if cname[:5] == 'xkcd:'])

        rgb = None
        for cname in args:
            try:
                rgb = matplotlib.colors.to_rgb('xkcd:%s' % cname)
                break
            except ValueError:
                continue
        return rgb
