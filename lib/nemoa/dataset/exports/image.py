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
        return nemoa.log('error',
            "could not plot dataset '%s': "
            "plot type '%s' is not supported." % (dataset.name, plot))

    # create and save plot
    plot = getattr(module, class_name)(**kwargs)
    if plot.create(dataset): plot.save(path)
    plot.release()
    return path

class Heatmap(nemoa.common.plot.Heatmap):

    def create(self, dataset):

        # calculate matrix for heatmap
        relation = self._config.get('relation', 'correlation')
        matrix = dataset.evaluate(relation)

        # update x and y labels from dataset
        cols = dataset.get('columns')
        self._config['x_labels'] = cols
        self._config['y_labels'] = cols

        # update title from dataset
        if not isinstance(self._config.get('title'), str):
            self._config['title'] = dataset.name

        # create plot
        return self.plot(matrix)

class Histogram(nemoa.common.plot.Histogram):

    def create(self, dataset):

        # get flat data
        data = dataset.get('data').flatten()

        # update title from dataset
        if not isinstance(self._config.get('title'), str):
            self._config['title'] = dataset.name

        # create plot
        return self.plot(data)
