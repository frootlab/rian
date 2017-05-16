# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import numpy
import os
import importlib

def filetypes():
    """Get supported image filetypes."""
    return nemoa.common.plot.filetypes()

def show(dataset, plot = None, **kwargs):

    # get class for plotting from attribute 'plot'
    if not plot: plot = 'histogram'
    class_name = plot.lower().title()
    module_name = save.__module__
    try:
        module = importlib.import_module(module_name)
        if not hasattr(module, class_name):raise ImportError()
    except ImportError:
        return nemoa.log('error', """could not plot dataset '%s':
            plot type '%s' is not supported.""" % (dataset.name, plot))

    # create and show plot
    plot = getattr(module, class_name)(**kwargs)
    if plot.create(dataset): plot.show()
    plot.release()
    return True

def save(dataset, path = None, filetype = None, plot = None, **kwargs):

    # test if filetype is supported
    if not filetype in filetypes():
        return nemoa.log('error', """could not create plot:
            filetype '%s' is not supported.""" %
            (filetype))

    # get class for plotting from attribute 'plot'
    if not plot: plot = 'histogram'
    class_name = plot.lower().title()
    module_name = save.__module__
    try:
        module = importlib.import_module(module_name)
        if not hasattr(module, class_name):raise ImportError()
    except ImportError:
        return nemoa.log('error', """could not plot dataset '%s':
            plot type '%s' is not supported.""" % (dataset.name, plot))

    # create and save plot
    plot = getattr(module, class_name)(**kwargs)
    if plot.create(dataset): plot.save(path)
    plot.release()
    return path

class Heatmap(nemoa.common.classes.Plot):

    settings = {
        'fileformat': 'pdf',
        'dpi': None,
        'title': None,
        'show_title': True,
        'title_fontsize': 14,
        'bg_color': 'none',
        'path': ('system', 'relations'),
        'units': (None, None),
        'relation': 'correlation',
        'preprocessing': None,
        'measure': 'error',
        'statistics': 10000,
        'transform': '',
        'layer': None,
        'interpolation': 'nearest' }

    def create(self, dataset):

        # calculate relation
        R = dataset.evaluate(self.settings['relation'])

        if not isinstance(R, numpy.ndarray): return nemoa.log('error',
            'could not plot heatmap: relation matrix is not valid!')

        # Todo: ugly workaround
        columns = dataset.get('columns')
        self.settings['units'] = (columns, columns)

        # create plot
        return nemoa.common.plot.heatmap(R, **self.settings)

class Histogram(nemoa.common.classes.Plot):

    settings = {
        'path': ('dataset', ),
        'units': (None, None),
        'bins': 120,
        'facecolor': 'lightgrey',
        'edgecolor': 'black',
        'histtype': 'bar',
        'linewidth': 0.5 }

    def create(self, dataset):

        # create data (numpy 1-d array)
        data = dataset.get('data').flatten()

        # create plot
        return nemoa.common.plot.histogram(data, **self.settings)
