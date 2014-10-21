# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import networkx
import numpy
import os
import importlib
import matplotlib.pyplot

def filetypes():
    """Get supported image filetypes for model export."""
    return matplotlib.pyplot.gcf().canvas.get_supported_filetypes()

def save(model, path = None, filetype = None, plot = None,
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
        return nemoa.log('error', """could not plot model '%s':
            plot type '%s' is not supported.""" %
            (model.get('name'), plot))

    # create plot of model
    plot = getattr(module, class_name)(**kwargs)

    # common matplotlib settings
    matplotlib.rc('font', family = 'sans-serif')

    # close previous figures
    matplotlib.pyplot.close('all')

    # create plot
    if plot.create(model):

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

class Graph:

    @staticmethod
    def _settings(): return {
        'graph_caption': True,
        'units': (None, None),
        'relation': 'correlation',
        'preprocessing': None,
        'measure': 'error',
        'statistics': 10000,
        'transform': '',
        'normalize_weights': 'auto',
        'sign': None,
        'filter': None,
        'cutoff': 0.5,
        'node_caption': 'accuracy',
        'layout': 'spring',
    }

    def _create(self, model):

        # get units and edges
        units = self.settings['units']
        edges = [(i, o) for i in units[0] for o in units[1]
            if not o == i]

        # calculate edge weights from 'weight' relation
        W = model.evaluate('system', 'relations',
            self.settings['relation'],
            preprocessing = self.settings['preprocessing'],
            measure = self.settings['measure'],
            statistics = self.settings['statistics'],
            transform = self.settings['transform'])
        if not isinstance(W, dict):
            return nemoa.log('error',
                """could not create relation graph: invalid weight
                relation '%s'!""" % (self.settings['relation']))
        rel_about = model.about('system', 'relations',
            nemoa.common.str_split_params(self.settings['relation'])[0])

        # calculate edge filter from 'filter' relation
        # default: use the same relation, as used for weights
        if not self.settings['filter'] or self.settings['filter'] == \
            self.settings['relation']: F = W
        else: F = model.evaluate('system', 'relations',
            self.settings['filter'],
            preprocessing = self.settings['preprocessing'],
            measure = self.settings['measure'],
            statistics = self.settings['statistics'])
        if not isinstance(F, dict):
            return nemoa.log('error',
                """could not create relation graph: invalid filter
                relation '%s'!""" % (self.settings['filter']))

        # create filter mask from filter relation (parameter: 'cutoff')
        # and update list of edges
        bound = self.settings['cutoff'] * F['std']
        edges = [edge for edge in edges if not -bound < F[edge] < bound]
        if len(edges) == 0:
            return nemoa.log('warning',
                """could not create relation graph: no relation passed
                filter (threshold = %.2f)!""" % (bound))

        # calculate edge signs from 'sign' relation
        # default: use the same relation, as used for weights
        if self.settings['sign'] == None \
            or self.settings['sign'] == self.settings['relation']:
            SR = W
        else:
            SR = model.evaluate('system', 'relations',
                self.settings['sign'],
                preprocessing = self.settings['preprocessing'],
                measure = self.settings['measure'],
                statistics = self.settings['statistics'])
        if not isinstance(SR, dict):
            return nemoa.log('error',
                """could not create relation graph:
                invalid sign relation!""")
        S = {edge: 2. * (float(SR[edge] > 0.) - 0.5) for edge in edges}

        # create graph and set name
        graph = networkx.DiGraph(name = rel_about['name'])

        # add edges and edge attributes to graph
        if self.settings['normalize_weights'] in [None, 'auto']:
            normalize = not rel_about['normal']
        elif self.settings['normalize_weights'] in [True, False]:
            normalize = self.settings['normalize_weights']
        else: return nemoa.log('error',
            """could not create relation graph:
            invalid value for parameter 'normalize_weights'!""")
        for edge in edges: graph.add_edge(*edge,
            weight = abs(W[edge] / W['std'] if normalize else W[edge]),
            color = {1: 'green', 0: 'black', -1: 'red'}[S[edge]])

        # find (disconected) complexes in graph
        graphs = networkx.connected_component_subgraphs(
            graph.to_undirected())
        if len(graphs) > 1: nemoa.log(
            '%i complexes found' % (len(graphs)))

        # update node attributes
        for i in xrange(len(graphs)):
            for n in graphs[i].nodes():
                node = model.network.get('node', n)
                label = nemoa.common.str_format_unit_label(
                    node['params']['label'])
                # TODO: node_type not in {i, o}
                node_type = node['params']['layer']
                graph.node[n]['label'] = label
                graph.node[n]['type'] = node_type
                graph.node[n]['complex'] = i
                graph.node[n]['color'] = {
                    'i': 'lightgrey1', 'o': 'white'}[node_type]

        # create plot
        return nemoa.common.plot.graph(graph, **self.settings)

class Heatmap:

    settings = {
        'fileformat': 'pdf',
        'dpi': 300,
        'show_title': True,
        'title': None,
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

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            if key in self.settings.keys():
                self.settings[key] = val

    def create(self, system):

        # create data (numpy 1-d array)
        data = dataset.get('data').flatten()

        # create plot
        return nemoa.common.plot.histogram(data, **self.settings)

    def _create(self, model):

        # calculate relation
        R = model.evaluate('system', 'relations', self.settings['relation'],
            preprocessing = self.settings['preprocessing'],
            measure = self.settings['measure'],
            statistics = self.settings['statistics'],
            transform = self.settings['transform'],
            format = 'array')

        if not isinstance(R, numpy.ndarray): return nemoa.log('error',
            'could not plot heatmap: relation matrix is not valid!')

        # create plot
        return nemoa.common.plot.heatmap(R, **self.settings)

class Histogram:

    @staticmethod
    def _settings(): return {
        'path': ('system', 'relations'),
        'graph_caption': True,
        'units': (None, None),
        'relation': 'correlation',
        'preprocessing': None,
        'measure': 'error',
        'statistics': 10000,
        'transform': '',
        'layer': None,
        'bins': 50,
        'facecolor': 'lightgrey',
        'edgecolor': 'black',
        'histtype': 'bar',
        'linewidth': 0.5 }

    def _create(self, model):

        # get units and edges
        units = self.settings['units']
        edges = []
        for i in units[0]:
            for o in [u for u in units[1] if not u == i]:
                edges.append((i, o))

        # calculate relation
        R = model.evaluate('system', 'relations', self.settings['relation'],
            preprocessing = self.settings['preprocessing'],
            measure = self.settings['measure'],
            statistics = self.settings['statistics'],
            transform = self.settings['transform'])
        if not isinstance(R, dict): return nemoa.log('error', """
            could not create relation histogram:
            invalid relation '%s'!""" % (self.settings['relation']))

        # create data array
        data = numpy.array([R[edge] for edge in edges])

        # create plot
        return nemoa.common.plot.histogram(data, **self.settings)
