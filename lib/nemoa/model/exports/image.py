# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import importlib
import matplotlib.pyplot
import nemoa
import networkx
import numpy
import os

def filetypes():
    """Get supported image filetypes for model export."""
    return matplotlib.pyplot.gcf().canvas.get_supported_filetypes()

def save(model, path = None, filetype = None, plot = None, **kwargs):

    # test if filetype is supported by matplotlib
    if not filetype in filetypes():
        return nemoa.log('error', """could not create plot:
            filetype '%s' is not supported by matplotlib.""" %
            (filetype))

    # get class for plotting from attribute 'plot'
    if not plot: plot = 'graph'
    class_name = plot.lower().title()
    module_name = save.__module__
    try:
        module = importlib.import_module(module_name)
        if not hasattr(module, class_name): raise ImportError()
    except ImportError:
        return nemoa.log('error', """could not plot model '%s':
            plot type '%s' is not supported.""" %  (model.name, plot))

    # create plot of model
    plot = getattr(module, class_name)(**kwargs)

    # assert units
    mapping = model.system.mapping
    in_units = model.system.get('units', layer = mapping[0])
    out_units = model.system.get('units', layer = mapping[-1])
    if not isinstance(plot.settings['units'], tuple) \
        or not isinstance(plot.settings['units'][0], list) \
        or not isinstance(plot.settings['units'][1], list):
        plot.settings['units'] = (in_units, out_units)

    # get information about relation
    if plot.settings['show_title']:
        rel_id = nemoa.common.text.split_kwargs(
            plot.settings['relation'])[0]
        rel_dict = model.system.get('algorithm', rel_id,
            category = ('system', 'relation', 'evaluation'))
        rel_name = rel_dict['name']
        plot.settings['title'] = rel_name.title()

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
            else: title = '' # Todo: self._get_title(model)
            matplotlib.pyplot.title(title, fontsize = 11.)

        # output
        matplotlib.pyplot.savefig(path, dpi = plot.settings['dpi'])

    # clear figures and release memory
    matplotlib.pyplot.clf()

    return path

def show(model, plot = None, *args, **kwargs):

    # get class for plotting from attribute 'plot'
    if not plot: plot = 'graph'
    class_name = plot.lower().title()
    module_name = save.__module__
    try:
        module = importlib.import_module(module_name)
        if not hasattr(module, class_name): raise ImportError()
    except ImportError:
        return nemoa.log('error', """could not plot model '%s':
            plot type '%s' is not supported.""" % (model.name, plot))

    # create plot of model
    plot = getattr(module, class_name)(*args, **kwargs)

    # assert units
    mapping = model.system.mapping
    in_units = model.system.get('units', layer = mapping[0])
    out_units = model.system.get('units', layer = mapping[-1])
    if not isinstance(plot.settings['units'], tuple) \
        or not isinstance(plot.settings['units'][0], list) \
        or not isinstance(plot.settings['units'][1], list):
        plot.settings['units'] = (in_units, out_units)

    # get information about relation
    if plot.settings['show_title']:
        rel_id = nemoa.common.text.split_kwargs(
            plot.settings['relation'])[0]
        rel_dict = model.system.get('algorithm', rel_id,
            category = ('system', 'relation', 'evaluation'))
        rel_name = rel_dict['name']
        plot.settings['title'] = rel_name.title()

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
            else: title = '' # Todo: self._get_title(model)
            matplotlib.pyplot.title(title, fontsize = 11.)

        # output
        matplotlib.pyplot.show()

    # clear figures and release memory
    matplotlib.pyplot.clf()

    return True

class Graph(nemoa.common.classes.Plot):

    settings = None
    default = {
        'fileformat': 'pdf',
        'figure_size': (10., 6.),
        'dpi': None,
        'bg_color': 'none',
        'usetex': False,
        'show_title': True,
        'title': None,
        'title_fontsize': 14.0,
        'show_legend': True,
        'legend_fontsize': 9.0,
        'graph_layout': 'layer',
        'units': (None, None),
        'relation': 'induction',
        'preprocessing': None,
        'measure': 'error',
        'statistics': 10000,
        'transform': '',
        'edge_normalize': 'auto',
        'sign': None,
        'filter': None,
        'cutoff': 0.5,
        'node_caption': 'accuracy' }

    def create(self, model):

        import nemoa.common.graph as nmgraph

        # get units and edges
        units = self.settings.get('units')
        edges = [(i, o) for i in units[0] for o in units[1]
            if not o == i]

        # calculate edge weights from 'weight' relation
        relarg = self.settings.get('relation', '')
        rel_name = nemoa.common.text.split_kwargs(relarg)[0]
        W = model.evaluate('system', 'relations', rel_name,
            preprocessing = self.settings['preprocessing'],
            measure = self.settings['measure'],
            statistics = self.settings['statistics'],
            transform = self.settings['transform'])
        if not isinstance(W, dict): return nemoa.log('error',
            "could not create relation graph: "
            "invalid weight relation '%s'" % rel_name)
        rel_about = model.system.get('algorithm', rel_name,
            category = ('system', 'relation', 'evaluation'))

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
            return nemoa.log('error', """could not create relation
                graph: invalid filter relation
                '%s'!""" % self.settings['filter'])

        # create filter mask from filter relation (parameter: 'cutoff')
        # and update list of edges
        bound = self.settings['cutoff'] * F['std']
        edges = [edge for edge in edges if not -bound < F[edge] < bound]
        if len(edges) == 0: return nemoa.log('warning',
            "could not create relation graph:"
            "no relation passed threshold (%.2f)!" % bound)

        # calculate edge signs from 'sign' relation
        # default: use the same relation, as used for weights
        rel_sign_name = self.settings.get('sign')
        if rel_sign_name == None:
            rel_sign_name = rel_name
            rel_sign_about = rel_about
        else:
            rel_sign_about = model.system.get(
                'algorithm', rel_sign_name,
                category = ('system', 'relation', 'evaluation'))
        signed = rel_sign_about.get('signed', False)
        if signed:
            if rel_sign_name == rel_name: sr = W
            else: sr = model.evaluate('system', 'relations',
                rel_sign_name,
                preprocessing = self.settings['preprocessing'],
                measure = self.settings['measure'],
                statistics = self.settings['statistics'])
            if not isinstance(sr, dict): return nemoa.log('error',
                "could not create relation graph: "
                "invalid sign relation!")
            S = {edge: 2. * (float(sr[edge] > 0.) - 0.5) \
                for edge in edges}

        # create graph and set attributes
        graph = networkx.DiGraph(name = rel_about.get('name'))

        # add edges and edge attributes to graph
        if self.settings['edge_normalize'] in [None, 'auto']:
            normalize = not rel_about.get('normal')
        elif self.settings['edge_normalize'] in [True, False]:
            normalize = self.settings['edge_normalize']
        else: return nemoa.log('error',
            "could not create relation graph: "
            "invalid value for parameter 'edge_normalize'")

        # add nodes with attributes
        nodes = units[0] + units[1]
        for node in nodes:
            attr = model.network.get('node', node)
            if attr == None: continue
            params = attr.get('params', {})
            graph.add_node(node,
                label = params.get('label'),
                group = params.get('layer'))
            issrc, istgt = node in units[0], node in units[1]
            if issrc and istgt: node_type = 'transit'
            elif issrc and not istgt: node_type = 'source'
            elif not issrc and istgt: node_type = 'target'
            else: node_type = 'isolated'
            layout = nmgraph.get_node_layout(node_type)
            graph.node[node].update(layout)

        # add edges with attributes
        for (u, v) in edges:
            if u == v: continue
            value = W[(u, v)]
            weight = numpy.absolute(value / W['std'] \
                if normalize else value)
            if signed: color = \
                {1: 'green', 0: 'black', -1: 'red'}[S.get((u, v))]
            else: color = 'black'
            graph.add_edge(u, v, weight = weight, color = color)

        # normalize weights (optional)
        if normalize:
            mean = numpy.mean([data.get('weight', 0.) \
                for (u, v, data) in graph.edges(data = True)])
            for (u, v, data) in graph.edges(data = True):
                graph.edge[u][v]['weight'] = data['weight'] / mean

        # graph layout specific attributes
        graph_layout = self.settings.get('graph_layout', None)
        if graph_layout == 'layer':
            for node in graph.nodes():
                attr = model.network.get('node', node)
                params = attr.get('params', {})
                graph.node[node].update({
                    'layer': params.get('layer'),
                    'layer_id': params.get('layer_id'),
                    'layer_sub_id': params.get('layer_sub_id')})

        # create plot
        return nemoa.common.plot.graph(graph, **self.settings)

class Heatmap:

    settings = None
    default = {
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
        'interpolation': 'nearest',
        'format': 'array' }

    def __init__(self, **kwargs):
        self.settings = nemoa.common.dict.merge(kwargs, self.default)

    def create(self, model):

        # calculate relation
        relation = model.evaluate('system', 'relations',
            self.settings['relation'], **self.settings)

        if not isinstance(relation, numpy.ndarray):
            return nemoa.log('error', """could not plot heatmap:
                relation matrix is not valid.""")

        # create plot
        return nemoa.common.plot.heatmap(relation, **self.settings)

class Histogram:

    settings = None
    default = {
        'fileformat': 'pdf',
        'dpi': 300,
        'show_title': True,
        'title': None,
        'bg_color': 'none',
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

    def __init__(self, **kwargs):
        self.settings = nemoa.common.dict.merge(kwargs, self.default)

    def create(self, model):

        # get units and edges
        units = self.settings['units']
        edges = []
        for i in units[0]:
            for o in [u for u in units[1] if not u == i]:
                edges.append((i, o))

        # calculate relation
        R = model.evaluate('system', 'relations',
            self.settings['relation'],
            preprocessing = self.settings['preprocessing'],
            measure = self.settings['measure'],
            statistics = self.settings['statistics'],
            transform = self.settings['transform'])
        if not isinstance(R, dict):
            return nemoa.log('error', """could not create relation
                histogram: invalid relation
                '%s'!""" % self.settings['relation'])

        # create data array
        data = numpy.array([R[edge] for edge in edges])

        # create plot
        return nemoa.common.plot.histogram(data, **self.settings)
