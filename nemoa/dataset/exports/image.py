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

__copyright__ = '2019 Frootlab'
__license__ = 'GPLv3'
__docformat__ = 'google'
__author__ = 'Frootlab Developers'
__email__ = 'contact@frootlab.org'
__authors__ = ['Patrick Michl <patrick.michl@frootlab.org>']

import networkx as nx
import numpy as np
from flib.base import call, otree
import nemoa
from nemoa.plot import Plot, heatmap, histogram, network, scatter

def filetypes():
    """Get supported image filetypes."""

    return Plot.filetypes()

def get_plot(dataset, func=None, plot=None, **kwds):

    import importlib

    # get evaluation function
    fname = func or 'sample'
    fdict = dataset.get('algorithm', fname)
    if not isinstance(fdict, dict):
        raise ValueError(
            "could not plot dataset '%s': "
            "dataset evaluation function '%s' "
            "is not supported." % (dataset.name, fname))

    # get plot type
    plot = plot or fdict.get('plot', None) or 'histogram'

    # get plot class and module name
    cname = plot.lower().title()
    mname = save.__module__
    try:
        module = importlib.import_module(mname)
        if not hasattr(module, cname):
            raise ImportError()
    except ImportError as err:
        raise ValueError(
            "could not plot dataset '%s': "
            "plot type '%s' is not supported." % (dataset.name, plot)) from err

    # create plot
    plot = getattr(module, cname)(func=fname, **kwds)
    if plot.create(dataset):
        return plot

    plot.release()
    return None

def show(dataset, *args, **kwds):
    """ """

    # create plot
    plot = get_plot(dataset, *args, **kwds)
    if plot is None: return None

    plot.show()
    plot.release()

    return True

def save(dataset, path = None, filetype = None, *args, **kwds):

    # test if filetype is supported
    if filetype not in filetypes():
        raise ValueError(f"filetype '{filetype}' is not supported")

    plot = get_plot(dataset, *args, **kwds)
    if plot is None: return None

    plot.save(path)
    plot.release()

    return True

class Heatmap(heatmap.Heatmap):

    def create(self, dataset):

        # set plot defaults
        self.set_default({
            'func': 'correlation' })

        # evaluate function
        fname = self._config.get('func')
        fdict = dataset.get('algorithm', fname)
        func = fdict.get('func', None) or fdict.get('reference', None)

        # Note: The following workaround is to be replaced by:
        # kwds = call.parameters(func, **self._config)
        keys = set(call.parameters(func).keys())
        keys = keys.intersection(self._config.keys())
        kwds = {key: self._config[key] for key in keys}

        array = dataset.evaluate(fname, **kwds)

        # check return value
        cols  = dataset.get('columns')
        shape = (len(cols), len(cols))
        if not isinstance(array, np.ndarray) or not array.shape == shape:
            raise Warning(
                "representation of '%s' as heatmap "
                "is not supported." % fname)

        # update axes labels
        self._config['x_labels'] = cols
        self._config['y_labels'] = cols

        # update title
        if not isinstance(self._config.get('title', None), str):
            if self._config.get('usetex', False):
                self._config['title'] = fdict.get('title_tex', None) \
                    or fdict.get('title', fname.title())
            else:
                self._config['title'] = fdict.get('title', fname.title())

        # create plot
        return self.plot(array)

class Histogram(histogram.Histogram):

    def create(self, dataset):

        # set plot defaults
        self.set_default({
            'func': 'correlation' })

        # evaluate function
        fname = self._config.get('func')
        fdict = dataset.get('algorithm', fname)
        func = fdict.get('func', None) or fdict.get('reference', None)

        # Note: The following workaround is to be replaced by:
        # kwds = call.parameters(func, **self._config)
        keys = set(call.parameters(func).keys())
        keys = keys.intersection(self._config.keys())
        kwds = {key: self._config[key] for key in keys}

        array = dataset.evaluate(fname, **kwds)

        # check return value
        if not isinstance(array, np.ndarray):
            raise Warning(
                "representation of '%s' as histogram "
                "is not supported." % (fname))

        # get flat data
        data = array.flatten()

        # update title
        if not isinstance(self._config.get('title', None), str):
            if self._config.get('usetex', False):
                self._config['title'] = fdict.get('title_tex', None) \
                    or fdict.get('title', fname.title())
            else:
                self._config['title'] = fdict.get('title', fname.title())

        # create plot
        return self.plot(data)

class Scatter2D(scatter.Scatter2D):

    def create(self, dataset):

        # set plot defaults
        self.set_default({
            'func': 'correlation',
            'pca': True })

        # evaluate function
        fname = self._config.get('func')
        fdict = dataset.get('algorithm', fname)
        func = fdict.get('func', None) or fdict.get('reference', None)
        kwds = call.parameters(func, default = self._config)
        array = dataset.evaluate(fname, **kwds)

        # check return value
        if not isinstance(array, np.ndarray):
            raise Warning(
                "representation of '%s' as 2d scatter plot "
                "is not supported." % fname)

        # update title
        if not isinstance(self._config.get('title', None), str):
            if self._config.get('usetex', False):
                self._config['title'] = fdict.get('title_tex', None) \
                    or fdict.get('title', fname.title())
            else:
                self._config['title'] = fdict.get('title', fname.title())

        # create plot
        return self.plot(array)

class Graph(network.Graph2D):

    def create(self, dataset):

        # set plot defaults
        self.set_default({
            'func': 'correlation',
            'graph_layout': 'spring',
            'node_style': 'o',
            'edge_width_enabled': True,
            'edge_curvature': 1.0,
            'show_legend': False })

        # evaluate function
        fname = self._config.get('func')
        fdict = dataset.get('algorithm', fname)
        func = fdict.get('func', None) or fdict.get('reference', None)
        kwds = call.parameters(func, default = self._config)
        array = dataset.evaluate(fname, **kwds)

        # check if evaluation yields valid relation
        cols  = dataset.get('columns')
        shape = (len(cols), len(cols))
        if not isinstance(array, np.ndarray) or not array.shape == shape:
            raise Warning(
                "representation of '%s' as graph "
                "is not supported." % fname)

        # create networkx graph object
        G = nx.DiGraph(name = fname)

        # graph is directed if and only if relation is unsymmetric
        G.graph['directed'] = not np.allclose(array, array.T)

        # add nodes with attributes
        nodes = dataset.get('columns')
        for node in nodes:
            G.add_node(node, label = node)

        # add edges with weights
        for i, u in enumerate(nodes):
            for j, v in enumerate(nodes):
                G.add_edge(u, v, weight = array[i, j], visible = True)

        # create plot
        return self.plot(G)
