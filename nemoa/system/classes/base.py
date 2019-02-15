# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

import numpy
from flab.base import catalog, otree
import nemoa
from nemoa.base import nbase
from nemoa.math import curve
from flab.base.types import Any, Dict

class System(nbase.ObjectIP):
    """Base class for systems.

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

    _attr: Dict[str, int] = {
        'units': 0b01, 'links': 0b01, 'layers': 0b01, 'mapping': 0b11}

    _copy: Dict[str, str] = {
        'params': '_params'}

    _default = {
        'params': {}, 'init': {}, 'optimize': {}, 'schedules': {}}

    _config = None
    _params = None

    def __init__(self, *args: Any, **kwds: Any) -> None:
        """Initialize system with content from arguments."""
        # get attribute and storage defaults from parent
        self._attr = {**getattr(super(), '_attr', {}), **self._attr}
        self._copy = {**getattr(super(), '_copy', {}), **self._copy}
        super().__init__(*args, **kwds)

    def configure(self, network = None):
        """Configure system to network."""

        if not otree.has_base(network, 'Network'):
            raise ValueError("network is not valid")

        return self._set_params(network = network)

    def initialize(self, dataset = None):
        """Initialize system parameters.

        Initialize all system parameters to dataset.

        Args:
            dataset: nemoa dataset instance

        """

        if not otree.has_base(dataset, 'Dataset'):
            raise ValueError("dataset is not valid")

        return self._set_params_init_units(dataset) \
            and self._set_params_init_links(dataset)

    def _check_network(self, network, *args, **kwds):
        """Check if network is valid for system."""
        if not otree.has_base(network, 'Network'): return False
        return True

    def _check_dataset(self, dataset, *args, **kwds):
        """Check if network is valid for system."""
        if not otree.has_base(dataset, 'Dataset'): return False
        return True

    def _get_algorithms(
            self, category = None, attribute = None, astree = False):
        """Get algorithms provided by system."""
        # get dictionary with all methods
        # with prefix '_get_' and attribute 'name'
        methods = otree.get_methods(self, pattern = '_get_*', val = 'name')

        # filter algorithms by given category
        if category is not None:
            for key, val in list(methods.items()):
                if val.get('category', None) != category:
                    del methods[key]

        # create flat structure if category is given or astree is False
        structured = {}
        if category or not astree:
            for ukey, udata in methods.items():
                if attribute: structured[udata['name']] = \
                    udata[attribute]
                else: structured[udata['name']] = udata
            return structured

        # create tree structure if category is not given
        categories = {
            ('system', 'evaluation'): None,
            ('system', 'units', 'evaluation'): 'units',
            ('system', 'links', 'evaluation'): 'links',
            ('system', 'relation', 'evaluation'): 'relation'
        }
        for ukey, udata in methods.items():
            if udata['category'] not in categories: continue
            ckey = categories[udata['category']]
            if ckey is None:
                if attribute: structured[udata['name']] = \
                    udata[attribute]
                else: structured[udata['name']] = udata
            else:
                if ckey not in structured: structured[ckey] = {}
                if attribute: structured[ckey][udata['name']] = \
                    udata[attribute]
                else: structured[ckey][udata['name']] = udata

        return structured

    def _get_algorithms_new(self, *args, **kwds):
        """Get list of all available algorithms for system."""

        import nemoa.model.analysis

        ctest = lambda s: s.split('.')[:2] == ['nemoa', 'system']
        clist = [obj.__name__ for obj in self.__class__.__mro__
            if ctest(obj.__module__)]

        return nemoa.model.analysis.algorithms(classes = clist, **kwds)

    def _get_algorithm(self, algorithm = None, *args, **kwds):
        """Get algorithm."""
        algorithms = self._get_algorithms(*args, **kwds)
        if algorithm not in algorithms: return None
        return algorithms[algorithm]

    def _get_unit(self, unit):
        """Get unit information."""

        # get layer of unit
        layer_ids = []
        for i in range(len(self._params['units'])):
            if unit in self._params['units'][i]['id']:
                layer_ids.append(i)
        if len(layer_ids) == 0: raise ValueError(
            "could not find unit '%s'." % (unit))
        if len(layer_ids) > 1: raise ValueError(
            "unit name '%s' is not unique." % (unit))
        layer_id = layer_ids[0]

        # get parameters of unit
        layer_params = self._params['units'][layer_id]
        layer_units = layer_params['id']
        layer_size = len(layer_units)
        layer_unit_id = layer_units.index(unit)
        unit_params = { 'layer_sub_id': layer_unit_id }
        for param in list(layer_params.keys()):
            layer_param_array = \
                numpy.array(layer_params[param]).flatten()
            if layer_param_array.size == 1:
                unit_params[param] = layer_param_array[0]
            elif layer_param_array.size == layer_size:
                unit_params[param] = layer_param_array[layer_unit_id]

        return unit_params

    def _get_units(self, groupby = None, **kwds):
        """Get units of system.

        Args:
            groupby (str or 'None): Name of a unit attribute
                used to group units. If groupby is not
                None, the returned units are grouped by the different
                values of this attribute. Grouping is only
                possible if every unit contains the attribute.
            **kwds: filter parameters of units. If kwds are given,
                only units that match the filter parameters are
                returned.

        Returns:
            If the argument 'groupby' is not set, a list of strings
            containing name identifiers of units is returned. If
            'groupby' is a valid unit attribute, the units are grouped
            by the values of this attribute.

        Examples:
            Get a list of all units grouped by layers:
                model.system.get('units', groupby = 'layer')
            Get a list of visible units:
                model.system.get('units', visible = True)

        """

        # test if system is initialized to network
        if not isinstance(self._params, dict) \
            or not 'units' in self._params:
            return []

        # filter units to given attributes
        units = []
        for layer in self._params['units']:
            valid = True
            for key in list(kwds.keys()):
                if layer[key] != kwds[key]:
                    valid = False
                    break
            if not valid: continue
            units += layer['id']
        if groupby is None: return units

        # group units by given attribute
        units_params = {}
        for unit in units:
            units_params[unit] = self._get_unit(unit)
        grouping_values = []
        for unit in units:
            if groupby not in list(units_params[unit].keys()):
                raise ValueError("""could not get units:
                    unknown parameter '%s'.""" % (groupby))
            grouping_value = units_params[unit][groupby]
            if not grouping_value in grouping_values:
                grouping_values.append(grouping_value)
        grouped_units = []
        for grouping_value in grouping_values:
            group = []
            for unit in units:
                if units_params[unit][groupby] == grouping_value:
                    group.append(unit)
            grouped_units.append(group)
        return grouped_units

    def _get_layers(self, **kwds):
        """Get unit layers of system.

        Returns:
            List of strings containing labels of unit layers that match
            a given property. The order is from input to output.

        Examples:
            return visible unit layers:
                model.system.get('layers', visible = True)

            search for unit layer 'test':
                model.system.get('layers', type = 'test')

        """

        # test if system is initialized to network
        if not isinstance(self._params, dict) \
            or not 'units' in self._params:
            return []

        filter_list = []
        for key in list(kwds.keys()):
            if key in list(self._params['units'][0].keys()):
                filter_list.append((key, kwds[key]))

        layers = []
        for layer in self._params['units']:
            valid = True
            for key, val in filter_list:
                if layer[key] != val:
                    valid = False
                    break
            if valid: layers.append(layer['layer'])

        return layers

    def _get_layer(self, layer):
        if layer not in self._units:
            raise ValueError(f"layer '{layer}' is not valid")
        return self._units[layer].params

    def _get_link(self, link):
        if not isinstance(link, tuple):
            raise ValueError(f"link '{str(link)}' is not valid")

        src, tgt = link

        layers = [layer['layer'] for layer in self._params['units']]

        src_unit = self._get_unit(src)
        src_id = src_unit['layer_sub_id']
        src_layer = src_unit['layer']
        src_layer_id = layers.index(src_layer)
        src_layer_params = self._params['units'][src_layer_id]

        tgt_unit = self._get_unit(tgt)
        tgt_id = tgt_unit['layer_sub_id']
        tgt_layer = tgt_unit['layer']
        tgt_layer_id = layers.index(tgt_layer)
        tgt_layer_params = self._params['units'][tgt_layer_id]

        link_layer_params = \
            self._params['links'][(src_layer_id, tgt_layer_id)]
        link_layer_size = \
            len(src_layer_params['id']) * len(tgt_layer_params['id'])

        # get link parameters
        link_params = {}
        for param in list(link_layer_params.keys()):
            layer_param_array = \
                numpy.array(link_layer_params[param])
            if layer_param_array.size == 1:
                link_params[param] = link_layer_params[param]
            elif layer_param_array.size == link_layer_size:
                link_params[param] = layer_param_array[src_id, tgt_id]

        # calculate additional link parameters
        layer_weights = link_layer_params['W']
        layer_adjacency = link_layer_params['A']
        link_weight = link_params['W']
        link_adjacency = link_params['A']

        # calculate normalized weight of link (per link layer)
        if link_weight == 0.0:
            link_norm_weight = 0.0
        else:
            adjacency_sum = numpy.sum(layer_adjacency)
            weight_sum = numpy.sum(
                numpy.abs(layer_adjacency * layer_weights))
            link_norm_weight = link_weight * adjacency_sum / weight_sum

        # calculate intensified weight of link (per link layer)
        if link_norm_weight == 0.0: link_intensity = 0.0
        else:
            link_max_norm = numpy.amax(numpy.abs(layer_adjacency
                * layer_weights)) * adjacency_sum / weight_sum
            link_intensity = curve.dialogistic(link_norm_weight,
                scale = 0.7 * link_max_norm, sigma = 10.)

        link_params['layer'] = (src_layer, tgt_layer)
        link_params['layer_sub_id'] = (src_id, tgt_id)
        link_params['adjacency'] = link_params['A']
        link_params['weight'] = link_params['W']
        link_params['sign'] = numpy.sign(link_params['W'])
        link_params['normal'] = link_norm_weight
        link_params['intensity'] = link_intensity

        return link_params

    def _get_links(self, groupby = None, **kwds):
        """Get links of system.

        Args:
            groupby (str or None): Name of a link attribute
                used to group links. If groupby is not
                None, the returned links are grouped by the different
                values of this attribute. Grouping is only
                possible if every link contains the attribute.
            **kwds: filter attributs of links. If kwds are given,
                only links that match the filter attributes are
                returned.

        Returns:
            If the argument 'groupby' is not set, a list of strings
            containing name identifiers of links is returned. If
            'groupby' is a valid link attribute, the links are grouped
            by the values of this attribute.

        Examples:
            Get a list of all links grouped by layers:
                model.system.get('links', groupby = 'layer')
            Get a list of links with weight = 0.0:
                model.system.get('links', weight = 0.0)

        """

        # test if system is initialized to network
        if not isinstance(self._params, dict) \
            or not 'links' in self._params:
            return []

        # filter links by given attributes
        layers = self._get_layers()
        if not layers: return False
        links = []
        links_params = {}

        for layer_id in range(len(layers) - 1):
            src_layer = layers[layer_id]
            src_units = self._params['units'][layer_id]['id']
            tgt_layer = layers[layer_id + 1]
            tgt_units = self._params['units'][layer_id + 1]['id']
            link_layer_id = (layer_id, layer_id + 1)
            link_layer_params = self._params['links'][link_layer_id]

            for src_unit in src_units:
                for tgt_unit in tgt_units:
                    link = (src_unit, tgt_unit)
                    link_params = self._get_link(link)
                    if not link_params['A']: continue
                    valid = True
                    for key in list(kwds.keys()):
                        if not link_params[key] == kwds[key]:
                            valid = False
                            break
                    if not valid: continue
                    links.append(link)
                    links_params[link] = link_params
        if groupby is None: return links

        # group links by given attribute
        grouping_values = []
        for link in links:
            if groupby not in links_params[link]:
                raise ValueError("""could not get links:
                    unknown link attribute '%s'.""" % (groupby))
            grouping_value = links_params[link][groupby]
            if grouping_value not in grouping_values:
                grouping_values.append(grouping_value)
        grouped_links = []
        for grouping_value in grouping_values:
            group = []
            for link in links:
                if links_params[link][groupby] == grouping_value:
                    group.append(link)
            grouped_links.append(group)
        return grouped_links

    def _get_mapping(self, src = None, tgt = None):
        """Get mapping of unit layers from source to target.

        Args:
            src: name of source unit layer
            tgt: name of target unit layer

        Returns:
            tuple with names of unit layers from source to target.

        """

        if 'mapping' in self._params: mapping = self._params['mapping']
        else:
            mapping = tuple([l['layer'] for l in self._params['units']])

        sid = mapping.index(src) \
            if isinstance(src, str) and src in mapping else 0
        tid = mapping.index(tgt) \
            if isinstance(tgt, str) and tgt in mapping else len(mapping)

        return mapping[sid:tid + 1] if sid <= tid \
            else mapping[tid:sid + 1][::-1]

    def _get_params(self, key = None, *args, **kwds):
        """Get configuration or configuration value."""

        import copy

        if key is None: return copy.deepcopy(self._params)

        if isinstance(key, str) and key in list(self._params.keys()):
            if isinstance(self._params[key], dict):
                return copy.deepcopy(self._params[key])
            return self._params[key]

        raise ValueError("""could not get parameters:
            unknown key '%s'.""" % key)

    @catalog.objective(
        name     = 'error',
        category = ('system', 'evaluation'),
        args     = 'all',
        formater = lambda val: '%.3f' % (val),
        optimum  = 'min')
    def _get_error(self, *args, **kwds):
        """Mean data reconstruction error of output units."""
        return numpy.mean(self._get_uniterror(*args, **kwds))

    @catalog.custom(
        name     = 'accuracy',
        category = ('system', 'evaluation'),
        args     = 'all',
        formater = lambda val: '%.1f%%' % (val * 100.),
        optimum  = 'max' )
    def _get_accuracy(self, *args, **kwds):
        """Mean data reconstruction accuracy of output units."""
        return numpy.mean(self._get_unitaccuracy(*args, **kwds))

    @catalog.custom(
        name     = 'precision',
        category = ('system', 'evaluation'),
        args     = 'all',
        formater = lambda val: '%.1f%%' % (val * 100.),
        optimum  = 'max' )
    def _get_precision(self, *args, **kwds):
        """Mean data reconstruction precision of output units."""
        return numpy.mean(self._get_unitprecision(*args, **kwds))

    @catalog.custom(
        name     = 'units_mean',
        category = ('system', 'units', 'evaluation'),
        args     = 'input',
        retfmt   = 'scalar',
        formater = lambda val: '%.3f' % (val),
        plot     = 'diagram' )

    def _get_units_mean(self, data, mapping = None, block = None):
        """Mean values of reconstructed target units.

        Args:
            data: numpy array containing source data corresponding to
                the source unit layer (first argument of the mapping)
            mapping: n-tuple of strings containing the mapping
                from source unit layer (first argument of tuple)
                to target unit layer (last argument of tuple)
            block: list of strings containing labels of source units
                that are 'blocked' by setting their values to the means
                of their values.

        Returns:
            Numpy array of shape (targets).

        """

        if mapping is None: mapping = self._get_mapping()
        if block is None: model_out = self._get_unitexpect(data[0], mapping)
        else:
            data_in_copy = numpy.copy(data)
            for i in block:
                data_in_copy[:,i] = numpy.mean(data_in_copy[:,i])
            model_out = self._get_unitexpect(
                data_in_copy, mapping)

        return model_out.mean(axis = 0)

    @catalog.custom(
        name     = 'units_variance',
        category = ('system', 'units', 'evaluation'),
        args     = 'input',
        retfmt   = 'scalar',
        formater = lambda val: '%.3f' % (val),
        plot     = 'diagram'
    )
    def _get_units_variance(self, data, mapping = None, block = None):
        """Return variance of reconstructed unit values.

        Args:
            data: numpy array containing source data corresponding to
                the first layer in the mapping
            mapping: n-tuple of strings containing the mapping
                from source unit layer (first argument of tuple)
                to target unit layer (last argument of tuple)
            block: list of strings containing labels of source units
                that are blocked by setting the values to their means
        """

        if mapping is None: mapping = self._get_mapping()
        if block is None:
            model_out = self._get_unitexpect(data, mapping)
        else:
            data_in_copy = numpy.copy(data)
            for i in block:
                data_in_copy[:,i] = numpy.mean(data_in_copy[:,i])
            model_out = self._get_unitexpect(data_in_copy, mapping)

        return model_out.var(axis = 0)

    @catalog.custom(
        name     = 'units_expect',
        category = ('system', 'units', 'evaluation'),
        args     = 'input',
        retfmt   = 'vector',
        formater = lambda val: '%.3f' % (val),
        plot     = 'histogram'
    )
    def _get_unitexpect(self, data, mapping = None, block = None):
        """Expectation values of target units.

        Args:
            data: numpy array containing source data corresponding to
                the source unit layer (first argument of the mapping)
            mapping: n-tuple of strings containing the mapping
                from source unit layer (first argument of tuple)
                to target unit layer (last argument of tuple)
            block: list of strings containing labels of source units
                that are 'blocked' by setting their values to the means
                of their values.

        Returns:
            Numpy array of shape (data, targets).

        """

        if mapping is None: mapping = self._get_mapping()
        if block is None: in_data = data
        else:
            in_data = numpy.copy(data)
            for i in block: in_data[:,i] = numpy.mean(in_data[:,i])
        if len(mapping) == 2: return self._units[mapping[1]].expect(
            in_data, self._units[mapping[0]].params)
        out_data = numpy.copy(in_data)
        for id in range(len(mapping) - 1):
            out_data = self._units[mapping[id + 1]].expect(
                out_data, self._units[mapping[id]].params)

        return out_data


    @catalog.custom(
        name     = 'units_values',
        category = ('system', 'units', 'evaluation'),
        args     = 'input',
        retfmt   = 'vector',
        formater = lambda val: '%.3f' % (val),
        plot     = 'histogram' )

    def _get_unitvalues(self, data, mapping = None, block = None,
        expect_last = False):
        """Unit maximum likelihood values of target units.

        Args:
            data: numpy array containing source data corresponding to
                the source unit layer (first argument of the mapping)
            mapping: n-tuple of strings containing the mapping
                from source unit layer (first argument of tuple)
                to target unit layer (last argument of tuple)
            block: list of strings containing labels of source units
                that are 'blocked' by setting their values to the means
                of their values.
            expect_last: return expectation values of the units
                for the last step instead of maximum likelihood values.

        Returns:
            Numpy array of shape (data, targets).

        """

        if mapping is None: mapping = self._get_mapping()
        if block is None: in_data = data
        else:
            in_data = numpy.copy(data)
            for i in block: in_data[:,i] = numpy.mean(in_data[:,i])
        if expect_last:
            if len(mapping) == 1:
                return in_data
            elif len(mapping) == 2:
                return self._units[mapping[1]].expect(
                    self._units[mapping[0]].get_samples(in_data),
                    self._units[mapping[0]].params)
            return self._units[mapping[-1]].expect(
                self._get_unitvalues(data, mapping[0:-1]),
                self._units[mapping[-2]].params)
        else:
            if len(mapping) == 1:
                return self._units[mapping[0]].get_values(in_data)
            elif len(mapping) == 2:
                return self._units[mapping[1]].get_values(
                    self._units[mapping[1]].expect(in_data,
                    self._units[mapping[0]].params))
            data = numpy.copy(in_data)
            for id in range(len(mapping) - 1):
                data = self._units[mapping[id + 1]].get_values(
                    self._units[mapping[id + 1]].expect(data,
                    self._units[mapping[id]].params))
            return data

    @catalog.custom(
        name     = 'units_samples',
        category = ('system', 'units', 'evaluation'),
        args     = 'input',
        retfmt   = 'vector',
        formater = lambda val: '%.3f' % (val),
        plot     = 'histogram' )

    def _get_unitsamples(self, data, mapping = None,
        block = None, expect_last = False):
        """Sampled unit values of target units.

        Args:
            data: numpy array containing source data corresponding to
                the source unit layer (first argument of the mapping)
            mapping: n-tuple of strings containing the mapping
                from source unit layer (first argument of tuple)
                to target unit layer (last argument of tuple)
            block: list of strings containing labels of source units
                that are 'blocked' by setting their values to the means
                of their values.
            expect_last: return expectation values of the units
                for the last step instead of sampled values

        Returns:
            Numpy array of shape (data, targets).

        """

        if mapping is None: mapping = self._get_mapping()
        if block is None: in_data = data
        else:
            in_data = numpy.copy(data)
            for i in block: in_data[:,i] = numpy.mean(in_data[:,i])
        if expect_last:
            if len(mapping) == 1:
                return data
            elif len(mapping) == 2:
                return self._units[mapping[1]].expect(
                    self._units[mapping[0]].get_samples(data),
                    self._units[mapping[0]].params)
            return self._units[mapping[-1]].expect(
                self._get_unitsamples(data, mapping[0:-1]),
                self._units[mapping[-2]].params)
        else:
            if len(mapping) == 1:
                return self._units[mapping[0]].get_samples(data)
            elif len(mapping) == 2:
                return self._units[mapping[1]].get_samples_from_input(
                    data, self._units[mapping[0]].params)
            data = numpy.copy(data)
            for id in range(len(mapping) - 1):
                data = \
                    self._units[mapping[id + 1]].get_samples_from_input(
                    data, self._units[mapping[id]].params)
            return data

    @catalog.custom(
        name     = 'units_residuals',
        category = ('system', 'units', 'evaluation'),
        args     = 'all',
        retfmt   = 'vector',
        formater = lambda val: '%.3f' % (val),
        plot     = 'histogram'
    )
    def _get_unitresiduals(self, data, mapping = None, block = None):
        """Reconstruction residuals of target units.

        Args:
            data: 2-tuple of numpy arrays containing source and target
                data corresponding to the first and the last argument
                of the mapping
            mapping: n-tuple of strings containing the mapping
                from source unit layer (first argument of tuple)
                to target unit layer (last argument of tuple)
            block: list of strings containing labels of source units
                that are 'blocked' by setting their values to the means
                of their values.

        Returns:
            Numpy array of shape (data, targets).

        """

        d_src, d_tgt = data

        # set mapping: inLayer to outLayer (if not set)
        if mapping is None: mapping = self._get_mapping()

        # set unit values to mean (optional)
        if isinstance(block, list):
            d_src = numpy.copy(d_src)
            for i in block: d_src[:, i] = numpy.mean(d_src[:, i])

        # calculate estimated output values
        m_out = self._get_unitexpect(d_src, mapping)

        # calculate residuals
        return d_tgt - m_out

    @catalog.custom(
        name     = 'units_error',
        category = ('system', 'units', 'evaluation'),
        args     = 'all',
        retfmt   = 'scalar',
        formater = lambda val: '%.3f' % (val),
        plot     = 'diagram'
    )
    def _get_uniterror(self, data, norm = 'MSE', **kwds):
        """Unit reconstruction error.

        The unit reconstruction error is defined by:
            error := norm(residuals)

        Args:
            data: 2-tuple of numpy arrays containing source and target
                data corresponding to the first and the last layer in
                the mapping
            mapping: n-tuple of strings containing the mapping
                from source unit layer (first argument of tuple)
                to target unit layer (last argument of tuple)
            block: list of strings containing labels of source units
                that are blocked by setting the values to their means
            norm: used norm to calculate data reconstuction error from
                residuals. see flab.base.vector.norm for a list
                of provided norms

        """

        from nemoa.math import vector

        # TODO: use vector
        #error = vector.distance(x, y, metric=metric)
        res = self._get_unitresiduals(data, **kwds)
        error = numpy.mean(numpy.square(res), axis=0)

        return error

    @catalog.custom(
        name     = 'units_accuracy',
        category = ('system', 'units', 'evaluation'),
        args     = 'all',
        retfmt   = 'scalar',
        formater = lambda val: '%.3f' % (val),
        plot     = 'diagram')

    def _get_unitaccuracy(self, data, norm = 'MSE', **kwds):
        """Unit reconstruction accuracy.

        The unit reconstruction accuracy is defined by:
            accuracy := 1 - norm(residuals) / norm(data).

        Args:
            data: 2-tuple of numpy arrays containing source and target
                data corresponding to the first and the last layer
                in the mapping
            mapping: n-tuple of strings containing the mapping
                from source unit layer (first argument of tuple)
                to target unit layer (last argument of tuple)
            block: list of strings containing labels of source units
                that are blocked by setting the values to their means
            norm: used norm to calculate accuracy
                see flab.base.vector.norm for a list of provided
                norms

        """
        from nemoa.math import vector

        # TODO: use vector
        #error = vector.distance(x, y, metric=metric)
        res = self._get_unitresiduals(data, **kwds)
        normres = numpy.mean(numpy.square(res), axis=0)
        normdat = numpy.mean(numpy.square(data[1]), axis=0)

        return 1. - normres / normdat

    @catalog.custom(
        name     = 'units_precision',
        category = ('system', 'units', 'evaluation'),
        args     = 'all',
        retfmt   = 'scalar',
        formater = lambda val: '%.3f' % (val),
        plot     = 'diagram' )

    def _get_unitprecision(self, data, norm='SD', **kwds):
        """Unit reconstruction precision.

        The unit reconstruction precision is defined by:
            precision := 1 - dev(residuals) / dev(data).

        Args:
            data: 2-tuple of numpy arrays containing source and target
                data corresponding to the first and the last layer
                in the mapping
            mapping: n-tuple of strings containing the mapping
                from source unit layer (first argument of tuple)
                to target unit layer (last argument of tuple)
            block: list of strings containing labels of source units
                that are blocked by setting the values to their means
            norm: used norm to calculate deviation for precision
                see flab.base.vector.norm for a list of provided
                norms

        """

        from nemoa.math import vector

        res = self._get_unitresiduals(data, **kwds)
        devres = vector.length(res, norm=norm)
        devdat = vector.length(data[1], norm=norm)

        return 1. - devres / devdat

    @catalog.custom(
        name     = 'correlation',
        category = ('system', 'relation', 'evaluation'),
        directed = False,
        signed   = True,
        normal   = True,
        args     = 'all',
        retfmt   = 'scalar',
        plot     = 'heatmap',
        formater = lambda val: '%.3f' % (val) )

    def _get_correlation(self, data, mapping = None, **kwds):
        """Data correlation between source and target units.

        Undirected data based relation describing the 'linearity'
        between variables (units).

        Args:
            data: 2-tuple with numpy arrays: input data and output data
            mapping: tuple of strings containing the mapping
                from input layer (first argument of tuple)
                to output layer (last argument of tuple)

        Returns:
            Numpy array of shape (source, target) containing pairwise
            correlation between source and target units.

        """

        # 2do: allow correlation between hidden units

        # calculate symmetric correlation matrix
        C = numpy.corrcoef(numpy.hstack(data).T)

        # create asymmetric output matrix
        mapping = self._get_mapping()
        src = self._get_units(layer = mapping[0])
        tgt = self._get_units(layer = mapping[-1])
        units = src + tgt
        R = numpy.zeros(shape = (len(src), len(tgt)))
        for i, u in enumerate(src):
            k = units.index(u)
            for j, v in enumerate(tgt):
                l = units.index(v)
                R[i, j] = C[k, l]

        return R

    @catalog.custom(
        name     = 'weightsumproduct',
        category = ('system', 'relation', 'evaluation'),
        directed = True,
        signed   = True,
        normal   = False,
        args     = 'all',
        retfmt   = 'scalar',
        plot     = 'heatmap',
        formater = lambda val: '%.3f' % (val) )

    def _get_weightsumproduct(self, data, mapping = None, **kwds):
        """Weight sum product from source to target units.

        Directed graph based relation describing the matrix product from
        source to target units (variables) given by mapping.

        Args:
            data: 2-tuple with numpy arrays: input data and output data
            mapping: tuple of strings containing the mapping
                from input layer (first argument of tuple)
                to output layer (last argument of tuple)

        Returns:
            Numpy array of shape (source, target) containing pairwise
            weight sum products from source to target units.

        """

        if not mapping: mapping = self._get_mapping()

        # calculate product of weight matrices
        for i in range(1, len(mapping))[::-1]:
            weights = self._units[mapping[i - 1]].links(
                {'layer': mapping[i]})['W']
            if i == len(mapping) - 1: wsp = weights.copy()
            else: wsp = numpy.dot(wsp.copy(), weights)

        return wsp.T

    @catalog.custom(
        name     = 'knockout',
        category = ('system', 'relation', 'evaluation'),
        directed = True,
        signed   = True,
        normal   = False,
        args     = 'all',
        retfmt   = 'scalar',
        plot     = 'heatmap',
        formater = lambda val: '%.3f' % (val)
    )
    def _get_knockout(self, data, mapping = None, **kwds):
        """Knockout effect from source to target units.

        Directed data manipulation based relation describing the
        increase of the data reconstruction error of a given output
        unit, when setting the values of a given input unit to its mean
        value.

        Knockout single source units and measure effects on target units
        respective to given data

        Args:
            data: 2-tuple with numpy arrays: input data and output data
            mapping: tuple of strings containing the mapping
                from input layer (first argument of tuple)
                to output layer (last argument of tuple)

        Returns:
            Numpy array of shape (source, target) containing pairwise
            knockout effects from source to target units.

        """

        if not mapping: mapping = self._get_mapping()
        in_labels = self._get_units(layer = mapping[0])
        out_labels = self._get_units(layer = mapping[-1])

        # prepare knockout matrix
        R = numpy.zeros((len(in_labels), len(out_labels)))

        # calculate unit values without knockout
        measure = kwds.get('measure', 'error')
        default = self._evaluate_units(data,
            func = measure, mapping = mapping)

        # calculate unit values with knockout
        for in_id, in_unit in enumerate(in_labels):

            # modify unit and calculate unit values
            knockout = self._evaluate_units(data, func = measure,
                mapping = mapping, block = [in_id])

            # store difference in knockout matrix
            for out_id, out_unit in enumerate(out_labels):
                R[in_id, out_id] = \
                    knockout[out_unit] - default[out_unit]

        return R

    @catalog.custom(
        name     = 'coinduction',
        category = ('system', 'relation', 'evaluation'),
        directed = True,
        signed   = False,
        normal   = False,
        args     = 'all',
        retfmt   = 'scalar',
        plot     = 'heatmap',
        formater = lambda val: '%.3f' % (val)
    )
    def _get_coinduction(self, data, *args, **kwds):
        """Coinduced deviation from source to target units."""

        # 2do: Open Problem:
        #       Normalization of CoInduction
        # Ideas:
        #       - Combine CoInduction with common distribution
        #         of induced values
        #       - Take a closer look to extreme Values

        # 2do: Proove:
        # CoInduction <=> Common distribution in 'deep' latent variables

        # algorithmic default parameters
        gauge = 0.1 # setting gauge lower than induction default
                    # to increase sensitivity

        mapping = self._get_mapping()
        srcunits = self._get_units(layer = mapping[0])
        tgtunits = self._get_units(layer = mapping[-1])

        # prepare cooperation matrix
        coop = numpy.zeros((len(srcunits), len(srcunits)))

        # create keawords for induction measurement

        if 'gauge' not in kwds: kwds['gauge'] = gauge

        # calculate induction without manipulation
        ind = self._get_induction(data, *args, **kwds)
        norm = numpy.sqrt((ind ** 2).sum(axis = 1))

        # calculate induction with manipulation
        for sid, sunit in enumerate(srcunits):

            # manipulate source unit values and calculate induction
            datamp = [numpy.copy(data[0]), data[1]]
            datamp[0][:, sid] = 10.0
            indmp = self._get_induction(datamp, *args, **kwds)

            print(('manipulation of', sunit))
            vals = [-2., -1., -0.5, 0., 0.5, 1., 2.]
            maniparr = numpy.zeros(shape = (len(vals), data[0].shape[1]))
            for vid, val in enumerate(vals):
                datamod = [numpy.copy(data[0]), data[1]]
                datamod[0][:, sid] = val #+ datamod[0][:, sid].mean()
                indmod = self._get_induction(datamod, *args, **kwds)
                maniparr[vid, :] = numpy.sqrt(((indmod - ind) ** 2).sum(axis = 1))
            manipvar = maniparr.var(axis = 0)
            #manipvar /= numpy.amax(manipvar)
            manipnorm = numpy.amax(manipvar)
            # 2do
            print((manipvar * 1000.))
            print((manipvar / manipnorm))

            coop[:,sid] = \
                numpy.sqrt(((indmp - ind) ** 2).sum(axis = 1))

        return coop

    @catalog.custom(
        name     = 'induction',
        category = ('system', 'relation', 'evaluation'),
        directed = True,
        signed   = False,
        normal   = False,
        args     = 'all',
        retfmt   = 'scalar',
        plot     = 'heatmap',
        formater = lambda val: '%.3f' % (val)
    )
    def _get_induction(self, data, mapping = None, points = 10,
        amplify = 1., gauge = 0.25, contrast = 20.0, **kwds):
        """Induced deviation from source to target units.

        Directed data manipulation based relation describing the induced
        deviation of reconstructed values of a given output unit, when
        manipulating the values of a given input unit.

        For each sample and for each source the induced deviation on
        target units is calculated by respectively fixing one sample,
        modifying the value for one source unit (n uniformly taken
        points from it's own distribution) and measuring the deviation
        of the expected valueas of each target unit. Then calculate the
        mean of deviations over a given percentage of the strongest
        induced deviations.

        Args:
            data: 2-tuple with numpy arrays: input data and output data
            mapping: tuple of strings containing the mapping
                from source layer (first argument of tuple)
                to target layer (last argument of tuple)
            points: number of points to extrapolate induction
            amplify: amplification of the modified source values
            gauge: cutoff for strongest induced deviations
            contrast:

        Returns:
            Numpy array of shape (source, target) containing pairwise
            induced deviation from source to target units.

        """

        if not mapping: mapping = self._get_mapping()
        inputs = self._get_units(layer = mapping[0])
        outputs = self._get_units(layer = mapping[-1])
        sdata = data[0]
        tdata = data[1]
        R = numpy.zeros((len(inputs), len(outputs)))

        # get indices of representatives
        r_ids = [int((i + 0.5) * int(float(sdata.shape[0])
            / points)) for i in range(points)]

        for inid, inunit in enumerate(inputs):
            try:
                i_curve = numpy.take(numpy.sort(sdata[:, inid]), r_ids)
            except Exception as err:
                raise ValueError(
                    "could not evaluate induction: unknown error") from err
            i_curve = amplify * i_curve

            # create output matrix for each output
            C = {outunit: numpy.zeros((sdata.shape[0], points)) \
                for outunit in outputs}

            for p_id in range(points):
                i_data  = sdata.copy()
                i_data[:, inid] = i_curve[p_id]

                o_expect = self._evaluate_units((i_data, data[1]),
                    func = 'units_expect', mapping = mapping)

                for outunit in outputs:
                    C[outunit][:, p_id] = o_expect[outunit]

            # calculate mean of standard deviations of outputs
            for outid, outunit in enumerate(outputs):

                # calculate norm by mean over part of data
                bound = int((1. - gauge) * sdata.shape[0])
                subset = numpy.sort(C[outunit].std(axis = 1))[bound:]
                norm = subset.mean() / tdata[:, outid].std()

                # calculate influence
                R[inid, outid] = norm

        # amplify contrast of induction
        A = R.copy()
        for inid, inunit in enumerate(inputs):
            for outid, outunit in enumerate(outputs):
                if ':' in outunit: inlabel = outunit.split(':')[1]
                else: inlabel = outunit
                if ':' in inunit: outlabel = inunit.split(':')[1]
                else: outlabel = inunit
                if inlabel == outlabel: A[inid, outid] = 0.0
        bound = numpy.amax(A)

        R = curve.dialogistic(R, scale = bound, sigma = contrast)

        return R

    def set(self, key = None, *args, **kwds):
        """Set meta information, configuration and parameters."""

        # set writeable attributes
        if self._attr.get(key, 0b00) & 0b10:
            return getattr(self, '_set_' + key)(*args, **kwds)

        # set configuration and parameters
        if key == 'links': return self._set_links(*args, **kwds)
        if key == 'mapping': return self._set_mapping(*args, **kwds)

        # import configuration and parameters
        if key == 'copy': return self._set_copy(*args, **kwds)
        if key == 'config': return self._set_config(*args, **kwds)
        if key == 'params': return self._set_params(*args, **kwds)

        raise KeyError(f"unknown key '{key}'")

    def _set_links(self, links = None, initialize = True):
        """Create link configuration from units."""

        if not self._configure_test_units(self._params):
            raise ValueError("""could not configure links:
                units have not been configured.""")

        if 'links' not in self._params: self._params['links'] = {}
        if not initialize: return self._set_params_create_links()

        # initialize adjacency matrices with default values
        for lid in range(len(self._params['units']) - 1):
            src_name = self._params['units'][lid]['layer']
            src_list = self._units[src_name].params['id']
            tgt_name = self._params['units'][lid + 1]['layer']
            tgt_list = self._units[tgt_name].params['id']
            lnk_name = (lid, lid + 1)

            if links:
                lnk_adja = numpy.zeros((len(src_list), len(tgt_list)))
            else:
                lnk_adja = numpy.ones((len(src_list), len(tgt_list)))

            self._params['links'][lnk_name] = {
                'source': src_name,
                'target': tgt_name,
                'A': lnk_adja.astype(float)
            }

        # set adjacency if links are given explicitly
        if links:

            for link in links:
                src, tgt = link

                # get layer id and layers sub id of link source
                src_unit = self._get_unit(src)
                if not src_unit: continue
                src_lid = src_unit['layer_id']
                src_sid = src_unit['layer_sub_id']

                # get layer id and layer sub id of link target
                tgt_unit = self._get_unit(tgt)
                if not tgt_unit: continue
                tgt_lid = tgt_unit['layer_id']
                tgt_sid = tgt_unit['layer_sub_id']

                # set adjacency
                if (src_lid, tgt_lid) not in self._params['links']: continue
                lnk_dict = self._params['links'][(src_lid, tgt_lid)]
                lnk_dict['A'][src_sid, tgt_sid] = 1.0

        return self._set_params_create_links() \
            and self._set_params_init_links()

    def _set_mapping(self, mapping):
        """Set the layer mapping of the system."""
        if not isinstance(mapping, tuple): raise Warning(
            "attribute 'mapping' requires datatype 'tuple'.")
        self._params['mapping'] = mapping
        return True

    def _set_copy(self, config = None, params = None):
        """Set configuration and parameters of system.

        Args:
            config (dict or None, optional): system configuration
            params (dict or None, optional): system parameters

        Returns:
            Bool which is True if and only if no error occured.

        """

        retval = True

        if config: retval &= self._set_config(config)
        if params: retval &= self._set_params(params)

        return retval

    def _set_config(self, config=None):
        """Set configuration from dictionary."""
        # initialize or update configuration dictionary
        if not hasattr(self, '_config') or not self._config:
            self._config = self._default.copy()
        if config:
            self._config = {**self._config, **config}

        # reset consistency check
        self._config['check'] = {
            'config': True, 'network': False, 'dataset': False }
        return True

    def _set_params(self, params = None, network = None, dataset = None):
        """Set system parameters from dictionary."""

        if not self._params:
            self._params = {'units': {}, 'links': {}}

        retval = True

        # get system parameters from dict
        if params:
            self._params = {**self._params, **params}

            # create instances of units and links
            retval &= self._set_params_create_units()
            retval &= self._set_params_create_links()

        # get system parameters from network
        elif network:
            if not otree.has_base(network, 'Network'):
                raise ValueError("network is not valid")

            # get unit layers and unit params
            layers = network.get('layers')
            units = [network.get('layer', layer) for layer in layers]

            for layer in units:
                layer['id'] = layer.pop('nodes')
                if 'type' in layer:
                    layer['class'] = layer.pop('type')
                elif layer['visible']:
                    layer['class'] = 'gauss'
                else: layer['class'] = 'sigmoid'

            # get link layers and link params
            links = {}
            for lid in range(len(units) - 1):
                src = units[lid]['layer']
                src_list = units[lid]['id']
                tgt = units[lid + 1]['layer']
                tgt_list = units[lid + 1]['id']
                link_layer = (lid, lid + 1)
                link_layer_shape = (len(src_list), len(tgt_list))
                link_layer_adj = numpy.zeros(link_layer_shape)
                links[link_layer] = {
                    'source': src, 'target': tgt,
                    'A': link_layer_adj.astype(float)}
            for link in network.edges:
                src, tgt = link
                found = False
                for lid in range(len(units) - 1):
                    if src in units[lid]['id']:
                        src_lid = lid
                        src_sid = units[lid]['id'].index(src)
                        tgt_lid = lid + 1
                        tgt_sid = units[lid + 1]['id'].index(tgt)
                        found = True
                        break
                if not found:
                    continue
                if (src_lid, tgt_lid) not in links:
                    continue
                links[(src_lid, tgt_lid)]['A'][src_sid, tgt_sid] = 1.0

            self._params['units'] = units
            self._params['links'] = links

            # create instances of units and links
            retval &= self._set_params_create_units()
            retval &= self._set_params_create_links()
            retval &= self._set_params_create_mapping()
            retval &= self._set_params_init_links()


        # initialize system parameters if dataset is given
        if dataset:
            if not otree.has_base(dataset, 'Dataset'):
                raise ValueError("""could not initialize
                    system: dataset instance is not valid.""")

            retval &= self._set_params_init_units(dataset)
            retval &= self._set_params_init_links(dataset)

        return retval

    def _set_params_create_units(self):
        # create instances of unit classes
        # and link units params to local params dict
        self._units = {}
        for layer_id in range(len(self._params['units'])):
            layer_params = self._params['units'][layer_id]
            layer_class = layer_params['class']
            layer_name = layer_params['layer']

            if layer_class == 'sigmoid':
                self._units[layer_name] \
                    = nemoa.system.commons.units.Sigmoid(layer_params)
            elif layer_class == 'gauss':
                self._units[layer_name] \
                    = nemoa.system.commons.units.Gauss(layer_params)
            else:
                raise ValueError("""could not create system:
                    unit class '%s' is not supported!"""
                    % (layer_class))

        return True

    def _set_params_create_links(self):

        self._links = {units: {'source': {}, 'target': {}}
            for units in list(self._units.keys())}

        for link_layer_id in list(self._params['links'].keys()):
            link_params = self._params['links'][link_layer_id]

            src = link_params['source']
            tgt = link_params['target']

            self._links[src]['target'][tgt] = link_params
            self._units[src].target = link_params
            self._links[tgt]['source'][src] = link_params
            self._units[tgt].source = link_params

        return True

    def _set_params_create_mapping(self):
        mapping = tuple([l['layer'] for l in self._params['units']])
        self._set_mapping(mapping)

        return True

    def _set_params_init_units(self, dataset=None):
        """Initialize unit parameteres.

        Args:
            dataset: nemoa dataset instance OR None

        """

        if dataset is not None and not otree.has_base(dataset, 'Dataset'):
            raise TypeError("invalid dataset argument given")

        for layer in list(self._units.keys()):
            if dataset is None:
                data = None
            elif not self._units[layer].params['visible']:
                data = None
            else:
                rows = self._config['params']['samples'] \
                    if 'samples' in self._config['params'] else '*'
                cols = layer \
                    if layer in dataset.get('colgroups') else '*'
                data = dataset.get('data', rows=rows, cols=cols)
            self._units[layer].initialize(data)

        return True

    def _set_params_init_links(self, dataset=None):
        """Initialize link parameteres (weights).

        If dataset is None, initialize weights matrices with zeros
        and all adjacency matrices with ones. if dataset is nemoa
        network instance, use data distribution to calculate random
        initial weights.

        Args:
            dataset (dataset instance OR None):

        Returns:


        """

        if dataset and not otree.has_base(dataset, 'Dataset'):
            raise TypeError("dataset is required to be of type dataset")

        for links in self._params['links']:
            source = self._params['links'][links]['source']
            target = self._params['links'][links]['target']
            A = self._params['links'][links]['A']
            x = len(self._units[source].params['id'])
            y = len(self._units[target].params['id'])
            alpha = self._config['init']['w_sigma'] \
                if 'w_sigma' in self._config['init'] else 1.
            sigma = numpy.ones([x, 1], dtype=float) * alpha / x

            if dataset is None:
                random = numpy.random.normal(numpy.zeros((x, y)), sigma)
            elif source in dataset.get('colgroups'):
                rows = self._config['params']['samples'] \
                    if 'samples' in self._config['params'] else '*'
                data = dataset.get('data', 100000, rows=rows, cols=source)
                delta = sigma * data.std(axis=0).reshape(x, 1) + 0.001
                random = numpy.random.normal(numpy.zeros((x, y)), delta)
            elif dataset.columns \
                == self._units[source].params['id']:
                rows = self._config['params']['samples'] \
                    if 'samples' in self._config['params'] else '*'
                data = dataset.get('data', 100000, rows=rows, cols='*')
                random = numpy.random.normal(numpy.zeros((x, y)),
                    sigma * numpy.std(data, axis=0).reshape(1, x).T)
            else: random = \
                numpy.random.normal(numpy.zeros((x, y)), sigma)

            self._params['links'][links]['W'] = A * random

        return True

    def evaluate(self, data, *args, **kwds):
        """Evaluate system using data."""

        # default system evaluation
        if not args:
            return self._evaluate_system(data, **kwds)

        # evaluate system units
        if args[0] == 'units':
            return self._evaluate_units(data, *args[1:], **kwds)

        # evaluate system links
        if args[0] == 'links':
            return self._evaluate_links(data, *args[1:], **kwds)

        # evaluate system relations
        if args[0] == 'relations':
            return self._evaluate_relation(data, *args[1:], **kwds)

        # evaluate system
        algorithms = list(
            self._get_algorithms(
                attribute='name', category=('system', 'evaluation')).values())

        if args[0] in algorithms:
            return self._evaluate_system(data, *args, **kwds)

        raise Warning(
            "unsupported system evaluation '%s'." % args[0])

    def _evaluate_system(self, data, func='accuracy', **kwds):
        """Evaluation of system.

        Args:
            data: 2-tuple of numpy arrays: source data and target data
            func: string containing the name of a supported system
                evaluation function. For a full list of available
                functions use: model.system.get('algorithms')

        Returns:
            Scalar system evaluation value (respective to given data).

        """

        # check if data is valid
        if not isinstance(data, tuple):
            raise ValueError('could not evaluate system: invalid data.')

        # get evaluation algorithms
        algorithms = self._get_algorithms(category=('system', 'evaluation'))
        if func not in list(algorithms.keys()):
            raise ValueError(
                f"could not evaluate system: unknown algorithm '{func}'")
        algorithm = algorithms[func]

        # prepare (non keyword) arguments for evaluation function
        evalargs = []
        if algorithm['args'] == 'none':
            pass
        elif algorithm['args'] == 'input':
            evalargs.append(data[0])
        elif algorithm['args'] == 'output':
            evalargs.append(data[1])
        elif algorithm['args'] == 'all':
            evalargs.append(data)

        # prepare keyword arguments for evaluation function
        evalkwds = kwds.copy()
        if 'mapping' not in evalkwds or evalkwds['mapping'] is None:
            evalkwds['mapping'] = self._get_mapping()

        # evaluate system
        return algorithm['reference'](*evalargs, **evalkwds)

    def _evaluate_units(self, data, func='units_accuracy', units=None, **kwds):
        """Evaluation of target units.

        Args:
            data: 2-tuple with numpy arrays: source and target data
            func: string containing name of unit evaluation function
                For a full list of available system evaluation functions
                see: model.system.get('algorithms')
            units: list of target unit names (within the same layer). If
                not given, all output units are selected.

        Returns:
            Dictionary with unit evaluation values for target units. The
            keys of the dictionary are given by the names of the target
            units, the values depend on the used evaluation function and
            are ether scalar (float) or vectorially (flat numpy array).

        """

        # check if data is valid
        if not isinstance(data, tuple):
            raise ValueError("could not evaluate system units: invalid data.")

        # get evaluation algorithms
        algorithms = self._get_algorithms(
            category=('system', 'units', 'evaluation'))
        if func not in algorithms:
            raise ValueError(
                "could not evaluate system units: "
                f"unknown algorithm name '{func}'")

        algorithm = algorithms[func]

        # prepare arguments for evaluation
        evalargs = {'input': [data[0]], 'output': [data[1]],
            'none': [], 'all': [data]}[algorithm.get('args', 'none')]
        evalkwds = kwds.copy()

        if isinstance(units, str):
            evalkwds['mapping'] = self._get_mapping(tgt = units)
        elif 'mapping' not in list(evalkwds.keys()) \
            or evalkwds['mapping'] is None:
            evalkwds['mapping'] = self._get_mapping()

        # evaluate units
        try:
            values = algorithm['reference'](*evalargs, **evalkwds)
        except Exception as err:
            raise ValueError('could not evaluate units') from err

        # create dictionary of target units
        labels = self._get_units(layer = evalkwds['mapping'][-1])
        if algorithm['retfmt'] == 'vector': return {unit: \
            values[:, uid] for uid, unit in enumerate(labels)}
        elif algorithm['retfmt'] == 'scalar': return {unit:
            values[uid] for uid, unit in enumerate(labels)}

        raise Warning(
            "could not evaluate system units: "
            "unknown return format '%s'." % algorithm['retfmt'])

    def _evaluate_links(self, data, func = 'energy', **kwds):
        """Evaluate system links respective to data.

        Args:
            data: 2-tuple of numpy arrays containing source and target
                data corresponding to the first and the last argument
                of the mapping
            mapping: n-tuple of strings containing the mapping
                from source unit layer (first argument of tuple)
                to target unit layer (last argument of tuple)
            func: string containing name of link evaluation function
                For a full list of available link evaluation functions
                see: model.system.get('algorithms')

        """

        # check if data is valid
        if not isinstance(data, tuple): raise ValueError(
            'could not evaluate system links: invalid data.')

        # get evaluation algorithms
        algorithms = self._get_algorithms(
            category = ('system', 'links', 'evaluation'))
        if func not in algorithms: raise ValueError(
            """could not evaluate system links:
            unknown algorithm name '%s'.""" % (func))
        algorithm = algorithms[func]

        # prepare (non keyword) arguments for evaluation
        if algorithm['args'] == 'none': evalargs = []
        elif algorithm['args'] == 'input': evalargs = [data[0]]
        elif algorithm['args'] == 'output': evalargs = [data[1]]
        elif algorithm['args'] == 'all': evalargs = [data]

        # prepare keyword arguments for evaluation
        evalkwds = kwds.copy()
        if isinstance(units, str):
            evalkwds['mapping'] = self._get_mapping(tgt = units)
        elif 'mapping' not in evalkwds or evalkwds['mapping'] is None:
            evalkwds['mapping'] = self._get_mapping()

        # perform evaluation
        try:
            values = algorithm['reference'](*evalargs, **evalkwds)
        except Exception as err:
            raise ValueError('could not evaluate links') from err

        # create link dictionary
        in_labels = self._get_units(layer = evalkwds['mapping'][-2])
        out_labels = self._get_units(layer = evalkwds['mapping'][-1])
        if algorithm['retfmt'] == 'scalar':
            rel_dict = {}
            for in_id, in_unit in enumerate(in_labels):
                for out_id, out_unit in enumerate(out_labels):
                    rel_dict[(in_unit, out_unit)] = \
                        values[in_id, out_id]
            return rel_dict
        raise Warning("""could not evaluate system links:
            unknown return format '%s'.""" % (algorithm['retfmt']))

    def _evaluate_relation(self, data, func = 'correlation',
        evalstat = True, **kwds):
        """Evaluate relations between source and target units.

        Args:
            data: 2-tuple with numpy arrays: input data and output data
            func: string containing name of unit relation function
                For a full list of available unit relation functions
                see: model.system.get('algorithms')
            transform: optional formula for transformation of relation
                which is executed by python eval() function. The usable
                variables are:
                    M: for the relation matrix as numpy array with shape
                        (source, target)
                    C: for the correlation matrix as numpy array with
                        shape (source, target)
                Example: 'M**2 - C'
            format: string describing format of return values
                'array': return values as numpy array
                'dict': return values as python dictionary
            eval_stat: if format is 'dict' and eval_stat is True then
                the return dictionary includes additional statistical
                values:
                    min: minimum value of unit relation
                    max: maximum value of unit relation
                    mean: mean value of unit relation
                    std: standard deviation of unit relation

        Returns:
            Python dictionary or numpy array with unit relation values.

        """

        # check if data is valid
        if not isinstance(data, tuple): raise ValueError(
            'could not evaluate system unit relation: invalid data.')

        # get evaluation algorithms
        algorithms = self._get_algorithms(
            category = ('system', 'relation', 'evaluation'))
        if func not in algorithms: raise ValueError(
            """could not evaluate system unit relation:
            unknown algorithm name '%s'.""" % (func))
        algorithm = algorithms[func]

        # prepare (non keyword) arguments for evaluation
        if algorithm['args'] == 'none': eargs = []
        elif algorithm['args'] == 'input': eargs = [data[0]]
        elif algorithm['args'] == 'output': eargs = [data[1]]
        elif algorithm['args'] == 'all': eargs = [data]

        # prepare keyword arguments for evaluation
        if 'transform' in list(kwds.keys()) \
            and isinstance(kwds['transform'], str):
            transform = kwds['transform']
            del kwds['transform']
        else: transform = ''
        if 'format' in list(kwds.keys()) \
            and isinstance(kwds['format'], str):
            retfmt = kwds['format']
            del kwds['format']
        else: retfmt = 'dict'
        ekwds = kwds.copy()
        if 'mapping' not in ekwds or ekwds['mapping'] is None:
            ekwds['mapping'] = self._get_mapping()

        # perform evaluation
        values = algorithm['reference'](*eargs, **ekwds)

        # create formated return values as matrix or dict
        # (for scalar relation evaluations)
        if algorithm['retfmt'] == 'scalar':
            # (optional) transform relation using 'transform' string
            if transform:
                M = values
                # 2do: calc real relation
                if 'C' in transform:
                    # TODO -> will lead to error
                    C = self._get_units_correlation(data)
                try:
                    T = eval(transform)
                    values = T
                except Exception as err:
                    raise ValueError(
                        "could not transform relations: "
                        "invalid syntax") from err

            # create formated return values
            if retfmt == 'array':
                retval = values
            elif retfmt == 'dict':
                from nemoa.math import matrix
                src = self._get_units(layer=ekwds['mapping'][0])
                tgt = self._get_units(layer=ekwds['mapping'][-1])
                retval = matrix.as_dict(values, labels=(src, tgt))
                if not evalstat:
                    return retval

                # (optional) add statistics
                filtered = []
                for src, tgt in retval:
                    sunit = src.split(':')[1] if ':' in src else src
                    tunit = tgt.split(':')[1] if ':' in tgt else tgt
                    if sunit == tunit: continue
                    filtered.append(retval[(src, tgt)])
                array = numpy.array(filtered)
                retval['max'] = numpy.amax(array)
                retval['min'] = numpy.amin(array)
                retval['mean'] = numpy.mean(array)
                retval['std'] = numpy.std(array)

                return retval

            else: raise Warning(
                'could not perform system unit relation evaluation')

            return False

    def save(self, *args, **kwds):
        """Export system to file."""
        return nemoa.system.save(self, *args, **kwds)

    def show(self, *args, **kwds):
        """Show system as image."""
        return nemoa.system.show(self, *args, **kwds)

    def copy(self, *args, **kwds):
        """Create copy of system."""
        return nemoa.system.copy(self, *args, **kwds)
