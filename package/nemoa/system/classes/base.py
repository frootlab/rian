# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import numpy
import time
import copy

class System:

    _default = {
        'params': {},
        'init': {},
        'optimize': {}}

    def __init__(self, network = None, **kwargs):
        """Import system from dictionary."""
        self._set_copy(**kwargs)
        if network: self._set_params(network = network)

    def configure(self, config = None, network = None):
        """Configure system to network and dataset."""

        retval = True

        if config: retval &= self._set_config(config)
        if network: retval &= self._set_params(network = network)

        return retval

    def _configure_set_dataset(self, dataset):
        """check if dataset columns match with visible units."""

        # test if argument dataset is nemoa dataset instance
        if not nemoa.type.is_dataset(dataset): return nemoa.log(
            'error', """could not configure system:
            dataset instance is not valid.""")

        # compare visible unit labels with dataset columns
        mapping = self.mapping()
        units = self._get_units(visible = True)
        if not dataset.get('columns') == units:
            return nemoa.log('error', """could not configure system:
                visible units differ from dataset columns.""")
        self._config['check']['dataset'] = True

        return True

    def _is_configured(self):
        """Return configuration state of system."""
        return self._config['check']['config'] \
            and self._config['check']['network'] \
            and self._config['check']['dataset']

    def _check_network(self, network, *args, **kwargs):
        """Check if network is valid for system."""
        if not nemoa.type.is_network(network): return False
        return True

    def _check_dataset(self, dataset, *args, **kwargs):
        """Check if network is valid for system."""
        if not nemoa.type.is_dataset(dataset): return False
        return True

    def _is_empty(self):
        """Return true if system is a dummy."""
        return False

    def get(self, key = None, *args, **kwargs):
        """Get meta information, configuration and parameters."""

        # get meta information
        if key == 'fullname': return self._get_fullname()
        if key == 'name': return self._get_name()
        if key == 'branch': return self._get_branch()
        if key == 'version': return self._get_version()
        if key == 'about': return self._get_about()
        if key == 'author': return self._get_author()
        if key == 'email': return self._get_email()
        if key == 'license': return self._get_license()
        if key == 'type': return self._get_type()

        # get configuration and parameters
        if key == 'unit': return self._get_unit(*args, **kwargs)
        if key == 'units': return self._get_units(*args, **kwargs)
        if key == 'link': return self._get_link(*args, **kwargs)
        if key == 'links': return self._get_links(*args, **kwargs)
        if key == 'layer': return self._get_layer(*args, **kwargs)
        if key == 'layers': return self._get_layers(*args, **kwargs)

        # export configuration and parameters
        if key == 'copy': return self._get_copy(*args, **kwargs)
        if key == 'config': return self._get_config(*args, **kwargs)
        if key == 'params': return self._get_params(*args, **kwargs)

        return nemoa.log('warning', "unknown key '%s'" % (key))

    def _get_fullname(self):
        """Get fullname of system."""
        fullname = ''
        name = self._get_name()
        if name: fullname += name
        branch = self._get_branch()
        if branch: fullname += '.' + branch
        version = self._get_version()
        if version: fullname += '.' + str(version)
        return fullname

    def _get_name(self):
        """Get name of system."""
        if 'name' in self._config: return self._config['name']
        return None

    def _get_branch(self):
        """Get branch of system."""
        if 'branch' in self._config: return self._config['branch']
        return None

    def _get_version(self):
        """Get version number of system branch."""
        if 'version' in self._config: return self._config['version']
        return None

    def _get_about(self):
        """Get description of system."""
        if 'about' in self._config: return self._config['about']
        return None

    def _get_author(self):
        """Get author of system."""
        if 'author' in self._config: return self._config['author']
        return None

    def _get_email(self):
        """Get email of author of system."""
        if 'email' in self._config: return self._config['email']
        return None

    def _get_license(self):
        """Get license of system."""
        if 'license' in self._config: return self._config['license']
        return None

    def _get_type(self):
        """Get type of system, using module and class name."""
        module_name = self.__module__.split('.')[-1]
        class_name = self.__class__.__name__
        return module_name + '.' + class_name

    def _get_unit(self, unit):

        # get layer of unit
        layer_ids = []
        for i in xrange(len(self._params['units'])):
            if unit in self._params['units'][i]['id']:
                layer_ids.append(i)
        if len(layer_ids) == 0: return nemoa.log('error',
            "could not find unit '%s'." % (unit))
        if len(layer_ids) > 1: return nemoa.log('error',
            "unit name '%s' is not unique." % (unit))
        layer_id = layer_ids[0]

        # get parameters of unit
        layer_params = self._params['units'][layer_id]
        layer_units = layer_params['id']
        layer_size = len(layer_units)
        layer_unit_id = layer_units.index(unit)
        unit_params = { 'layer_sub_id': layer_unit_id }
        for param in layer_params.keys():
            layer_param_array = \
                numpy.array(layer_params[param]).flatten()
            if layer_param_array.size == 1:
                unit_params[param] = layer_param_array[0]
            elif layer_param_array.size == layer_size:
                unit_params[param] = layer_param_array[layer_unit_id]

        return unit_params

    def _get_units(self, grouping = None, **kwargs):
        """Get units of system.

        Args:
            grouping: grouping parameter of units. If grouping is not
                None, the returned units are grouped by the different
                values of the grouping parameter. Grouping is only
                possible if every unit contains the parameter.
            **kwargs: filter parameters of units. If kwargs are given,
                only units that match the filter parameters are
                returned.

        Returns:
            If the argument 'grouping' is not set, a list of strings
            containing name identifiers of units is returned. If
            'grouping' is a valid unit parameter, the units are grouped
            by the values of the grouping parameter.

        Examples:
            Get a list of all units grouped by layers:
                model.system.get('units', grouping = 'layer')
            Get a list of visible units:
                model.system.get('units', visible = True)

        """

        # get filtered list of units
        units = []
        for layer in self._params['units']:
            valid = True
            for key in kwargs.keys():
                if not layer[key] == kwargs[key]:
                    valid = False
                    break
            if not valid: continue
            units += layer['id']
        if grouping == None: return units

        # group units by given grouping parameter
        units_params = {}
        for unit in units:
            units_params[unit] = self._get_unit(unit)
        grouping_values = []
        for unit in units:
            if not grouping in units_params[unit].keys():
                return nemoa.log('error', """could not get units:
                    unknown parameter '%s'.""" % (grouping))
            grouping_value = units_params[unit][grouping]
            if not grouping_value in grouping_values:
                grouping_values.append(grouping_value)
        grouped_units = []
        for grouping_value in grouping_values:
            group = []
            for unit in units:
                if units_params[unit][grouping] == grouping_value:
                    group.append(unit)
            grouped_units.append(group)
        return grouped_units

    def _get_layers(self, **kwargs):
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

        filter_list = []
        for key in kwargs.keys():
            if key in self._params['units'][0].keys():
                filter_list.append((key, kwargs[key]))

        layers = []
        for layer in self._params['units']:
            valid = True
            for key, val in filter_list:
                if not layer[key] == val:
                    valid = False
                    break
            if valid: layers.append(layer['layer'])

        return layers

    def _get_layer(self, layer):
        if not layer in self._units.keys():
            return nemoa.log('error', """could not get layer:
                layers '%s' is unkown.""" % (layer))
        return self._units[layer].params

    def _get_link(self, link):
        if not isinstance(link, tuple):
            return nemoa.log('error', """could not get link:
                link '%s' is unkown.""" % (edge))

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
        for param in link_layer_params.keys():
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

        # calculate normalized weight of link (normalized to link layer)
        if link_weight == 0.0:
            link_norm_weight = 0.0
        else:
            adjacency_sum = numpy.sum(layer_adjacency)
            weight_sum = numpy.sum(
                numpy.abs(layer_adjacency * layer_weights))
            link_norm_weight = link_weight * adjacency_sum / weight_sum

        link_params['layer'] = (src_layer, tgt_layer)
        link_params['layer_sub_id'] = (src_id, tgt_id)
        link_params['adjacency'] = link_params['A']
        link_params['weight'] = link_params['W']
        link_params['sign'] = numpy.sign(link_params['W'])
        link_params['normal'] = link_norm_weight

        return link_params

    def _get_links(self, grouping = None, **kwargs):
        """Get links of system.

        Args:
            grouping: grouping parameter of links. If grouping is not
                None, the returned links are grouped by the different
                values of the grouping parameter. Grouping is only
                possible if every links contains the parameter.
            **kwargs: filter parameters of links. If kwargs are given,
                only links that match the filter parameters are
                returned.

        Returns:
            If the argument 'grouping' is not set, a list of strings
            containing name identifiers of links is returned. If
            'grouping' is a valid link parameter, the links are grouped
            by the values of the grouping parameter.

        Examples:
            Get a list of all links grouped by layers:
                model.system.get('links', grouping = 'layer')
            Get a list of links with weight = 0.0:
                model.system.get('units', weight = 0.0)

        """

        # get links, filtered by kwargs
        layers = self._get_layers()
        if not layers: return False
        links = []
        links_params = {}

        for layer_id in xrange(len(layers) - 1):
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
                    for key in kwargs.keys():
                        if not link_params[key] == kwargs[key]:
                            valid = False
                            break
                    if not valid: continue
                    links.append(link)
                    links_params[link] = link_params
        if grouping == None: return links

        # group links by given grouping parameter
        grouping_values = []
        for link in links:
            if not grouping in links_params[link].keys():
                return nemoa.log('error', """could not get links:
                    unknown parameter '%s'.""" % (grouping))
            grouping_value = links_params[link][grouping]
            if not grouping_value in grouping_values:
                grouping_values.append(grouping_value)
        grouped_links = []
        for grouping_value in grouping_values:
            group = []
            for link in links:
                if links_params[link][grouping] == grouping_value:
                    group.append(link)
            grouped_links.append(group)
        return grouped_links

    def _get_copy(self, key = None, *args, **kwargs):
        """Get system copy as dictionary."""

        if key == None: return {
            'config': self._get_config(),
            'params': self._get_params() }

        if key == 'config': return self._get_config(*args, **kwargs)
        if key == 'params': return self._get_params(*args, **kwargs)

        return nemoa.log('error', """could not get system copy:
            unknown key '%s'.""" % (key))

    def _get_config(self, key = None, *args, **kwargs):
        """Get configuration or configuration value."""

        if key == None: return copy.deepcopy(self._config)

        if isinstance(key, str) and key in self._config.keys():
            if isinstance(self._config[key], dict):
                return self._config[key].copy()
            return self._config[key]

        return nemoa.log('error', """could not get configuration:
            unknown key '%s'.""" % (key))

    def _get_params(self, key = None, *args, **kwargs):
        """Get configuration or configuration value."""

        if key == None: return copy.deepcopy(self._params)

        if isinstance(key, str) and key in self._params.keys():
            if isinstance(self._params[key], dict):
                return self._params[key].copy()
            return self._params[key]

        return nemoa.log('error', """could not get parameters:
            unknown key '%s'.""" % (key))

    def set(self, key = None, *args, **kwargs):
        """Set meta information, configuration and parameters."""

        # set meta information
        if key == 'name': return self._set_name(*args, **kwargs)
        if key == 'branch': return self._set_branch(*args, **kwargs)
        if key == 'version': return self._set_version(*args, **kwargs)
        if key == 'about': return self._set_about(*args, **kwargs)
        if key == 'author': return self._set_author(*args, **kwargs)
        if key == 'email': return self._set_email(*args, **kwargs)
        if key == 'license': return self._set_license(*args, **kwargs)

        # set configuration and parameters
        #if key == 'units': return self._set_units(*args, **kwargs)
        if key == 'links': return self._set_links(*args, **kwargs)

        # import configuration and parameters
        if key == 'copy': return self._set_copy(*args, **kwargs)
        if key == 'config': return self._set_config(*args, **kwargs)
        if key == 'params': return self._set_params(*args, **kwargs)

        return nemoa.log('warning', "unknown key '%s'" % (key))

    def _set_name(self, system_name):
        """Set name of system."""
        if not isinstance(system_name, str): return False
        self._config['name'] = system_name
        return True

    def _set_branch(self, system_branch):
        """Set branch of system."""
        if not isinstance(system_branch, str): return False
        self._config['branch'] = system_branch
        return True

    def _set_version(self, system_version):
        """Set version number of system branch."""
        if not isinstance(system_version, int): return False
        self._config['version'] = system_version
        return True

    def _set_about(self, system_about):
        """Get description of system."""
        if not isinstance(system_about, str): return False
        self._config['about'] = system_about
        return True

    def _set_author(self, system_author):
        """Set author of system."""
        if not isinstance(system_author, str): return False
        self._config['author'] = system_author
        return True

    def _set_email(self, system_author_email):
        """Set email of author of system."""
        if not isinstance(system_author_email, str): return False
        self._config['email'] = system_author_email
        return True

    def _set_license(self, system_license):
        """Set license of system."""
        if not isinstance(system_license, str): return False
        self._config['license'] = system_license
        return True

    def _set_links(self, links = None, initialize = True):
        """Create link configuration from units."""

        if not self._configure_test_units(self._params):
            return nemoa.log('error', """could not configure links:
                units have not been configured.""")

        if not 'links' in self._params: self._params['links'] = {}
        if not initialize: return self._set_params_create_links()

        # initialize adjacency matrices with default values
        for lid in xrange(len(self._params['units']) - 1):
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
                if not (src_lid, tgt_lid) in self._params['links']:
                    continue
                lnk_dict = self._params['links'][(src_lid, tgt_lid)]
                lnk_dict['A'][src_sid, tgt_sid] = 1.0

        return self._set_params_create_links() \
            and self._set_params_init_links()

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

    def _set_config(self, config = None):
        """Set configuration from dictionary."""

        # initialize or update configuration dictionary
        if not hasattr(self, '_config') or not self._config:
            self._config = self._default.copy()
        if config:
            config_copy = copy.deepcopy(config)
            nemoa.common.dict_merge(config_copy, self._config)

        # reset consistency check
        self._config['check'] = {
            'config': True, 'network': False, 'dataset': False }
        return True

    def _set_params(self, params = None, network = None):
        """Set system parameters from dictionary."""

        if not hasattr(self, '_params'):
            self._params = {'units': {}, 'links': {}}

        # get system parameters from dict
        if params:
            nemoa.common.dict_merge(copy.deepcopy(params), self._params)

        # get system parameters from network
        elif network:
            if not nemoa.type.is_network(network):
                return nemoa.log('error', """could not configure system:
                    network instance is not valid!""")

            # get unit layers and unit params
            layers = network.get('layers')
            units = [network.get('layer', layer) for layer in layers]
            for layer in units: layer['id'] = layer.pop('nodes')

            # get link layers and link params
            links = {}
            for lid in xrange(len(units) - 1):
                src = units[lid]['layer']
                src_list = units[lid]['id']
                tgt = units[lid + 1]['layer']
                tgt_list = units[lid + 1]['id']
                link_layer = (lid, lid + 1)
                link_layer_shape = (len(src_list), len(tgt_list))
                link_layer_adj = numpy.zeros(link_layer_shape)
                links[link_layer] = {
                    'source': src, 'target': tgt,
                    'A': link_layer_adj.astype(float) }
            for link in network.get('edges'):
                src, tgt = link
                found = False
                for lid in xrange(len(units) - 1):
                    if src in units[lid]['id']:
                        src_lid = lid
                        src_sid = units[lid]['id'].index(src)
                        tgt_lid = lid + 1
                        tgt_sid = units[lid + 1]['id'].index(tgt)
                        found = True
                        break
                if not found: continue
                if not (src_lid, tgt_lid) in links: continue
                links[(src_lid, tgt_lid)]['A'][src_sid, tgt_sid] = 1.0

            params = {'units': units, 'links': links}
            nemoa.common.dict_merge(params, self._params)

        # get unit classes from system config
        # TODO: get unit classes from network
        visible_unit_class = self._config['params']['visible_class']
        hidden_unit_class = self._config['params']['hidden_class']
        for layer_id in xrange(len(self._params['units'])):
            if self._params['units'][layer_id]['visible'] == True:
                self._params['units'][layer_id]['class'] = \
                    visible_unit_class
            else:
                self._params['units'][layer_id]['class'] = \
                    hidden_unit_class

        # create instances of units and links
        self._set_params_create_units()
        self._set_params_create_links()

        if network: self._set_params_init_links()

        return True

    def _set_params_create_units(self):

        # create instances of unit classes
        # and link units params to local params dict
        self._units = {}
        for layer_id in xrange(len(self._params['units'])):
            layer_params = self._params['units'][layer_id]
            layer_class = layer_params['class']
            layer_name = layer_params['layer']
            if layer_class == 'sigmoid':
                self._units[layer_name] = self.UnitsSigmoid(layer_params)
            elif layer_class == 'gauss':
                self._units[layer_name] = self.UnitsGauss(layer_params)
            else:
                return nemoa.log('error', """could not create system:
                    unit class '%s' is not supported!"""
                    % (layer_class))

        return True

    def _set_params_create_links(self):

        self._links = {units: {'source': {}, 'target': {}}
            for units in self._units.keys()}

        for link_layer_id in self._params['links'].keys():
            link_params = self._params['links'][link_layer_id]

            src = link_params['source']
            tgt = link_params['target']

            self._links[src]['target'][tgt] = link_params
            self._units[src].target = link_params
            self._links[tgt]['source'][src] = link_params
            self._units[tgt].source = link_params

        return True

    def _set_params_init_units(self, dataset = None):
        """Initialize unit parameteres.

        Args:
            dataset: nemoa dataset instance OR None

        """

        if not (dataset == None) and not \
            nemoa.type.is_dataset(dataset):
            return nemoa.log('error', """could not initilize units:
            invalid dataset argument given!""")

        for layer in self._units.keys():
            if dataset == None:
                data = None
            elif not self._units[layer].params['visible']:
                data = None
            else:
                rows = self._config['params']['samples'] \
                    if 'samples' in self._config['params'] else '*'
                cols = layer \
                    if layer in dataset.get('colgroups') else '*'
                data = dataset.get('data', 100000, rows = rows, cols = cols)
            self._units[layer].initialize(data)

        return True

    def _set_params_init_links(self, dataset = None):
        """Initialize link parameteres (weights).

        If dataset is None, initialize weights matrices with zeros
        and all adjacency matrices with ones. if dataset is nemoa
        network instance, use data distribution to calculate random
        initial weights.

        Args:
            dataset: nemoa dataset instance OR None

        """

        if not(dataset == None) and \
            not nemoa.type.is_dataset(dataset): return nemoa.log(
            'error', """could not initilize link parameters:
            invalid dataset argument given!""")

        for links in self._params['links']:
            source = self._params['links'][links]['source']
            target = self._params['links'][links]['target']
            A = self._params['links'][links]['A']
            x = len(self._units[source].params['id'])
            y = len(self._units[target].params['id'])
            alpha = self._config['init']['w_sigma'] \
                if 'w_sigma' in self._config['init'] else 1.
            sigma = numpy.ones([x, 1], dtype = float) * alpha / x

            if dataset == None: random = \
                numpy.random.normal(numpy.zeros((x, y)), sigma)
            elif source in dataset.get('colgroups'):
                rows = self._config['params']['samples'] \
                    if 'samples' in self._config['params'] else '*'
                data = dataset.get('data', 100000, rows = rows, cols = source)
                random = numpy.random.normal(numpy.zeros((x, y)),
                    sigma * numpy.std(data, axis = 0).reshape(1, x).T)
            elif dataset.get('columns') \
                == self._units[source].params['id']:
                rows = self._config['params']['samples'] \
                    if 'samples' in self._config['params'] else '*'
                data = dataset.get('data', 100000, rows = rows, cols = '*')
                random = numpy.random.normal(numpy.zeros((x, y)),
                    sigma * numpy.std(data, axis = 0).reshape(1, x).T)
            else: random = \
                numpy.random.normal(numpy.zeros((x, y)), sigma)

            self._params['links'][links]['W'] = A * random

        return True

    def save(self, *args, **kwargs):
        """Export system to file."""
        return nemoa.system.save(self, *args, **kwargs)

    def show(self, *args, **kwargs):
        """Show system as image."""
        return nemoa.system.show(self, *args, **kwargs)

    def initialize(self, dataset = None):
        """Initialize system parameters.

        Initialize all system parameters to dataset.

        Args:
            dataset: nemoa dataset instance

        """

        if not nemoa.type.is_dataset(dataset):
            return nemoa.log('error', """could not initilize system
                parameters: invalid dataset instance given!""")

        return self._set_params_init_units(dataset) \
            and self._set_params_init_links(dataset)

    def optimize(self, dataset, schedule):
        """Optimize system parameters using data and given schedule."""

        # check if optimization schedule exists for current system
        # and merge default, existing and given schedule
        if not 'params' in schedule:
            config = self._default['optimize'].copy()
            nemoa.common.dict_merge(self._config['optimize'], config)
            self._config['optimize'] = config
        elif not self.get('type') in schedule['params']:
            return nemoa.log('error', """could not optimize model:
                optimization schedule '%s' does not include system '%s'
                """ % (schedule['name'], self.get('type')))
        else:
            config = self._default['optimize'].copy()
            nemoa.common.dict_merge(self._config['optimize'], config)
            nemoa.common.dict_merge(
                schedule['params'][self.get('type')], config)
            self._config['optimize'] = config

        # check dataset
        if (not 'check_dataset' in config
            or config['check_dataset'] == True) \
            and not self._check_dataset(dataset):
            return False

        # initialize tracker
        tracker = nemoa.system.classes.base.Tracker(self)
        tracker.set(data = self._get_test_data(dataset))

        # optimize system parameters
        return self._optimize(dataset, schedule, tracker)

    def evaluate(self, data, *args, **kwargs):

        # Default system evaluation
        if len(args) == 0:
            return self._eval_system(data, **kwargs)

        # Evaluate system units
        if args[0] == 'units':
            return self._eval_units(data, *args[1:], **kwargs)

        # Evaluate system links
        if args[0] == 'links':
            return self._eval_links(data, *args[1:], **kwargs)

        # Evaluate system relations
        if args[0] == 'relations':
            return self._eval_relation(data, *args[1:], **kwargs)

        # Evaluate system
        if args[0] in self._about_system().keys():
            return self._eval_system(data, *args, **kwargs)

        return nemoa.log('warning',
            "unsupported system evaluation '%s'" % (args[0]))

    def about(self, *args):
        """Metainformation of the system.

        Args:
            *args: strings, containing a breadcrump trail to
                a specific information about the system

        Examples:
            about('units', 'error')
                Returns information about the 'error' measurement
                function of the systems units.

        Returns:
            Dictionary containing generic information about various
            parts of the system.

        """

        # create information dictionary
        about = nemoa.common.dict_merge({
            'units': self._about_units(),
            'links': self._about_links(),
            'relations': self._about_relations()
        }, self._about_system())

        ret_dict = about
        path = ['system']
        for arg in args:
            if not isinstance(ret_dict, dict): return ret_dict
            if not arg in ret_dict.keys(): return nemoa.log('warning',
                "%s has no property '%s'" % (' → '.join(path), arg))
            path.append(arg)
            ret_dict = ret_dict[arg]
        if not isinstance(ret_dict, dict): return ret_dict
        return {key: ret_dict[key] for key in ret_dict.keys()}

    class Links:
        """Class to unify common ann link attributes."""

        params = {}

        def __init__(self): pass

        @staticmethod
        def energy(dSrc, dTgt, src, tgt, links, calc = 'mean'):
            """Return link energy as numpy array."""

            if src['class'] == 'gauss':
                M = - links['A'] * links['W'] \
                    / numpy.sqrt(numpy.exp(src['lvar'])).T
            elif src['class'] == 'sigmoid':
                M = - links['A'] * links['W']
            else: return nemoa.log('error', 'unsupported unit class')

            return numpy.einsum('ij,ik,jk->ijk', dSrc, dTgt, M)

        @staticmethod
        def get_updates(data, model):
            """Return weight updates of a link layer."""

            D = numpy.dot(data[0].T, data[1]) / float(data[1].size)
            M = numpy.dot(model[0].T, model[1]) / float(data[1].size)

            return { 'W': D - M }

        @staticmethod
        def get_updates_from_delta(data, delta):

            return { 'W': -numpy.dot(data.T, delta) / float(data.size) }

    class Units:
        """Base Class for Unit Layer.

        Unification of common unit layer functions and attributes.
        """

        params = {}
        source = {}
        target = {}

        def __init__(self, params = None):
            if params:
                self.params = params
                if not self.check(params): self.initialize()

        def expect(self, data, source):

            if source['class'] == 'sigmoid': return \
                self.expect_from_sigmoid_layer(data, source, self.weights(source))
            elif source['class'] == 'gauss': return \
                self.expect_from_gauss_layer(data, source, self.weights(source))

            return False

        def get_updates(self, data, model, source):

            return self.get_param_updates(data, model, self.weights(source))

        def get_delta(self, in_data, out_delta, source, target):

            return self.delta_from_bprop(in_data, out_delta,
                self.weights(source), self.weights(target))

        def get_samples_from_input(self, data, source):

            if source['class'] == 'sigmoid':
                return self.get_samples(
                    self.expect_from_sigmoid_layer(
                    data, source, self.weights(source)))
            elif source['class'] == 'gauss':
                return self.get_samples(
                    self.expect_from_gauss_layer(
                    data, source, self.weights(source)))

            return False

        def weights(self, source):

            if 'source' in self.source \
                and source['layer'] == self.source['source']:
                return self.source['W']
            elif 'target' in self.target \
                and source['layer'] == self.target['target']:
                return self.target['W'].T
            else: return nemoa.log('error', """could not get links:
                layers '%s' and '%s' are not connected!"""
                % (source['layer'], self.params['layer']))

        def links(self, source):

            if 'source' in self.source \
                and source['layer'] == self.source['source']:
                return self.source
            elif 'target' in self.target \
                and source['layer'] == self.target['target']:
                return {'W': self.target['W'].T, 'A': self.target['A'].T}
            else: return nemoa.log('error', """could not get links:
                layers '%s' and '%s' are not connected!"""
                % (source['name'], self.params['name']))

        def adjacency(self, source):

            if 'source' in self.source \
                and source['layer'] == self.source['source']:
                return self.source['A']
            elif 'target' in self.target \
                and source['layer'] == self.target['target']:
                return self.target['A'].T
            else: return nemoa.log('error', """could not get links:
                layers '%s' and '%s' are not connected!"""
                % (source['layer'], self.params['layer']))

    class UnitsSigmoid(Units):
        """Sigmoidal Unit Layer.

        Layer of units with sigmoidal activation function and bernoulli
        distributed sampling.

        """

        def initialize(self, data = None):
            """Initialize system parameters of sigmoid distributed units
            using data. """

            size = len(self.params['id'])
            shape = (1, size)
            self.params['bias'] = 0.5 * numpy.ones(shape)
            return True

        def update(self, updates):
            """Update parameter of sigmoid units. """

            if 'bias'in updates:
                self.params['bias'] += updates['bias']

            return True

        @staticmethod
        def remove(layer, select):
            """Delete selection (list of ids) of units from parameter arrays. """

            layer['bias'] = layer['bias'][0, [select]]

            return True

        @staticmethod
        def check(layer):

            return 'bias' in layer

        def energy(self, data):
            """Return system energy of sigmoidal units as numpy array. """

            bias = self.params['bias']

            return - data * bias

        def expect_from_sigmoid_layer(self, data, source, weights):
            """Return expected values of a sigmoid output layer
            calculated from a sigmoid input layer. """

            bias = self.params['bias']

            return nemoa.common.sigmoid(bias + numpy.dot(data, weights))

        def expect_from_gauss_layer(self, data, source, weights):
            """Return expected values of a sigmoid output layer
            calculated from a gaussian input layer. """

            bias = self.params['bias']
            sdev = numpy.sqrt(numpy.exp(source['lvar']))

            return nemoa.common.sigmoid(
                bias + numpy.dot(data / sdev, weights))

        def get_param_updates(self, data, model, weights):
            """Return parameter updates of a sigmoidal output layer
            calculated from real data and modeled data. """

            size = len(self.params['id'])

            return {'bias': numpy.mean(data[1] - model[1], axis = 0).reshape((1, size))}

        def get_updates_from_delta(self, delta):

            size = len(self.params['id'])

            return {'bias': - numpy.mean(delta, axis = 0).reshape((1, size))}

        def delta_from_bprop(self, data_in, delta_out, W_in, W_out):

            bias = self.params['bias']

            return numpy.dot(delta_out, W_out) * \
                nemoa.common.diff_sigmoid((bias + numpy.dot(data_in, W_in)))

        @staticmethod
        def grad(x):
            """Return gradiant of standard logistic function. """

            numpy.seterr(over = 'ignore')

            return ((1. / (1. + numpy.exp(-x)))
                * (1. - 1. / (1. + numpy.exp(-x))))

        @staticmethod
        def get_values(data):
            """Return median of bernoulli distributed layer
            calculated from expected values. """

            return (data > 0.5).astype(float)

        @staticmethod
        def get_samples(data):
            """Return sample of bernoulli distributed layer
            calculated from expected value. """

            return (data > numpy.random.rand(
                data.shape[0], data.shape[1])).astype(float)

        def get(self, unit):

            id = self.params['id'].index(unit)
            cl = self.params['class']
            visible = self.params['visible']
            bias = self.params['bias'][0, id]

            return {'label': unit, 'id': id, 'class': cl,
                'visible': visible, 'bias': bias}

    class UnitsGauss(Units):
        """Layer of Gaussian Linear Units (GLU).

        Artificial neural network units with linear activation function
        and gaussian sampling.

        """

        def initialize(self, data = None, v_sigma = 0.4):
            """Initialize parameters of gauss distributed units. """

            size = len(self.params['id'])
            if data == None:
                self.params['bias'] = \
                    numpy.zeros([1, size])
                self.params['lvar'] = \
                    numpy.log((v_sigma * numpy.ones((1, size))) ** 2)
            else:
                self.params['bias'] = \
                    numpy.mean(data, axis = 0).reshape(1, size)
                self.params['lvar'] = \
                    numpy.log((v_sigma * numpy.ones((1, size))) ** 2)

            return True

        def update(self, updates):
            """Update gaussian units parameters."""

            if 'bias' in updates:
                self.params['bias'] += updates['bias']
            if 'lvar' in updates:
                self.params['lvar'] += updates['lvar']

            return True

        def get_param_updates(self, data, model, weights):
            """Return parameter updates of a gaussian output layer
            calculated from real data and modeled data. """

            shape = (1, len(self.params['id']))
            var = numpy.exp(self.params['lvar'])
            bias = self.params['bias']

            updBias = numpy.mean(
                data[1] - model[1], axis = 0).reshape(shape) / var
            updLVarData = numpy.mean(
                0.5 * (data[1] - bias) ** 2 - data[1]
                * numpy.dot(data[0], weights), axis = 0)
            updLVarModel = numpy.mean(
                0.5 * (model[1] - bias) ** 2 - model[1]
                * numpy.dot(model[0], weights), axis = 0)
            updLVar = (updLVarData - updLVarModel).reshape(shape) / var

            return { 'bias': updBias, 'lvar': updLVar }

        def get_updates_from_delta(self, delta):
            # TODO: calculate update for lvar

            shape = (1, len(self.params['id']))
            bias = - numpy.mean(delta, axis = 0).reshape(shape)

            return { 'bias': bias }

        @staticmethod
        def remove(layer, select):
            """Delete selection (list of ids) of units from parameter arrays. """

            layer['bias'] = layer['bias'][0, [select]]
            layer['lvar'] = layer['lvar'][0, [select]]

            return True

        def expect_from_sigmoid_layer(self, data, source, weights):
            """Return expected values of a gaussian output layer
            calculated from a sigmoid input layer. """

            return self.params['bias'] + numpy.dot(data, weights)

        def expect_from_gauss_layer(self, data, source, weights):
            """Return expected values of a gaussian output layer
            calculated from a gaussian input layer. """

            bias = self.params['bias']
            sdev = numpy.sqrt(numpy.exp(source['lvar']))

            return bias + numpy.dot(data / sdev, weights)

        @staticmethod
        def grad(x):
            """Return gradient of activation function."""

            return 1.

        @staticmethod
        def check(layer):

            return 'bias' in layer and 'lvar' in layer

        def energy(self, data):

            bias = self.params['bias']
            var = numpy.exp(self.params['lvar'])
            energy = 0.5 * (data - bias) ** 2 / var

            return energy

        @staticmethod
        def get_values(data):
            """Return median of gauss distributed layer
            calculated from expected values."""

            return data

        def get_samples(self, data):
            """Return sample of gauss distributed layer
            calculated from expected values. """

            sigma = numpy.sqrt(numpy.exp(self.params['lvar']))
            return numpy.random.normal(data, sigma)

        def get(self, unit):

            id = self.params['id'].index(unit)

            cl = self.params['class']
            bias = self.params['bias'][0, id]
            lvar = self.params['lvar'][0, id]
            visible = self.params['visible']

            return {
                'label': unit, 'id': id, 'class': cl,
                'visible': visible, 'bias': bias, 'lvar': lvar }

class Tracker:

    _system = None # linked nemoa system instance
    _config = None # linked nemoa system optimization configuration
    _state = {}    # dictionary for tracking variables
    _store = {}    # dictionary for storage of optimization parameters

    def __init__(self, system):
        """Configure tracker to given nemoa system instance."""

        _state = {}
        _store = {}

        if not nemoa.type.is_system(system): return nemoa.log('warning',
            'could not configure tracker: system is not valid!')
        if not hasattr(system, '_config'): return nemoa.log('warning',
            'could not configure tracker: system contains no configuration!')
        if not 'optimize' in system._config: return nemoa.log('warning',
            'could not configure tracker: system contains no configuration for optimization!')

        # link system and system config
        self._system = system
        self._config = system._config['optimize']

        # init state
        now = time.time()

        self._state = {
            'epoch': 0,
            'data': None,
            'optimum': {},
            'continue': True,
            'obj_enable': self._config['tracker_obj_tracking_enable'],
            'obj_init_wait': self._config['tracker_obj_init_wait'],
            'obj_values': None,
            'obj_opt_value': None,
            'key_events': True,
            'key_events_started': False,
            'eval_enable': self._config['tracker_eval_enable'],
            'eval_prev_time': now,
            'eval_values': None,
            'estim_enable': self._config['tracker_estimate_time'],
            'estim_started': False,
            'estim_start_time': now
        }

    def get(self, key):
        if not key in self._state.keys(): return False
        return self._state[key]

    def set(self, **kwargs):
        found = True
        for key in kwargs.keys():
            if key in self._state.keys():
                self._state[key] = kwargs[key]
            else: found = False
        return found

    def read(self, key, id = -1):
        if not key in self._store.keys():
            self._store[key] = []
        elif len(self._store[key]) >= abs(id):
            return self._store[key][id]
        return {}

    def write(self, key, id = -1, append = False, **kwargs):
        if not key in self._store.keys():
            self._store[key] = []
        if len(self._store[key]) == (abs(id) - 1) or append == True:
            self._store[key].append(kwargs)
            return True
        if len(self._store[key]) < id: return nemoa.log('error',
            'could not write to store, wrong index!')
        self._store[key][id] = kwargs
        return True

    def _update_time_estimation(self):
        if not self._state['estim_enable']: return True

        if not self._state['estim_started']:
            nemoa.log("""estimating time for calculation
                of %i updates.""" % (self._config['updates']))
            self._state['estim_started'] = True
            self._state['estim_start_time'] = time.time()
            return True

        now = time.time()
        runtime = now - self._state['estim_start_time']
        if runtime > self._config['tracker_estimate_time_wait']:
            estim = (runtime / (self._state['epoch'] + 1)
                * self._config['updates'])
            estim_str = time.strftime('%H:%M',
                time.localtime(now + estim))
            nemoa.log('note', 'estimation: %ds (finishing time: %s)'
                % (estim, estim_str))
            self._state['estim_enable'] = False
            return True

        return True

    def update(self):
        """Update epoch and check termination criterions."""
        self._update_epoch()
        if self._state['key_events']: self._update_keypress()
        if self._state['estim_enable']: self._update_time_estimation()
        if self._state['obj_enable']: self._update_objective_function()
        if self._state['eval_enable']: self._update_evaluation()
        return self._state['continue']

    def _update_epoch(self):
        self._state['epoch'] += 1
        if self._state['epoch'] == self._config['updates']:
            self._state['continue'] = False
        return True

    def _update_keypress(self):
        """Check Keyboard."""
        if not self._state['key_events_started']:
            nemoa.log('note', """press 'q' if you want to abort
                the optimization""")
            self._state['key_events_started'] = True

        c = nemoa.common.getch()
        if isinstance(c, str):
            if c == 'q':
                nemoa.log('note', '... aborting optimization')
                self._state['continue'] = False

        return True

    def _update_objective_function(self):
        """Calculate objective function of system."""

        if self._state['data'] == None:
            nemoa.log('warning', """tracking the objective function
                is not possible: testdata is needed!""")
            self._state['obj_enable'] = False
            return False

        cfg = self._config
        interval = cfg['tracker_obj_update_interval']
        if self._state['continue'] \
            and not (self._state['epoch'] % interval == 0): return True

        # calculate objective function value
        func = cfg['tracker_obj_function']
        value = self._system.evaluate(
            data = self._state['data'], func = func)
        progr = float(self._state['epoch']) / float(cfg['updates'])

        # add objective function value to array
        if self._state['obj_values'] == None:
            self._state['obj_values'] = numpy.array([[progr, value]])
        else: self._state['obj_values'] = \
            numpy.vstack((self._state['obj_values'], \
            numpy.array([[progr, value]])))

        # (optional) check for new optimum
        if cfg['tracker_obj_keep_optimum']:
            # init optimum with first value
            if self._state['obj_opt_value'] == None:
                self._state['obj_opt_value'] = value
                self._state['optimum'] = \
                    {'params': self._system.get('copy', 'params')}
                return True
            # allways check last optimum
            if self._state['continue'] \
                and float(self._state['epoch']) / float(cfg['updates']) \
                < cfg['tracker_obj_init_wait']:
                return True

            type_of_optimum = self._system.about(func)['optimum']
            current_optimum = self._state['obj_opt_value']

            if type_of_optimum == 'min' and value < current_optimum:
                new_optimum = True
            elif type_of_optimum == 'max' and value > current_optimum:
                new_optimum = True
            else:
                new_optimum = False

            if new_optimum:
                self._state['obj_opt_value'] = value
                self._state['optimum'] = \
                    {'params': self._system.get('copy', 'params')}

            # set system parameters to optimum on last update
            if not self._state['continue']:
                return self._system.set('copy', **self._state['optimum'])

        return True

    def _update_evaluation(self):
        """Calculate evaluation function of system."""

        cfg = self._config
        now = time.time()

        if self._state['data'] == None:
            nemoa.log('warning', """tracking the evaluation function
                is not possible: testdata is needed!""")
            self._state['eval_enable'] = False
            return False

        if not self._state['continue']:
            func = cfg['tracker_eval_function']
            prop = self._system.about(func)
            value = self._system.evaluate(
                data = self._state['data'], func = func)
            out = 'found optimum with: %s = ' + prop['format']
            self._state['eval_enable'] = False
            return nemoa.log('note', out % (prop['name'], value))

        if ((now - self._state['eval_prev_time']) \
            > cfg['tracker_eval_time_interval']):
            func = cfg['tracker_eval_function']
            prop = self._system.about(func)
            value = self._system.evaluate(
                data = self._state['data'], func = func)
            progr = float(self._state['epoch']) \
                / float(cfg['updates']) * 100.

            # update time of last evaluation
            self._state['eval_prev_time'] = now

            # add evaluation to array
            if self._state['eval_values'] == None:
                self._state['eval_values'] = \
                    numpy.array([[progr, value]])
            else:
                self._state['eval_values'] = \
                    numpy.vstack((self._state['eval_values'], \
                    numpy.array([[progr, value]])))

            out = 'finished %.1f%%: %s = ' + prop['format']
            return nemoa.log('note', out % (progr, prop['name'], value))

        return False


