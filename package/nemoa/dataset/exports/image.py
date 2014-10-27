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
    """Get supported image filetypes for dataset export."""
    return matplotlib.pyplot.gcf().canvas.get_supported_filetypes()

def show(dataset, plot = None, **kwargs):

    # get class for plotting from attribute 'plot'
    if plot == None: plot = 'histogram'
    class_name = plot.lower().title()
    module_name = save.__module__
    try:
        module = importlib.import_module(module_name)
        if not hasattr(module, class_name):raise ImportError()
    except ImportError:
        return nemoa.log('error', """could not plot dataset '%s':
            plot type '%s' is not supported.""" % (dataset.name, plot))

    # create plot of dataset
    plot = getattr(module, class_name)(**kwargs)

    # common matplotlib settings
    matplotlib.rc('font', family = 'sans-serif')

    # close previous figures
    matplotlib.pyplot.close('all')

    # create plot
    if plot.create(dataset):

        # (optional) draw title
        if plot.settings['show_title']:
            if 'title' in plot.settings \
                and isinstance(plot.settings['title'], str):
                title = plot.settings['title']
            else: title = '' # TODO: self._get_title(model)
            matplotlib.pyplot.title(title, fontsize = 11.)

        # output
        matplotlib.pyplot.show()

    # clear figures and release memory
    matplotlib.pyplot.clf()

    return True

def save(dataset, path = None, filetype = None, plot = None, **kwargs):

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
        return nemoa.log('error', """could not plot dataset '%s':
            plot type '%s' is not supported.""" % (dataset.name, plot))

    # create plot of dataset
    plot = getattr(module, class_name)(**kwargs)

    # common matplotlib settings
    matplotlib.rc('font', family = 'sans-serif')

    # close previous figures
    matplotlib.pyplot.close('all')

    # create plot
    if plot.create(dataset):

        # (optional) draw title
        if plot.settings['show_title']:
            if 'title' in plot.settings \
                and isinstance(plot.settings['title'], str):
                title = plot.settings['title']
            else: title = '' # TODO: self._get_title(model)
            matplotlib.pyplot.title(title, fontsize = 11.)

        # output
        matplotlib.pyplot.savefig(path, dpi = plot.settings['dpi'])

    # clear figures and release memory
    matplotlib.pyplot.clf()

    return path

class Histogram:

    settings = {
        'fileformat': 'pdf',
        'dpi': 300,
        'show_title': True,
        'title': None,
        'bg_color': 'none',
        'path': ('dataset', ),
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

    def create(self, dataset):

        # create data (numpy 1-d array)
        data = dataset.get('data').flatten()

        # create plot
        return nemoa.common.plot.histogram(data, **self.settings)
