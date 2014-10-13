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

    def __init__(self, *args, **kwargs):
        """Configure system and system parameters."""

        # set configuration and update units and links
        self._set_config(kwargs['config'] if 'config' in kwargs else {})

    def configure(self, network = None, dataset = None, *args, **kwargs):
        """Configure system to network and dataset."""
        if not hasattr(self.__class__, '_configure') \
            or not callable(getattr(self.__class__, '_configure')):
            return True
        nemoa.log("configure system '%s'" % (self._config['name']))
        nemoa.log('set', indent = '+1')
        if not self._check_network(network):
            nemoa.log('error', """system could not be configured:
                network is not valid!""")
            nemoa.log('set', indent = '-1')
            return False
        ret_val = self._configure(dataset = dataset, network = network,
            *args, **kwargs)
        nemoa.log('set', indent = '-1')
        return ret_val

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
        """Get system system configuration and parameters."""

        # get generic information about system
        if key == 'name': return self._get_name()
        if key == 'type': return self._get_type()
        if key == 'about': return self._get_about()

        # get information about system parameters
        if key == 'unit': return self._get_unit(*args, **kwargs)
        if key == 'units': return self._get_units(*args, **kwargs)
        if key == 'link': return self._get_link(*args, **kwargs)
        if key == 'links': return self._get_links(*args, **kwargs)
        if key == 'layer': return self._get_layer(*args, **kwargs)
        if key == 'layers': return self._get_layers(*args, **kwargs)

        # get copy of system configuration and parameters
        if key == 'copy': return self._get_copy(*args, **kwargs)

        return nemoa.log('warning', "unknown key '%s'" % (key))

    def _get_name(self):
        """Get name of system."""
        return self._config['name'] if 'name' in self._config else None

    def _get_about(self):
        """Get docstring of system."""
        return self.__doc__

    def _get_type(self):
        """Get type of system, using module and class name."""
        module_name = self.__module__.split('.')[-1]
        class_name = self.__class__.__name__
        return module_name + '.' + class_name

    def _get_copy(self, section = None):
        """Get system copy as dictionary."""
        if section == None: return {
            'config': copy.deepcopy(self._config),
            'params': copy.deepcopy(self._params) }
        elif section == 'config':
            return copy.deepcopy(self._config)
        elif section == 'params':
            return copy.deepcopy(self._params)
        return nemoa.log('error', """could not get copy of
            configuration: unknown section '%s'.""" % (section))

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
            # TODO: flatten() maybe not needed
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

        src_unit = self._get_unit(src)
        src_id = src_unit['layer_sub_id']
        src_layer = src_unit['layer']
        src_layer_params = self._units[src_layer].params

        tgt_unit = self._get_unit(tgt)
        tgt_id = tgt_unit['layer_sub_id']
        tgt_layer = tgt_unit['layer']
        tgt_layer_params = self._units[tgt_layer].params

        link_layer_params = self._links[src_layer]['target'][tgt_layer]
        link_layer_size = len(src_layer_params['id']) \
            * len(tgt_layer_params['id'])

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
            src_units = self._units[src_layer].params['id']
            tgt_layer = layers[layer_id + 1]
            tgt_units = self._units[tgt_layer].params['id']
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

    def set(self, key = None, *args, **kwargs):
        """Set system configuration and parameters."""

        # get generic information about system
        if key == 'name': return self._set_name(*args, **kwargs)

        # get copy of system configuration and parameters
        if key == 'copy': return self._set_copy(*args, **kwargs)

        return nemoa.log('warning', "unknown key '%s'" % (key))

    def _set_name(self, name):
        """Set name of system."""
        if not isinstance(name, str): return False
        self._config['name'] = name
        return True

    def _set_copy(self, **kwargs):
        """Set system settings from dictionary."""
        if 'config' in kwargs:
            self._set_config(kwargs['config'])
        if 'params' in kwargs:
            self._set_params(copy.deepcopy(kwargs['params']))
        return self._configure_update_units_and_links()

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

    def _set_params(self, params = None):
        """Set system parameters from dictionary."""

        # create parameter dictionary if needed
        if not hasattr(self, '_params'):
            self._params = {'units': {}, 'links': {}}

        # merge parameters
        if params:
            nemoa.common.dict_merge(params, self._params)

        return True

    def _initialize(self, dataset = None):
        """Initialize system parameters.

        Initialize all system parameters to dataset.

        Args:
            dataset: nemoa dataset instance

        """

        if not nemoa.type.is_dataset(dataset):
            return nemoa.log('error', """could not initilize system
                parameters: invalid dataset instance given!""")
        return self._init_params(dataset)

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
        tracker = nemoa.system.base.Tracker(self)
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
