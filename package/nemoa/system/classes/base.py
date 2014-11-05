# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import numpy
import copy

class System:
    """System base class.

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
        type (str): String concatenation of module name and class name
            of the instance.
            Hint: Readonly wrapping attribute to get('type')
        version (int): Versionnumber of the resource.
            Hint: Read- & writeable wrapping attribute to get('version')
                and set('version', int).

    """

    _config  = None
    _params  = None
    _default = {'params': {}, 'init': {}, 'optimize': {}}
    _attr    = {'units': 'r', 'links': 'r', 'layers': 'r',
                'fullname': 'r', 'type': 'r', 'name': 'rw',
                'branch': 'rw', 'version': 'rw', 'about': 'rw',
                'author': 'rw', 'email': 'rw', 'license': 'rw'}
    _schedules = None

    def __init__(self, *args, **kwargs):
        """Import system from dictionary."""

        self._set_copy(**kwargs)

    def __getattr__(self, key):
        """Attribute wrapper to method get(key)."""

        if key in self._attr:
            if 'r' in self._attr[key]: return self.get(key)
            return nemoa.log('warning',
                "attribute '%s' can not be accessed directly.")

        raise AttributeError('%s instance has no attribute %r'
            % (self.__class__.__name__, key))

    def __setattr__(self, key, val):
        """Attribute wrapper to method set(key, val)."""

        if key in self._attr:
            if 'w' in self._attr[key]: return self.set(key, val)
            return nemoa.log('warning',
                "attribute '%s' can not be changed directly.")

        self.__dict__[key] = val

    def configure(self, network = None):
        """Configure system to network."""

        if not nemoa.type.is_network(network):
            return nemoa.log('error', """could not configure system:
                network is not valid.""")

        return self._set_params(network = network)

    def initialize(self, dataset = None):
        """Initialize system parameters.

        Initialize all system parameters to dataset.

        Args:
            dataset: nemoa dataset instance

        """

        if not nemoa.type.is_dataset(dataset):
            return nemoa.log('error', """could not initilize system:
                dataset is not valid.""")

        return self._set_params_init_units(dataset) \
            and self._set_params_init_links(dataset)

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

    def get(self, key = 'name', *args, **kwargs):
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

    def _get_units(self, groupby = None, **kwargs):
        """Get units of system.

        Args:
            groupby (str or 'None): Name of a unit attribute
                used to group units. If groupby is not
                None, the returned units are grouped by the different
                values of this attribute. Grouping is only
                possible if every unit contains the attribute.
            **kwargs: filter parameters of units. If kwargs are given,
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
            for key in kwargs.keys():
                if not layer[key] == kwargs[key]:
                    valid = False
                    break
            if not valid: continue
            units += layer['id']
        if groupby == None: return units

        # group units by given attribute
        units_params = {}
        for unit in units:
            units_params[unit] = self._get_unit(unit)
        grouping_values = []
        for unit in units:
            if not groupby in units_params[unit].keys():
                return nemoa.log('error', """could not get units:
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

        # test if system is initialized to network
        if not isinstance(self._params, dict) \
            or not 'units' in self._params:
            return []

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

    def _get_links(self, groupby = None, **kwargs):
        """Get links of system.

        Args:
            groupby (str or None): Name of a link attribute
                used to group links. If groupby is not
                None, the returned links are grouped by the different
                values of this attribute. Grouping is only
                possible if every link contains the attribute.
            **kwargs: filter attributs of links. If kwargs are given,
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
        if groupby == None: return links

        # group links by given attribute
        grouping_values = []
        for link in links:
            if not groupby in links_params[link].keys():
                return nemoa.log('error', """could not get links:
                    unknown link attribute '%s'.""" % (groupby))
            grouping_value = links_params[link][groupby]
            if not grouping_value in grouping_values:
                grouping_values.append(grouping_value)
        grouped_links = []
        for grouping_value in grouping_values:
            group = []
            for link in links:
                if links_params[link][groupby] == grouping_value:
                    group.append(link)
            grouped_links.append(group)
        return grouped_links

    def _get_copy(self, key = None, *args, **kwargs):
        """Get system copy as dictionary."""

        if key == None: return {
            'config': self._get_config(),
            'params': self._get_params(),
            'schedules': self._get_schedules() }

        if key == 'config': return self._get_config(*args, **kwargs)
        if key == 'params': return self._get_params(*args, **kwargs)
        if key == 'schedules':
            return self._get_schedules(*args, **kwargs)

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

    def _get_schedules(self, key = None, *args, **kwargs):
        """Get optimizeation schedules."""

        if key == None: return copy.deepcopy(self._schedules)

        if isinstance(key, str) and key in self._schedules.keys():
            if isinstance(self._schedules[key], dict):
                return self._schedules[key].copy()
            return self._schedules[key]

        return nemoa.log('error', """could not get optimization
            schedules: unknown key '%s'.""" % (key))

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

    def _set_copy(self, config = None, params = None, schedules = None):
        """Set configuration and parameters of system.

        Args:
            config (dict or None, optional): system configuration
            params (dict or None, optional): system parameters
            schedules (dict or None, optional): system optimization
                schedules

        Returns:
            Bool which is True if and only if no error occured.

        """

        retval = True

        if config: retval &= self._set_config(config)
        if params: retval &= self._set_params(params)
        if schedules: retval &= self._set_schedules(schedules)

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

    def _set_params(self, params = None, network = None, dataset = None):
        """Set system parameters from dictionary."""

        if not self._params:
            self._params = {'units': {}, 'links': {}}

        retval = True

        # get system parameters from dict
        if params:
            nemoa.common.dict_merge(copy.deepcopy(params), self._params)

            # create instances of units and links
            retval &= self._set_params_create_units()
            retval &= self._set_params_create_links()

        # get system parameters from network
        elif network:
            if not nemoa.type.is_network(network):
                return nemoa.log('error', """could not configure system:
                    network instance is not valid!""")

            # get unit layers and unit params
            layers = network.get('layers')
            units = [network.get('layer', layer) for layer in layers]

            for layer in units:
                layer['id'] = layer.pop('nodes')
                if 'type' in layer: layer['class'] = layer.pop('type')
                elif layer['visible']: layer['class'] = 'gauss'
                else: layer['class'] = 'sigmoid'

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
            for link in network.edges:
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

            # create instances of units and links
            retval &= self._set_params_create_units()
            retval &= self._set_params_create_links()

            retval &= self._set_params_init_links()


        # initialize system parameters if dataset is given
        if dataset:
            if not nemoa.type.is_dataset(dataset):
                return nemoa.log('error', """could not initialize
                    system: dataset instance is not valid.""")

            retval &= self._set_params_init_units(dataset)
            retval &= self._set_params_init_links(dataset)

        return retval

    def _set_params_create_units(self):

        # create instances of unit classes
        # and link units params to local params dict
        self._units = {}
        for layer_id in xrange(len(self._params['units'])):
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
                data = dataset.get('data', rows = rows, cols = cols)
            self._units[layer].initialize(data)

        return True

    def _set_params_init_links(self, dataset = None):
        """Initialize link parameteres (weights).

        If dataset is None, initialize weights matrices with zeros
        and all adjacency matrices with ones. if dataset is nemoa
        network instance, use data distribution to calculate random
        initial weights.

        Args:
            dataset (dataset instance OR None):

        Returns:


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

            if dataset == None:
                random = numpy.random.normal(numpy.zeros((x, y)), sigma)
            elif source in dataset.get('colgroups'):
                rows = self._config['params']['samples'] \
                    if 'samples' in self._config['params'] else '*'
                data = dataset.get('data', 100000, rows = rows,
                    cols = source)
                delta = sigma * data.std(axis = 0).reshape(x, 1) + 0.001
                random = numpy.random.normal(numpy.zeros((x, y)), delta)
            elif dataset.columns \
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

    def _set_schedules(self, schedules = None):
        """Set optimization schedules from dictionary."""

        # update optimization schedules dictionary
        if not isinstance(self._schedules, dict):
            self._schedules = {}
        if schedules:
            schedules_copy = copy.deepcopy(schedules)
            nemoa.common.dict_merge(schedules_copy, self._schedules)

        return True

    def save(self, *args, **kwargs):
        """Export system to file."""
        return nemoa.system.save(self, *args, **kwargs)

    def show(self, *args, **kwargs):
        """Show system as image."""
        return nemoa.system.show(self, *args, **kwargs)

    def copy(self, *args, **kwargs):
        """Create copy of system."""
        return nemoa.system.copy(self, *args, **kwargs)

    def optimize(self, dataset, schedule):
        """Optimize system parameters using data and given schedule."""

        # check if optimization schedule exists for current system
        # and merge default, existing and given schedule
        if not 'params' in schedule:
            config = self._default['optimize'].copy()
            nemoa.common.dict_merge(self._config['optimize'], config)
            self._config['optimize'] = config
        elif not self._get_type() in schedule['params']:
            return nemoa.log('error', """could not optimize model:
                optimization schedule '%s' does not include system '%s'
                """ % (schedule['name'], self._get_type()))
        else:
            config = self._default['optimize'].copy()
            nemoa.common.dict_merge(self._config['optimize'], config)
            nemoa.common.dict_merge(
                schedule['params'][self._get_type()], config)
            self._config['optimize'] = config

        # check dataset
        if (not 'check_dataset' in self._default['init']
            or self._default['init']['check_dataset'] == True) \
            and not self._check_dataset(dataset):
            return False

        # initialize tracker
        tracker = nemoa.system.commons.tracker.Tracker(self)
        tracker.set(data = self._get_test_data(dataset))

        # optimize system parameters
        return self._optimize(dataset, schedule, tracker)

    def evaluate(self, data, *args, **kwargs):

        # Default system evaluation
        if len(args) == 0:
            return self._get_eval_system(data, **kwargs)

        # Evaluate system units
        if args[0] == 'units':
            return self._get_eval_units(data, *args[1:], **kwargs)

        # Evaluate system links
        if args[0] == 'links':
            return self._get_eval_links(data, *args[1:], **kwargs)

        # Evaluate system relations
        if args[0] == 'relations':
            return self._get_eval_relation(data, *args[1:], **kwargs)

        # Evaluate system
        if args[0] in self._about_system().keys():
            return self._get_eval_system(data, *args, **kwargs)

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
