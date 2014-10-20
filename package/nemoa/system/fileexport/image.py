# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import numpy
import os
import importlib
import matplotlib.pyplot

def filetypes():
    """Get supported image filetypes for system export."""
    return matplotlib.pyplot.gcf().canvas.get_supported_filetypes()

def save(system, path = None, filetype = None, plot = None,
    output = 'file', **kwargs):

    if output.lower() == 'file':

        # test if filetype is supported by matplotlib
        if not filetype in filetypes():
            return nemoa.log('error', """could not create plot:
                filetype '%s' is not supported by matplotlib.""" %
                (filetype))

    # get class for plotting from attribute 'plot'
    if plot == None: plot = 'histogram'
    class_name = plot.lower().title()
    module_name = save.__module__
    try:
        module = importlib.import_module(module_name)
        if not hasattr(module, class_name):raise ImportError()
    except ImportError:
        return nemoa.log('error', """could not plot system '%s':
            plot type '%s' is not supported.""" %
            (system.get('name'), plot))

    # create plot of system
    plot = getattr(module, class_name)(**kwargs)

    # common matplotlib settings
    matplotlib.rc('font', family = 'sans-serif')

    # close previous figures
    matplotlib.pyplot.close('all')

    # create plot
    if plot.create(system):

        # (optional) draw title
        if plot.settings['show_title']:
            if 'title' in plot.settings \
                and isinstance(plot.settings['title'], str):
                title = plot.settings['title']
            else: title = '' # TODO: self._get_title(model)
            matplotlib.pyplot.title(title, fontsize = 11.)

        # output
        if output.lower() == 'file':
            matplotlib.pyplot.savefig(
                path, dpi = plot.settings['dpi'])
        elif output.lower() == 'display':
            matplotlib.pyplot.show()

    # clear figures and release memory
    matplotlib.pyplot.clf()

    if output.lower() == 'file':
        return path
    return True

class Histogram:

    settings = {
        'fileformat': 'pdf',
        'dpi': 300,
        'show_title': True,
        'title': None,
        'bg_color': 'none',
        'path': ('system', ),
        'units': (None, None),
        'bins': 120,
        'facecolor': 'lightgrey',
        'edgecolor': 'black',
        'histtype': 'bar',
        'linewidth': 0.5 }

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            if key in self.settings.keys():
                self.settings[key] = val

    def create(self, system):

        # create data (numpy 1-d array)
        data = system.get('data').flatten()

        # create plot
        return nemoa.common.plot.histogram(data, **self.settings)
