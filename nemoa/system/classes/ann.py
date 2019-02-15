# -*- coding: utf-8 -*-
"""Artificial Neuronal Network (ANN).

Generic class of layered feed forward networks aimed to provide common
attributes, methods, optimization algorithms like back-propagation of
errors [HINTON1986]_ and unit classes to other systems by inheritence. For
multilayer network topologies DBNs usually show better performance than
plain ANNs.

"""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

import numpy
import nemoa
from flab.base import catalog

class ANN(nemoa.system.classes.base.System):
    """Artificial Neuronal Network (ANN).

    Generic class of layered feed forward networks aimed to provide
    common attributes, methods, optimization algorithms like
    back-propagation of errors (1) and unit classes to other systems by
    inheritence. For multilayer network topologies DBNs usually show
    better performance than plain ANNs.

    References:
        (1) "Learning representations by back-propagating errors",
            Rumelhart, D. E., Hinton, G. E., and Williams, R. J. (1986)

    Attributes:
        about (str): Short description of the content of the resource.
            Hint: Read- & writeable wrapping attribute to get('about')
                and set('about', str).
        author (str): A person, an organization, or a service that is
            responsible for the creation of the content of the resource.
            Hint: Read- & writeable wrapping attribute to get('author')
                and set('author', str).
        branch (str): Name of a duplicate of the original resource.
            Hint: Read- & writeable wrapping attribute to get('branch')
                and set('branch', str).
        edges (list of str): List of all edges in the network.
            Hint: Readonly wrapping attribute to get('edges')
        email (str): Email address to a person, an organization, or a
            service that is responsible for the content of the resource.
            Hint: Read- & writeable wrapping attribute to get('email')
                and set('email', str).
        fullname (str): String concatenation of name, branch and
            version. Branch and version are only conatenated if they
            exist.
            Hint: Readonly wrapping attribute to get('fullname')
        layers (list of str): List of all layers in the network.
            Hint: Readonly wrapping attribute to get('layers')
        license (str): Namereference to a legal document giving official
            permission to do something with the resource.
            Hint: Read- & writeable wrapping attribute to get('license')
                and set('license', str).
        name (str): Name of the resource.
            Hint: Read- & writeable wrapping attribute to get('name')
                and set('name', str).
        nodes (list of str): List of all nodes in the network.
            Hint: Readonly wrapping attribute to get('nodes')
        path (str):
            Hint: Read- & writeable wrapping attribute to get('path')
                and set('path', str).
        type (str): String concatenation of module name and class name
            of the instance.
            Hint: Readonly wrapping attribute to get('type')
        version (int): Versionnumber of the resource.
            Hint: Read- & writeable wrapping attribute to get('version')
                and set('version', int).

    """

    _default = {
        'params': {
            'visible': 'auto',
            'hidden': 'auto',
            'visible_class': 'gauss',
            'hidden_class': 'sigmoid' },
        'init': {
            'check_dataset': False,
            'ignore_units': [],
            'w_sigma': 0.5 }}

    def _configure_test(self, params):
        """Check if system parameter dictionary is valid. """

        return self._configure_test_units(params) \
            and self._configure_test_links(params)

    def _configure_test_units(self, params):
        """Check if system unit parameter dictionary is valid. """

        if not isinstance(params, dict) \
            or not 'units' in list(params.keys()) \
            or not isinstance(params['units'], list): return False

        for layer_id in range(len(params['units'])):

            # test parameter dictionary
            layer = params['units'][layer_id]

            if not isinstance(layer, dict): return False
            for key in ['id', 'layer', 'layer_id', 'visible', 'class']:
                if key not in layer: return False

            # test unit class
            if layer['class'] == 'gauss' \
                and not nemoa.system.commons.units.Gauss.check(layer):
                return False
            elif layer['class'] == 'sigmoid' \
                and not nemoa.system.commons.units.Sigmoid.check(layer):
                return False

        return True

    def _remove_units(self, layer = None, label = []):
        """Remove units from parameter space. """

        if layer is not None and layer not in self._units:
            raise ValueError(f"layer '{layer}' is not valid")

        # search for labeled units in given layer
        layer = self._units[layer].params
        select = []
        labels = []
        for id, unit in enumerate(layer['id']):
            if unit not in label:
                select.append(id)
                labels.append(unit)

        # remove units from unit labels
        layer['id'] = labels

        # delete units from unit parameter arrays
        if layer['class'] == 'gauss':
            nemoa.system.commons.units.Gauss.remove(layer, select)
        elif layer['class'] == 'sigmoid':
            nemoa.system.commons.units.Sigmoid.remove(layer, select)

        # delete units from link parameter arrays
        links = self._links[layer['layer']]

        for src in list(links['source'].keys()):
            links['source'][src]['A'] = \
                links['source'][src]['A'][:, select]
            links['source'][src]['W'] = \
                links['source'][src]['W'][:, select]
        for tgt in list(links['target'].keys()):
            links['target'][tgt]['A'] = \
                links['target'][tgt]['A'][select, :]
            links['target'][tgt]['W'] = \
                links['target'][tgt]['W'][select, :]

        return True

    def _configure_test_links(self, params):
        """Check if system link parameter dictionary is valid."""

        if not isinstance(params, dict) \
            or not 'links' in list(params.keys()) \
            or not isinstance(params['links'], dict): return False
        for id in list(params['links'].keys()):
            if not isinstance(params['links'][id], dict): return False
            for attr in ['A', 'W', 'source', 'target']:
                if not attr in list(params['links'][id].keys()): return False

        return True

    @catalog.custom(
        name     = 'energy',
        category = ('system', 'evaluation'),
        args     = 'all',
        formater = lambda val: '%.3f' % (val),
        optimum  = 'min'
    )
    def _get_energy(self, data, *args, **kwds):
        """Sum of local link and unit energies."""

        mapping = list(self._get_mapping())
        energy = 0.

        # sum local unit energies
        for i in range(1, len(mapping) + 1):
            energy += self._get_units_energy(data[0],
                mapping = tuple(mapping[:i])).sum(axis = 1)

        # sum local link energies
        for i in range(1, len(mapping)):
            energy += self._get_links_energy(data[0],
                mapping = tuple(mapping[:i + 1])).sum(axis = (1, 2))

        # calculate (pseudo) energy of system
        return numpy.log(1. + numpy.exp(-energy).sum())

    @catalog.custom(
        name     = 'units_energy',
        category = ('system', 'units', 'evaluation'),
        args     = 'input',
        retfmt   = 'scalar',
        formater = lambda val: '%.3f' % (val),
        plot     = 'diagram'
    )
    def _get_units_energy(self, data, mapping = None):
        """Unit energies of target units.

        Args:
            data: numpy array containing source data corresponding to
                the source unit layer (first argument of the mapping)
            mapping: n-tuple of strings containing the mapping
                from source unit layer (first argument of tuple)
                to target unit layer (last argument of tuple)

        Returns:
            Numpy array of shape (data, targets).

        """

        # set mapping from input layer to output layer (if not set)
        if mapping is None: mapping = self._get_mapping()
        data = self._get_unitexpect(data, mapping)
        return self._units[mapping[-1]].energy(data)

    @catalog.custom(
        name     = 'links_energy',
        category = ('system', 'links', 'evaluation'),
        args     = 'input',
        retfmt   = 'scalar',
        formater = lambda val: '%.3f' % (val),
        plot     = 'diagram'
    )
    def _get_links_energy(self, data, mapping = None, **kwds):
        """Return link energies of a layer.

        Args:
            mapping: tuple of strings containing the mapping
                from source unit layer (first argument of tuple)
                to target unit layer (last argument of tuple)

        """

        if len(mapping) == 1:
            # TODO
            raise ValueError("""sorry: bad implementation of
                ann._get_links_energy""")
        elif len(mapping) == 2:
            sdata = data
            tdata = self._get_unitvalues(sdata, mapping)
        else:
            sdata = self._get_unitexpect(data, mapping[0:-1])
            tdata = self._get_unitvalues(sdata, mapping[-2:])

        sid = self._get_mapping().index(mapping[-2])
        tid = self._get_mapping().index(mapping[-1])
        src = self._units[mapping[-2]].params
        tgt = self._units[mapping[-1]].params

        if (sid, tid) in self._params['links']:
            links = self._params['links'][(sid, tid)]
            return nemoa.system.commons.links.Links.energy(
                sdata, tdata, src, tgt, links)
        elif (tid, sid) in self._params['links']:
            links = self._params['links'][(tid, sid)]
            return nemoa.system.commons.links.Links.energy(
                tdata, sdata, tgt, src, links)
