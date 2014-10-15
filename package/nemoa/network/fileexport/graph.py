# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import networkx
import os

def filetypes():
    """Get supported graph filetypes for network export."""
    return {
        'gml': 'Graph Modelling Language',
        'graphml': 'Graph Markup Language',
        'dot': 'GraphViz DOT' }

def save(network, path, **kwargs):

    # extract filetype from path
    filetype = nemoa.common.get_file_extension(path).lower()

    # test if filetype is supported
    if not filetype in filetypes():
        return nemoa.log('error', """could not export graph:
            filetype '%s' is not supported by networkx.""" % (filetype))

    # create path if not available
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))

    # get networkx graph from network
    graph = network.get('graph', type = 'graph')

    if filetype == 'gml':
        return Gml(**kwargs).save(graph, path)
    if filetype == 'graphml':
        return Graphml(**kwargs).save(graph, path)
    if filetype == 'dot':
        return Dot(**kwargs).save(graph, path)

    return False

class Gml:
    """Export network to GML file."""

    settings = {
        'coding': 'base64' }

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            if key in self.settings.keys():
                self.settings[key] = val

    def save(self, graph, path):

        # encode graph parameter dictionaries
        graph = nemoa.network.fileexport.encode(graph,
            coding = self.settings['coding'])

        # write networkx graph to gml file
        networkx.write_gml(graph, path)

        return path

class Graphml:
    """Export network to GraphML file."""

    settings = {
        'coding': 'base64' }

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            if key in self.settings.keys():
                self.settings[key] = val

    def save(self, graph, path):

        # encode graph parameter dictionaries
        graph = nemoa.network.fileexport.encode(graph,
            coding = self.settings['coding'])

        # write networkx graph to gml file
        networkx.write_graphml(graph, path)

        return path

class Dot:
    """Export network to GraphViz Dot file."""

    settings = {
        'coding': 'base64' }

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            if key in self.settings.keys():
                self.settings[key] = val

    def save(self, graph, path):

        # encode graph parameter dictionaries
        graph = nemoa.network.fileexport.encode(graph,
            coding = self.settings['coding'])

        # check library support for dot files
        try:
            module = networkx.drawing.write_dot.__module__
        except:
            return nemoa.log('error', """could not export graph:
                filetype 'dot' needs libraries 'pygraphviz' and
                'pydot'.""")

        # write networkx graph to graphviz dot file
        networkx.write_dot(graph, path)

        return path
