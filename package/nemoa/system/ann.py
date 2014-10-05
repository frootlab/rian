# -*- coding: utf-8 -*-
"""Artificial Neuronal Network (ANN).

Generic class of layered feed forward networks aimed to provide common
attributes, methods, optimization algorithms like back-propagation of
errors (1) and unit classes to other systems by inheritence. For
multilayer network topologies DBNs usually show better performance than
plain ANNs.

References:
    (1) "Learning representations by back-propagating errors",
        Rumelhart, D. E., Hinton, G. E., Williams, R. J. (1986)

"""

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import numpy

class ANN(nemoa.system.base.System):
    """Artificial Neuronal Network (ANN).

    Generic class of layered feed forward networks aimed to provide
    common attributes, methods, optimization algorithms like
    back-propagation of errors (1) and unit classes to other systems by
    inheritence. For multilayer network topologies DBNs usually show
    better performance than plain ANNs.

    References:
        (1) "Learning representations by back-propagating errors",
            Rumelhart, D. E., Hinton, G. E., and Williams, R. J. (1986)

    """

    _default = {
        'params': {
            'visible': 'auto',
            'hidden': 'auto',
            'visibleClass': 'gauss',
            'hiddenClass': 'sigmoid',
            'visibleSystem': None,
            'visibleSystemModule': 'rbm',
            'visibleSystemClass': 'grbm',
            'hiddenSystem': None,
            'hiddenSystemModule': 'rbm',
            'hiddenSystemClass': 'rbm' },
        'init': {
            'checkDataset': False,
            'ignoreUnits': [],
            'wSigma': 0.5 },
        'optimize': {
            'checkDataset': False,
            'ignoreUnits': [],
            'algorithm': 'bprop',
            'mod_corruption_enable': False,
            'minibatch_size': 100,
            'minibatch_update_interval': 10,
            'updates': 10000,
            'schedule': None,
            'visible': None,
            'hidden': None,
            'useAdjacency': False,
            'tracker_obj_function': 'error',
            'tracker_eval_time_interval': 10. ,
            'tracker_estimate_time': True,
            'tracker_estimate_timeWait': 15. }}

    def _configure(self, config = {},
        network = None, dataset = None, update = False):
        """Configure ANN to network and dataset.

        Args:
            config: dictionary containing system configuration
            network: nemoa network instance
            dataset: nemoa dataset instance

        """

        if not 'check' in self._config:
            self._config['check'] = {
                'config': False,
                'network': False,
                'dataset': False}
        self._set_config(config)

        if not network == None:
            self._configure_set_network(network, update)
        if not dataset == None:
            self._configure_set_dataset(dataset)

        return self._is_configured()

    def _configure_update_units_and_links(self, *args, **kwargs):

        nemoa.log('update system units and links')
        self._configure_set_units(
            self._params['units'], initialize = False)
        self._configure_set_links(
            self._params['links'], initialize = False)

        return True

    def _configure_set_network(self, network, update = False):
        """Update units and links to network instance."""

        nemoa.log("""get system units and links
            from network '%s'.""" % (network.get('name')))
        nemoa.log('set', indent = '+1')

        if not nemoa.type.is_network(network):
            nemoa.log('error', """could not configure system:
                network instance is not valid!""")
            nemoa.log('set', indent = '-1')
            return False

        initialize = (update == False)

        self._configure_set_units(
            self._get_units_from_network(network),
            initialize = initialize)

        self._configure_set_links(
            network.get('edges'),
            initialize = initialize)

        self._config['check']['network'] = True
        nemoa.log('set', indent = '-1')

        return True

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

    def _configure_test(self, params):
        """Check if system parameter dictionary is valid. """

        return self._configure_test_units(params) \
            and self._configure_test_links(params)

    def _init_units(self, dataset = None):
        """Initialize unit parameteres.

        Args:
            dataset: nemoa dataset instance OR None
        """

        if not (dataset == None) and not \
            nemoa.type.is_dataset(dataset): return nemoa.log(
            'error', """could not initilize unit parameters:
            invalid dataset argument given!""")

        for layer_name in self._units.keys():
            if dataset == None \
                or self._units[layer_name].params['visible'] == False:
                data = None
            else:
                rows = self._config['params']['samples'] \
                    if 'samples' in self._config['params'] else '*'
                cols = layer_name \
                    if layer_name in dataset.get('groups') else '*'
                data = dataset.data(100000, rows = rows, cols = cols)
            self._units[layer_name].initialize(data)

        return True

    def _configure_set_units(self, units = None, initialize = True):
        """Create instances for units."""

        if not 'units' in self._params: self._params['units'] = []
        if not hasattr(self, 'units'): self._units = {}

        if not isinstance(units, list): return False
        if len(units) < 2: return False
        self._params['units'] = units

        # get unit classes from system config
        visibleUnitsClass = self._config['params']['visibleClass']
        hiddenUnitsClass = self._config['params']['hiddenClass']
        for id in xrange(len(self._params['units'])):
            if self._params['units'][id]['visible'] == True:
                self._params['units'][id]['class'] = visibleUnitsClass
            else: self._params['units'][id]['class'] = hiddenUnitsClass

        # create instances of unit classes
        # and link units params to local params dict
        self._units = {}
        for id in xrange(len(self._params['units'])):
            unitClass = self._params['units'][id]['class']
            name = self._params['units'][id]['name']
            if unitClass == 'sigmoid': self._units[name] = self._SigmoidUnits()
            elif unitClass == 'gauss': self._units[name] = self._GaussUnits()
            else: return nemoa.log('error', """could not create system:
                unit class '%s' is not supported!""" % (unitClass))
            self._units[name].params = self._params['units'][id]

        if initialize: return self._init_units()
        return True

    def _configure_test_units(self, params):
        """Check if system parameter dictionary is valid respective to units. """

        if not isinstance(params, dict) \
            or not 'units' in params.keys() \
            or not isinstance(params['units'], list): return False
        for id in xrange(len(params['units'])):
            layer = params['units'][id]
            if not isinstance(layer, dict): return False
            for attr in ['name', 'visible', 'class', 'label']:
                if not attr in layer.keys(): return False
            if layer['class'] == 'gauss' \
                and not self._GaussUnits.check(layer): return False
            elif params['units'][id]['class'] == 'sigmoid' \
                and not self._SigmoidUnits.check(layer): return False

        return True

    def _get_units_from_network(self, network):
        """Return tuple with lists of unit labels from network."""

        units = []
        for layer in network.get('layers'):
            label = network.get('nodes', type = layer)
            params = network.get('node', label[0])['params']
            units.append({
                'name': layer,
                'label': network.get('nodes', type = layer),
                'visible': params['visible'],
                'id': params['layer_id']})

        return units

    def _remove_units(self, layer = None, label = []):
        """Remove units from parameter space. """

        if not layer == None and not layer in self._units.keys():
            return nemoa.log('error', """could not remove units:
                unknown layer '%'""" % (layer))

        # search for labeled units in given layer
        layer = self._units[layer].params
        select = []
        labels = []
        for id, unit in enumerate(layer['label']):
            if not unit in label:
                select.append(id)
                labels.append(unit)

        # remove units from unit labels
        layer['label'] = labels

        # delete units from unit parameter arrays
        if layer['class'] == 'gauss':
            self._GaussUnits.remove(layer, select)
        elif layer['class'] == 'sigmoid':
            self._SigmoidUnits.remove(layer, select)

        # delete units from link parameter arrays
        links = self._links[layer['name']]

        for src in links['source'].keys():
            links['source'][src]['A'] = \
                links['source'][src]['A'][:, select]
            links['source'][src]['W'] = \
                links['source'][src]['W'][:, select]
        for tgt in links['target'].keys():
            links['target'][tgt]['A'] = \
                links['target'][tgt]['A'][select, :]
            links['target'][tgt]['W'] = \
                links['target'][tgt]['W'][select, :]

        return True

    def _configure_set_links(self, links = None, initialize = True):
        """Create link configuration from units."""

        if not self._configure_test_units(self._params):
            return nemoa.log('error', """could not configure links:
                units have not been configured.""")

        if not 'links' in self._params: self._params['links'] = {}
        if not initialize: return self._configure_index_links()

        # initialize adjacency matrices with default values
        for lid in xrange(len(self._params['units']) - 1):
            src_name = self._params['units'][lid]['name']
            src_list = self._units[src_name].params['label']
            tgt_name = self._params['units'][lid + 1]['name']
            tgt_list = self._units[tgt_name].params['label']
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

        # set adjacency to one if links are given explicitly
        if links:
            layers = [layer['name'] for layer in self._params['units']]

            for link in links:
                src, tgt = link

                # get layer id and unit id of link source
                src_name = src.split(':')[0]
                src_unit = src[len(src_name) + 1:]
                if not src_name in layers: continue
                src_lid = layers.index(src_name)
                src_list = self._units[src_name].params['label']
                if not src in src_list: continue
                scr_uid = src_list.index(src)

                # get layer id and unit id of link target
                tgt_name = tgt.split(':')[0]
                tgt_unit = tgt[len(tgt_name) + 1:]
                if not tgt_name in layers: continue
                tgt_lid = layers.index(tgt_name)
                tgt_list = self._units[tgt_name].params['label']
                if not tgt in tgt_list: continue
                tgt_uid = tgt_list.index(tgt)

                # set link adjacency to 1
                if (src_lid, tgt_lid) in self._params['links']:
                    lnk_dict = self._params['links'][(src_lid, tgt_lid)]
                    lnk_dict['A'][scr_uid, tgt_uid] = 1.0
                elif (tgt_lid, src_lid) in self._params['links']:
                    lnk_dict = self._params['links'][(tgt_lid, src_lid)]
                    lnk_dict['A'][tgt_uid, scr_uid] = 1.0

        return self._configure_index_links() and self._init_links()

    def _init_links(self, dataset = None):
        """Initialize link parameteres (weights).

        If dataset is None, initialize weights matrices with zeros
        and all adjacency matrices with ones. if dataset is nemoa
        network instance, initialize weights with random values.

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
            x = len(self._units[source].params['label'])
            y = len(self._units[target].params['label'])
            alpha = self._config['init']['wSigma'] \
                if 'wSigma' in self._config['init'] else 1.
            sigma = numpy.ones([x, 1], dtype = float) * alpha / x

            if dataset == None: random = \
                numpy.random.normal(numpy.zeros((x, y)), sigma)
            elif source in dataset.get('groups'):
                rows = self._config['params']['samples'] \
                    if 'samples' in self._config['params'] else '*'
                data = dataset.data(100000, rows = rows, cols = source)
                random = numpy.random.normal(numpy.zeros((x, y)),
                    sigma * numpy.std(data, axis = 0).reshape(1, x).T)
            elif dataset.get('columns') \
                == self._units[source].params['label']:
                rows = self._config['params']['samples'] \
                    if 'samples' in self._config['params'] else '*'
                data = dataset.data(100000, rows = rows, cols = '*')
                random = numpy.random.normal(numpy.zeros((x, y)),
                    sigma * numpy.std(data, axis = 0).reshape(1, x).T)
            else: random = \
                numpy.random.normal(numpy.zeros((x, y)), sigma)

            self._params['links'][links]['W'] = A * random

        return True

    def _configure_test_links(self, params):
        """Check if system parameter dictionary is valid respective to links."""

        if not isinstance(params, dict) \
            or not 'links' in params.keys() \
            or not isinstance(params['links'], dict): return False
        for id in params['links'].keys():
            if not isinstance(params['links'][id], dict): return False
            for attr in ['A', 'W', 'source', 'target']:
                if not attr in params['links'][id].keys(): return False

        return True

    def _configure_index_links(self):

        self._links = {units: {'source': {}, 'target': {}}
            for units in self._units.keys()}
        for id in self._params['links'].keys():
            source = self._params['links'][id]['source']
            target = self._params['links'][id]['target']
            self._links[source]['target'][target] = \
                self._params['links'][id]
            self._units[source].target = \
                self._params['links'][id]
            self._links[target]['source'][source] = \
                self._params['links'][id]
            self._units[target].source = \
                self._params['links'][id]

        return True

    def _get_weights_from_layers(self, source, target):
        """Return ..."""

        if self._config['optimize']['useAdjacency']:
            if target['name'] in self._links[source['name']]['target']:
                return self._links[source['name']]['target'][target['name']]['W'] \
                    * self._links[source['name']]['target'][target['name']]['A']
            elif source['name'] in self._links[target['name']]['target']:
                return (self._links[target['name']]['target'][source['name']]['W'] \
                    * self._links[source['name']]['target'][target['name']]['A']).T
        else:
            if target['name'] in self._links[source['name']]['target']:
                return self._links[source['name']]['target'][target['name']]['W']
            elif source['name'] in self._links[target['name']]['target']:
                return self._links[target['name']]['target'][source['name']]['W'].T

        return nemoa.log('error', """Could not get links:
            Layer '%s' and layer '%s' are not connected.
            """ % (source['name'], target['name']))

    def _get_link(self, link):

        src_unit = link[0]
        src_layer = self._get_layer_of_unit(src_unit)
        if not src_layer in self._links:
            return None

        tgt_unit = link[1]
        tgt_layer = self._get_layer_of_unit(tgt_unit)
        if not tgt_layer in self._links[src_layer]['target']:
            return None

        # get weight and adjacency matrices of link layer
        link_layer = self._links[src_layer]['target'][tgt_layer]
        W = link_layer['W']
        A = link_layer['A']

        # get weight and adjacency of link
        src_id = self._units[src_layer].params['label'].index(src_unit)
        tgt_id = self._units[tgt_layer].params['label'].index(tgt_unit)
        link_weight = W[src_id, tgt_id]
        link_adjacency = A[src_id, tgt_id]

        # calculate normalized weight of link (normalized to link layer)
        if link_weight == 0.0:
            link_norm_weight = 0.0
        else:
            W_sum = numpy.sum(numpy.abs(A * W))
            A_sum = numpy.sum(A)
            # TODO: Problem with multilayer plain anns
            link_norm_weight = link_weight * A_sum / W_sum

        return {
            'adjacency': link_adjacency,
            'weight': link_weight,
            'normal': link_norm_weight}

    def _get_links(self):
        """Return links from adjacency matrix. """

        layers = self._get_layers()
        if not layers: return False

        links = ()
        for lid in xrange(len(layers) - 1):
            src = layers[lid]
            src_units = self._units[src].params['label']
            tgt = layers[lid + 1]
            tgt_units = self._units[tgt].params['label']

            lg = []
            for src_unit_id, src_unit in enumerate(src_units):
                for tgt_unit_id, tgt_unit in enumerate(tgt_units):
                    link_layer = self._params['links'][(lid, lid + 1)]

                    if not 'A' in link_layer \
                        or link_layer['A'][src_unit_id, tgt_unit_id]:
                        lg.append((src_unit, tgt_unit))

            links += (lg, )

        return links

    def _init_params(self, dataset = None):
        """Initialize system parameters.

        Initialize all unit and link parameters to dataset.

        Args:
            dataset: nemoa dataset instance

        """

        if not nemoa.type.is_dataset(dataset): return nemoa.log(
            'error', """could not initilize system:
            invalid dataset instance given-""")
        return self._init_units(dataset) and self._init_links(dataset)

    def _optimize_get_data(self, dataset, **kwargs):

        config = self._config['optimize']
        kwargs['size'] = config['minibatch_size']
        if config['mod_corruption_enable']: kwargs['corruption'] = \
            (config['mod_corruption_type'], config['mod_corruption_factor'])
        return dataset.data(**kwargs)

    def _optimize_get_values(self, data):
        """Forward pass (compute estimated values, from given input). """

        mapping = self.mapping()
        out = {}
        for lid, layer in enumerate(mapping):
            if lid == 0: out[layer] = data
            else: out[layer] = self._eval_units_expect(
                out[mapping[lid - 1]], mapping[lid - 1:lid + 1])

        return out

    def _optimize_get_deltas(self, outputData, out):
        """Return weight delta from backpropagation of error. """

        layers = self.mapping()
        delta = {}
        for id in range(len(layers) - 1)[::-1]:
            src = layers[id]
            tgt = layers[id + 1]
            if id == len(layers) - 2:
                delta[(src, tgt)] = out[tgt] - outputData
                continue
            inData = self._units[tgt].params['bias'] \
                + numpy.dot(out[src], self._params['links'][(id, id + 1)]['W'])
            grad = self._units[tgt].grad(inData)
            delta[(src, tgt)] = numpy.dot(delta[(tgt, layers[id + 2])],
                self._params['links'][(id + 1, id + 2)]['W'].T) * grad

        return delta

    def _optimize_update_params(self, updates):
        """Update parameters from dictionary."""

        layers = self.mapping()
        for id, layer in enumerate(layers[:-1]):
            src = layer
            tgt = layers[id + 1]
            self._params['links'][(id, id + 1)]['W'] += \
                updates['links'][(src, tgt)]['W']
            self._units[tgt].update(updates['units'][tgt])

        return True

    def _optimize_params(self, dataset, schedule, tracker):
        """Optimize system parameters."""

        nemoa.log('note', 'optimizing model')
        nemoa.log('set', indent = '+1')

        # Optimize system parameters
        algorithm = self._config['optimize']['algorithm'].lower()

        if algorithm == 'bprop':
            self._optimize_bprop(dataset, schedule, tracker)
        elif algorithm == 'rprop':
            self._optimize_rprop(dataset, schedule, tracker)
        else:
            nemoa.log('error', """could not optimize model:
                unknown algorithm '%s'!""" % (algorithm))

        nemoa.log('set', indent = '-1')
        return True

    def _optimize_bprop(self, dataset, schedule, tracker):
        """Optimize parameters using backpropagation of error."""

        cnf = self._config['optimize']
        mapping = self.mapping()

        # update parameters
        while tracker.update():

            # Get data (sample from minibatches)
            if tracker.get('epoch') % cnf['minibatch_update_interval'] == 0:
                data = self._optimize_get_data(dataset,
                    cols = (mapping[0], mapping[-1]))
            # Forward pass (Compute value estimations from given input)
            out = self._optimize_get_values(data[0])
            # Backward pass (Compute deltas from backpropagation of error)
            delta = self._optimize_get_deltas(data[1], out)
            # Compute parameter updates
            updates = self._optimize_bprop_get_updates(out, delta)
            # Update parameters
            self._optimize_update_params(updates)

        return True

    def _optimize_bprop_get_updates(self, out, delta, rate = 0.1):
        """Compute parameter update directions from weight deltas."""

        def getUpdate(grad, rate): return {
            key: rate * grad[key] for key in grad.keys()}

        layers = self.mapping()
        links = {}
        units = {}
        for id, src in enumerate(layers[:-1]):
            tgt = layers[id + 1]
            units[tgt] = getUpdate(
                self._units[tgt].get_updates_from_delta(
                delta[src, tgt]), rate)
            links[(src, tgt)] = getUpdate(
                self._LinkLayer.get_updates_from_delta(out[src],
                delta[src, tgt]), rate)

        return {'units': units, 'links': links}

    def _optimize_rprop(self, dataset, schedule, tracker):
        """Optimize parameters using resiliant backpropagation (RPROP).

        resiliant backpropagation ...

        """

        cnf = self._config['optimize']
        mapping = self.mapping()

        # update parameters
        while tracker.update():

            # Get data (sample from minibatches)
            if epoch % cnf['minibatch_update_interval'] == 0:
                data = self._optimize_get_data(dataset,
                    cols = (mapping[0], mapping[-1]))
            # Forward pass (Compute value estimations from given input)
            out = self._optimize_get_values(data[0])
            # Backward pass (Compute deltas from BPROP)
            delta = self._optimize_get_deltas(data[1], out)
            # Compute updates
            updates = self._optimize_rprop_get_updates(out, delta,
                tracker)
            # Update parameters
            self._optimize_update_params(updates)

        return True

    def _optimize_rprop_get_updates(self, out, delta, tracker):

        def getDict(dict, val): return {key: val * numpy.ones(
            shape = dict[key].shape) for key in dict.keys()}

        def getUpdate(prevGrad, prevUpdate, grad, accel, minFactor, maxFactor):
            update = {}
            for key in grad.keys():
                sign = numpy.sign(grad[key])
                a = numpy.sign(prevGrad[key]) * sign
                magnitude = numpy.maximum(numpy.minimum(prevUpdate[key] \
                    * (accel[0] * (a == -1) + accel[1] * (a == 0)
                    + accel[2] * (a == 1)), maxFactor), minFactor)
                update[key] = magnitude * sign
            return update

        # RProp parameters
        accel     = (0.5, 1., 1.2)
        initRate  = 0.001
        minFactor = 0.000001
        maxFactor = 50.

        layers = self.mapping()

        # Compute gradient from delta rule
        grad = {'units': {}, 'links': {}}
        for id, src in enumerate(layers[:-1]):
            tgt = layers[id + 1]
            grad['units'][tgt] = \
                self._units[tgt].get_updates_from_delta(delta[src, tgt])
            grad['links'][(src, tgt)] = \
                self._LinkLayer.get_updates_from_delta(out[src], delta[src, tgt])

        # Get previous gradients and updates
        prev = tracker.read('rprop')
        if not prev:
            prev = {
                'gradient': grad,
                'update': {'units': {}, 'links': {}}}
            for id, src in enumerate(layers[:-1]):
                tgt = layers[id + 1]
                prev['update']['units'][tgt] = \
                    getDict(grad['units'][tgt], initRate)
                prev['update']['links'][(src, tgt)] = \
                    getDict(grad['links'][(src, tgt)], initRate)
        prevGradient = prev['gradient']
        prevUpdate = prev['update']

        # Compute updates
        update = {'units': {}, 'links': {}}
        for id, src in enumerate(layers[:-1]):
            tgt = layers[id + 1]

            # calculate current rates for units
            update['units'][tgt] = getUpdate(
                prevGradient['units'][tgt],
                prevUpdate['units'][tgt],
                grad['units'][tgt],
                accel, minFactor, maxFactor)

            # calculate current rates for links
            update['links'][(src, tgt)] = getUpdate(
                prevGradient['links'][(src, tgt)],
                prevUpdate['links'][(src, tgt)],
                grad['links'][(src, tgt)],
                accel, minFactor, maxFactor)

        # Save updates to store
        tracker.write('rprop', gradient = grad, update = update)

        return update

    def _eval_system(self, data, func = 'accuracy', **kwargs):
        """Evaluation of system.

        Args:
            data: 2-tuple of numpy arrays: source data and target data
            func: string containing the name of a supported system
                evaluation function. For a full list of available
                functions use: model.about('system', 'eval')

        Returns:
            Scalar system evaluation value (respective to given data).
        """

        # get evaluation function
        methods = self._about_system()
        if not func in methods.keys(): return nemoa.log('error',
            "could not evaluate system: unknown method '%s'" % (func))
        method = methods[func]['method']
        if not hasattr(self, method): return nemoa.log('error',
            "could not evaluate units: unknown method '%s'" % (method))

        # prepare (non keyword) arguments for evaluation function
        evalArgs = []
        argsType = methods[func]['args']
        if   argsType == 'none':   pass
        elif argsType == 'input':  evalArgs.append(data[0])
        elif argsType == 'output': evalArgs.append(data[1])
        elif argsType == 'all':    evalArgs.append(data)

        # prepare keyword arguments for evaluation function
        eval_kwargs = kwargs.copy()
        if not 'mapping' in eval_kwargs.keys() \
            or eval_kwargs['mapping'] == None:
            eval_kwargs['mapping'] = self.mapping()

        # evaluate system
        return getattr(self, method)(*evalArgs, **eval_kwargs)
        #try: return getattr(self, method)(*evalArgs, **eval_kwargs)
        #except: return nemoa.log('error', 'could not evaluate system')

    @staticmethod
    def _about_system(): return {
        'energy': {
            'name': 'energy',
            'description': 'sum of local unit and link energies',
            'method': '_eval_system_energy',
            'args': 'all', 'format': '%.3f',
            'optimum': 'min'},
        'error': {
            'name': 'average reconstruction error',
            'description': 'mean error of reconstructed values',
            'method': '_eval_system_error',
            'args': 'all', 'format': '%.3f',
            'optimum': 'min'},
        'accuracy': {
            'name': 'average accuracy',
            'description': 'mean accuracy of reconstructed values',
            'method': '_eval_system_accuracy',
            'args': 'all', 'format': '%.3f',
            'optimum': 'max'},
        'precision': {
            'name': 'average precision',
            'description': 'mean precision of reconstructed values',
            'method': '_eval_system_precision',
            'args': 'all', 'format': '%.3f',
            'optimum': 'max'}
        }

    def _eval_system_error(self, *args, **kwargs):
        """Mean data reconstruction error of output units."""
        return numpy.mean(self._eval_units_error(*args, **kwargs))

    def _eval_system_accuracy(self, *args, **kwargs):
        """Mean data reconstruction accuracy of output units."""
        return numpy.mean(self._eval_units_accuracy(*args, **kwargs))

    def _eval_system_precision(self, *args, **kwargs):
        """Mean data reconstruction precision of output units."""
        return numpy.mean(self._eval_units_precision(*args, **kwargs))

    def _eval_system_energy(self, data, *args, **kwargs):
        """Sum of local link and unit energies."""

        mapping = list(self.mapping())
        energy = 0.

        # sum local unit energies
        for i in xrange(1, len(mapping) + 1):
            energy += numpy.sum(
                self._eval_units_energy(data[0],
                mapping = tuple(mapping[:i])))

        # sum local link energies
        for i in xrange(1, len(mapping)):
            energy += numpy.sum(
                self._eval_links_energy(data[0],
                mapping = tuple(mapping[:i+1])))

        return energy

    def _eval_units(self, data, func = 'accuracy', units = None, **kwargs):
        """Evaluation of target units.

        Args:
            data: 2-tuple with numpy arrays: source and target data
            func: string containing name of unit evaluation function
                For a full list of available system evaluation functions
                see: model.about('system', 'units')
            units: list of target unit names (within the same layer). If
                not given, all output units are selected.

        Returns:
            Dictionary with unit evaluation values for target units. The
            keys of the dictionary are given by the names of the target
            units, the values depend on the used evaluation function and
            are ether scalar (float) or vectorially (flat numpy array).

        """

        # check if data is valid
        if not isinstance(data, tuple): return nemoa.log('error',
            'could not evaluate units: invalid data format')

        # look for name of unit evaluation function in dictionary
        funcs = self._about_units()
        if not func in funcs.keys(): return nemoa.log('error',
            "could not evaluate units: unknown function '%s'" % (func))

        # get name of class method used for unit evaluation
        method = funcs[func]['method']
        if not hasattr(self, method): return nemoa.log('error',
            "could not evaluate units: unknown method '%s'" % (method))

        # prepare (non keyword) arguments for evaluation
        func_args = funcs[func]['args']
        if func_args == 'none': eArgs = []
        elif func_args == 'input': eArgs = [data[0]]
        elif func_args == 'output': eArgs = [data[1]]
        elif func_args == 'all': eArgs = [data]

        # prepare keyword arguments for evaluation
        e_kwargs = kwargs.copy()
        if isinstance(units, str):
            e_kwargs['mapping'] = self.mapping(tgt = units)
        elif not 'mapping' in e_kwargs.keys() \
            or e_kwargs['mapping'] == None:
            e_kwargs['mapping'] = self.mapping()

        # evaluate units
        try: values = getattr(self, method)(*eArgs, **e_kwargs)
        except: return nemoa.log('error', 'could not evaluate units')

        # create dictionary of target units
        labels = self._get_units(group = e_kwargs['mapping'][-1])
        ret_fmt = funcs[func]['return']
        if ret_fmt == 'vector': return {unit: values[:, uid] \
            for uid, unit in enumerate(labels)}
        elif ret_fmt == 'scalar': return {unit: values[uid] \
            for uid, unit in enumerate(labels)}
        return nemoa.log('error', 'could not evaluate units')

    @staticmethod
    def _about_units(): return {
        'energy': {
            'name': 'energy',
            'description': 'energy of units',
            'method': '_eval_units_energy',
            'show': 'diagram',
            'args': 'input', 'return': 'scalar', 'format': '%.3f'},
        'expect': {
            'name': 'expect',
            'description': 'reconstructed values',
            'method': '_eval_units_expect',
            'show': 'histogram',
            'args': 'input', 'return': 'vector', 'format': '%.3f'},
        'values': {
            'name': 'values',
            'description': 'reconstructed values',
            'method': '_eval_units_values',
            'show': 'histogram',
            'args': 'input', 'return': 'vector', 'format': '%.3f'},
        'samples': {
            'name': 'samples',
            'description': 'reconstructed samples',
            'method': '_eval_units_samples',
            'show': 'histogram',
            'args': 'input', 'return': 'vector', 'format': '%.3f'},
        'mean': {
            'name': 'mean values',
            'description': 'mean of reconstructed values',
            'method': '_eval_units_mean',
            'show': 'diagram',
            'args': 'input', 'return': 'scalar', 'format': '%.3f'},
        'variance': {
            'name': 'variance',
            'description': 'variance of reconstructed values',
            'method': '_eval_units_variance',
            'show': 'diagram',
            'args': 'input', 'return': 'scalar', 'format': '%.3f'},
        'residuals': {
            'name': 'residuals',
            'description': 'residuals of reconstructed values',
            'method': '_eval_units_residuals',
            'show': 'histogram',
            'args': 'all', 'return': 'vector', 'format': '%.3f'},
        'error': {
            'name': 'error',
            'description': 'mean error of reconstructed values',
            'method': '_eval_units_error',
            'show': 'diagram',
            'args': 'all', 'return': 'scalar', 'format': '%.3f'},
        'accuracy': {
            'name': 'accuracy',
            'description': 'accuracy of reconstructed values',
            'method': '_eval_units_accuracy',
            'show': 'diagram',
            'args': 'all', 'return': 'scalar', 'format': '%.3f'},
        'precision': {
            'name': 'precision',
            'description': 'precision of reconstructed values',
            'method': '_eval_units_precision',
            'show': 'diagram',
            'args': 'all', 'return': 'scalar', 'format': '%.3f'},
        'correlation': {
            'name': 'correlation',
            'description': 'correlation of reconstructed to real values',
            'method': '_eval_units_correlation',
            'show': 'diagram',
            'args': 'all', 'return': 'scalar', 'format': '%.3f'}
        }

    def _eval_units_expect(self, data, mapping = None, block = None):
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

        if mapping == None: mapping = self.mapping()
        if block == None: inData = data
        else:
            inData = numpy.copy(data)
            for i in block: inData[:,i] = numpy.mean(inData[:,i])
        if len(mapping) == 2: return self._units[mapping[1]].expect(
            inData, self._units[mapping[0]].params)
        outData = numpy.copy(inData)
        for id in xrange(len(mapping) - 1):
            outData = self._units[mapping[id + 1]].expect(
                outData, self._units[mapping[id]].params)

        return outData

    def _eval_units_values(self, data, mapping = None, block = None,
        expectLast = False):
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
            expectLast: return expectation values of the units
                for the last step instead of maximum likelihood values.

        Returns:
            Numpy array of shape (data, targets).
        """

        if mapping == None: mapping = self.mapping()
        if block == None: inData = data
        else:
            inData = numpy.copy(data)
            for i in block: inData[:,i] = numpy.mean(inData[:,i])
        if expectLast:
            if len(mapping) == 1:
                return inData
            elif len(mapping) == 2:
                return self._units[mapping[1]].expect(
                    self._units[mapping[0]].get_samples(inData),
                    self._units[mapping[0]].params)
            return self._units[mapping[-1]].expect(
                self._eval_units_values(data, mapping[0:-1]),
                self._units[mapping[-2]].params)
        else:
            if len(mapping) == 1:
                return self._units[mapping[0]].get_values(inData)
            elif len(mapping) == 2:
                return self._units[mapping[1]].get_values(
                    self._units[mapping[1]].expect(inData,
                    self._units[mapping[0]].params))
            data = numpy.copy(inData)
            for id in xrange(len(mapping) - 1):
                data = self._units[mapping[id + 1]].get_values(
                    self._units[mapping[id + 1]].expect(data,
                    self._units[mapping[id]].params))
            return data

    def _eval_units_samples(self, data, mapping = None, block = None,
        expectLast = False):
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
            expectLast: return expectation values of the units
                for the last step instead of sampled values

        Returns:
            Numpy array of shape (data, targets).
        """

        if mapping == None: mapping = self.mapping()
        if block == None: inData = data
        else:
            inData = numpy.copy(data)
            for i in block: inData[:,i] = numpy.mean(inData[:,i])
        if expectLast:
            if len(mapping) == 1:
                return data
            elif len(mapping) == 2:
                return self._units[mapping[1]].expect(
                    self._units[mapping[0]].get_samples(data),
                    self._units[mapping[0]].params)
            return self._units[mapping[-1]].expect(
                self._eval_units_samples(data, mapping[0:-1]),
                self._units[mapping[-2]].params)
        else:
            if len(mapping) == 1:
                return self._units[mapping[0]].get_samples(data)
            elif len(mapping) == 2:
                return self._units[mapping[1]].get_samples_from_input(
                    data, self._units[mapping[0]].params)
            data = numpy.copy(data)
            for id in xrange(len(mapping) - 1):
                data = self._units[mapping[id + 1]].get_samples_from_input(
                    data, self._units[mapping[id]].params)
            return data

    def _eval_units_residuals(self, data, mapping = None, block = None):
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

        dSrc, dTgt = data

        # set mapping: inLayer to outLayer (if not set)
        if mapping == None: mapping = self.mapping()

        # set unit values to mean (optional)
        if isinstance(block, list):
            dSrc = numpy.copy(dSrc)
            for i in block: dSrc[:, i] = numpy.mean(dSrc[:, i])

        # calculate estimated output values
        mOut = self._eval_units_expect(dSrc, mapping)

        # calculate residuals
        return dTgt - mOut

    def _eval_units_energy(self, data, mapping = None):
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

        # set mapping: inLayer to outLayer (if not set)
        if mapping == None: mapping = self.mapping()

        data = self._eval_units_expect(data, mapping)

        return self._units[mapping[-1]].energy(data)

    def _eval_units_mean(self, data, mapping = None, block = None):
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

        if mapping == None: mapping = self.mapping()
        if block == None:
            modelOut = self._eval_units_expect(data[0], mapping)
        else:
            dataInCopy = numpy.copy(data)
            for i in block: dataInCopy[:,i] = numpy.mean(dataInCopy[:,i])
            modelOut = self._eval_units_expect(dataInCopy, mapping)

        return modelOut.mean(axis = 0)

    def _eval_units_variance(self, data, mapping = None, block = None, **kwargs):
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

        if mapping == None: mapping = self.mapping()
        if block == None: modelOut = self._eval_units_expect(data, mapping)
        else:
            dataInCopy = numpy.copy(data)
            for i in block: dataInCopy[:,i] = numpy.mean(dataInCopy[:,i])
            modelOut = self._eval_units_expect(dataInCopy, mapping)

        return modelOut.var(axis = 0)

    def _eval_units_error(self, data, norm = 'ME', **kwargs):
        """Return reconstruction error of units (depending on norm)

        Args:
            data: 2-tuple of numpy arrays containing source and
                target data corresponding to the first and the last layer
                in the mapping
            mapping: n-tuple of strings containing the mapping
                from source unit layer (first argument of tuple)
                to target unit layer (last argument of tuple)
            block: list of strings containing labels of source units
                that are blocked by setting the values to their means
            norm: used norm to calculate data reconstuction error from
                residuals. see _get_data_mean for a list of provided norms
        """

        res = self._eval_units_residuals(data, **kwargs)
        error = self._get_data_mean(res, norm = norm)

        return error

    def _eval_units_accuracy(self, data, norm = 'MSE', **kwargs):
        """Return unit reconstruction accuracy.

        Args:
            data: 2-tuple of numpy arrays containing source and
                target data corresponding to the first and the last layer
                in the mapping
            mapping: n-tuple of strings containing the mapping
                from source unit layer (first argument of tuple)
                to target unit layer (last argument of tuple)
            block: list of strings containing labels of source units
                that are blocked by setting the values to their means
            norm -- used norm to calculate accuracy
                see getDataNorm for a list of provided norms

        Description:
            accuracy := 1 - norm(residuals) / norm(data).
        """

        res = self._eval_units_residuals(data, **kwargs)
        normres = self._get_data_mean(res, norm = norm)
        normdat = self._get_data_mean(data[1], norm = norm)

        return 1. - normres / normdat

    def _eval_units_precision(self, data, norm = 'SD', **kwargs):
        """Return unit reconstruction precision.

        Args:
            data: 2-tuple of numpy arrays containing source and
                target data corresponding to the first and the last layer
                in the mapping
            mapping: n-tuple of strings containing the mapping
                from source unit layer (first argument of tuple)
                to target unit layer (last argument of tuple)
            block: list of strings containing labels of source units
                that are blocked by setting the values to their means
            norm: used norm to calculate precision
                see _get_data_deviation for a list of provided norms

        Description:
            precision := 1 - dev(residuals) / dev(data).
        """

        res = self._eval_units_residuals(data, **kwargs)
        devres = self._get_data_deviation(res, norm = norm)
        devdat = self._get_data_deviation(data[1], norm = norm)

        return 1. - devres / devdat

    def _eval_units_correlation(self, data, mapping = None, block = None, **kwargs):
        """Correlation reconstructed unit values.

        Args:
            data: 2-tuple of numpy arrays containing source and
                target data corresponding to the first and the last layer
                in the mapping
            mapping: n-tuple of strings containing the mapping
                from source unit layer (first argument of tuple)
                to target unit layer (last argument of tuple)
            block: list of string containing labels of units in the
                input layer that are blocked by setting the values to
                their means

        Returns:
            Numpy array with reconstructed correlation of units.
        """

        if mapping == None: mapping = self.mapping()
        if block == None: modelOut = self._eval_units_expect(data, mapping)
        else:
            dataInCopy = numpy.copy(data)
            for i in block: dataInCopy[:,i] = numpy.mean(dataInCopy[:,i])
            modelOut = self._eval_units_expect(dataInCopy, mapping)

        M = numpy.corrcoef(numpy.hstack(data).T)

        return True

    def _eval_links(self, data, func = 'energy', **kwargs):
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
                see: system.about('links')
        """

        # get link evaluation function
        methods = self._about_links()
        if not func in methods.keys(): return nemoa.log('error',
            "could not evaluate links: unknown method '%s'" % (func))
        method = methods[func]['method']
        if not hasattr(self, method): return nemoa.log('error',
            "could not evaluate links: unknown method '%s'" % (method))

        # prepare arguments for evaluation functions
        evalArgs = []
        argsType = methods[func]['args']
        if   argsType == 'none':   pass
        elif argsType == 'input':  evalArgs.append(data[0])
        elif argsType == 'output': evalArgs.append(data[1])
        elif argsType == 'all':    evalArgs.append(data)

        # prepare keyword arguments for evaluation functions
        eval_kwargs = kwargs.copy()
        if not 'mapping' in eval_kwargs.keys() \
            or eval_kwargs['mapping'] == None:
            eval_kwargs['mapping'] = self.mapping()

        # evaluate
        values = getattr(self, method)(*evalArgs, **eval_kwargs)

        # create link dictionary
        in_labels = self._get_units(group = eval_kwargs['mapping'][-2])
        out_labels = self._get_units(group = eval_kwargs['mapping'][-1])
        out_fmt = methods[func]['return']
        if out_fmt == 'scalar':
            rel_dict = {}
            for in_id, in_unit in enumerate(in_labels):
                for out_id, out_unit in enumerate(out_labels):
                    rel_dict[(in_unit, out_unit)] = \
                        values[in_id, out_id]
            return rel_dict
        return nemoa.log('warning', 'could not perform evaluation')

    @staticmethod
    def _about_links(): return {
        'energy': {
            'name': 'energy',
            'description': 'local energy of links',
            'method': '_eval_links_energy',
            'show': 'graph',
            'args': 'input', 'return': 'vector', 'format': '%.3f'}
        }

    def _eval_links_energy(self, data, mapping = None, **kwargs):
        """Return link energies of a layer.

        Args:
            mapping: tuple of strings containing the mapping
                from source unit layer (first argument of tuple)
                to target unit layer (last argument of tuple)
        """

        if len(mapping) == 1:
            return nemoa.log('error', 'bad implementation of ann._eval_links_energy')
        elif len(mapping) == 2:
            dSrc  = data
            dTgt = self._eval_units_values(dSrc, mapping)
        else:
            dSrc  = self._eval_units_expect(data, mapping[0:-1])
            dTgt = self._eval_units_values(dSrc, mapping[-2:])

        sID = self.mapping().index(mapping[-2])
        tID = self.mapping().index(mapping[-1])
        src = self._units[mapping[-2]].params
        tgt = self._units[mapping[-1]].params

        if (sID, tID) in self._params['links']:
            links = self._params['links'][(sID, tID)]
            return self._LinkLayer.energy(dSrc, dTgt, src, tgt, links)
        elif (tID, sID) in self._params['links']:
            links = self._params['links'][(tID, sID)]
            return self._LinkLayer.energy(dTgt, dSrc, tgt, src, links)

    def _eval_relation(self, data, func = 'correlation',
        relations = None, evalStat = True, **kwargs):
        """Evaluate relations between source and target units.

        Args:
            data: 2-tuple with numpy arrays: input data and output data
            func: string containing name of unit relation function
                For a full list of available unit relation functions
                see: system.about('relations')
            transform: optional formula for transformation of relation
                which is executed by python eval() function. The usable
                variables are:
                    M: for the relation matrix as numpy array with shape
                        (source, target)
                    C: for the standard correlation matrix s numpy array
                        with shape (source, target)
                Example: 'M**2 - C'
            format: string describing format of return values
                'array': return values as numpy array
                'dict': return values as python dictionary
            evalStat: if format is 'dict' and evalStat is True then the
                return dictionary includes additional statistical
                values:
                    min: minimum value of unit relation
                    max: maximum value of unit relation
                    mean: mean value of unit relation
                    std: standard deviation of unit relation

        Returns:
            Python dictionary or numpy array with unit relation values.
        """

        # get evaluation function
        methods = self._about_relations()
        if not func in methods.keys(): return nemoa.log('error',
            "could not evaluate relations: unknown method '%s'" % (func))
        method = methods[func]['method']
        if not hasattr(self, method): return nemoa.log('error',
            "could not evaluate relations: unknown method '%s'" % (method))

        # prepare arguments for evaluation function
        evalArgs = []
        argsType = methods[func]['args']
        if   argsType == 'none':   pass
        elif argsType == 'input':  evalArgs.append(data[0])
        elif argsType == 'output': evalArgs.append(data[1])
        elif argsType == 'all':    evalArgs.append(data)

        # extract keyword arguments:
        # 'transform', 'format' and 'evalStat'
        if 'transform' in kwargs.keys():
            transform = kwargs['transform']
            del kwargs['transform']
        else: transform = ''
        if not isinstance(transform, str): transform = ''
        if 'format' in kwargs.keys():
            ret_fmt = kwargs['format']
            del kwargs['format']
        else: ret_fmt = 'dict'
        if not isinstance(ret_fmt, str): ret_fmt = 'dict'

        # prepare keyword arguments for evaluation function
        eval_kwargs = kwargs.copy()
        if not 'mapping' in eval_kwargs.keys() \
            or eval_kwargs['mapping'] == None:
            eval_kwargs['mapping'] = self.mapping()

        # evaluate relations and get information about relation values
        values = getattr(self, method)(*evalArgs, **eval_kwargs)
        valuesFmt = methods[func]['return']

        # create formated return values as matrix or dict
        # (for scalar relation evaluations)
        if valuesFmt == 'scalar':
            # (optional) transform relation using 'transform' string
            if transform:
                M = values
                if 'C' in transform:
                    C = self._eval_relation_correlation(data)
                try:
                    T = eval(transform)
                    values = T
                except: return nemoa.log('error',
                    'could not transform relations: invalid syntax!')

            # create formated return values
            if ret_fmt == 'array': ret_val = values
            elif ret_fmt == 'dict':
                in_units = self._get_units(
                    group = eval_kwargs['mapping'][0])
                out_units = self._get_units(
                    group = eval_kwargs['mapping'][-1])
                ret_val = nemoa.common.dict_from_array(
                    values, (in_units, out_units))

                # optionally evaluate statistical values over all relations
                if evalStat:
                    A = numpy.array([ret_val[key] for key in ret_val.keys()
                        if not key[0].split(':')[1] == key[1].split(':')[1]])
                    ret_val['max'] = numpy.amax(A)
                    ret_val['min'] = numpy.amin(A)
                    ret_val['mean'] = numpy.mean(A)
                    ret_val['std'] = numpy.std(A)
                    # force symmetric distribution with mean at 0
                    # by adding additive inverse values
                    B = numpy.concatenate((A, -A))
                    ret_val['cstd'] = numpy.std(B) - numpy.mean(A)
            else: return nemoa.log('warning',
                'could not perform evaluation')

            return ret_val

    @staticmethod
    def _about_relations(): return {
        'correlation': {
            'name': 'correlation',
            'description': """
                undirected data based relation describing
                the 'linearity' between variables (units) """,
            'directed': False, 'signed': True, 'normal': True,
            'method': '_eval_relation_correlation', 'show': 'heatmap',
            'args': 'all', 'return': 'scalar', 'format': '%.3f'},
        'capacity': {
            'name': 'network capacity',
            'description': """
                directed graph based relation describing
                the 'network capacity' between units (variables). """,
            'directed': True, 'signed': True, 'normal': False,
            'method': '_eval_relation_capacity', 'show': 'heatmap',
            'args': 'all', 'return': 'scalar', 'format': '%.3f'},
        'knockout': {
            'name': 'knockout effect',
            'description': """
                directed data manipulation based relation describing
                the increase of the data reconstruction error of a given
                output unit, when setting the values of a given input
                unit to its mean value. """,
            'directed': True, 'signed': True, 'normal': False,
            'method': '_eval_relation_knockout', 'show': 'heatmap',
            'args': 'all', 'return': 'scalar', 'format': '%.3f'},
        'induction': {
            'name': 'induced deviation',
            'description': """
                directed data manipulation based relation describing
                the induced deviation of reconstructed values of a given
                output unit, when manipulating the values of a given
                input unit. """,
            'directed': True, 'signed': True, 'normal': True,
            'method': '_eval_relation_induction', 'show': 'heatmap',
            'args': 'all', 'return': 'scalar', 'format': '%.3f'},
        }

    def _eval_relation_correlation(self, data, mapping = None, **kwargs):
        """Data correlation between source and target units.

        Args:
            data: 2-tuple with numpy arrays: input data and output data
            mapping: tuple of strings containing the mapping
                from input layer (first argument of tuple)
                to output layer (last argument of tuple)

        Returns:
            Numpy array of shape (source, target) containing pairwise
            correlation between source and target units.

        """

        if not mapping: mapping = self.mapping()
        in_labels = self._get_units(group = mapping[0])
        out_labels = self._get_units(group = mapping[-1])

        # calculate symmetric correlation matrix
        M = numpy.corrcoef(numpy.hstack(data).T)
        u_list = in_labels + out_labels

        # create asymmetric output matrix
        R = numpy.zeros(shape = (len(in_labels), len(out_labels)))
        for i, u1 in enumerate(in_labels):
            k = u_list.index(u1)
            for j, u2 in enumerate(out_labels):
                l = u_list.index(u2)
                R[i, j] = M[k, l]

        return R

    def _eval_relation_capacity(self, data, mapping = None, **kwargs):
        """Network Capacity from source to target units.

        Args:
            data: 2-tuple with numpy arrays: input data and output data
            mapping: tuple of strings containing the mapping
                from input layer (first argument of tuple)
                to output layer (last argument of tuple)

        Returns:
            Numpy array of shape (source, target) containing pairwise
            network capacity from source to target units.

        """

        if mapping == None: mapping = self.mapping()

        # calculate product of weight matrices
        for i in range(1, len(mapping))[::-1]:
            W = self._units[mapping[i-1]].links({'name': mapping[i]})['W']
            if i == len(mapping) - 1: R = W.copy()
            else: R = numpy.dot(R.copy(), W)

        return R.T

    def _eval_relation_knockout(self, data, mapping = None, **kwargs):
        """Knockout effect from source to target units.

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

        if not mapping: mapping = self.mapping()
        in_labels = self._get_units(group = mapping[0])
        out_labels = self._get_units(group = mapping[-1])

        # prepare knockout matrix
        R = numpy.zeros((len(in_labels), len(out_labels)))

        # calculate unit values without knockout
        if not 'measure' in kwargs: measure = 'error'
        else: measure = kwargs['measure']
        method_name = self.about('units', measure, 'name')
        default = self._eval_units(data,
            func = measure, mapping = mapping)

        # calculate unit values with knockout
        for in_id, in_unit in enumerate(in_labels):

            # modify unit and calculate unit values
            knockout = self._eval_units(data, func = measure,
                mapping = mapping, block = [in_id])

            # store difference in knockout matrix
            for out_id, out_unit in enumerate(out_labels):
                R[in_id, out_id] = \
                    knockout[out_unit] - default[out_unit]

        return R

    def _eval_relation_induction(self, data, mapping = None,
        points = 10, amplify = 2., gauge = 0.05, **kwargs):
        """Induced deviation from source to target units.

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

        Returns:
            Numpy array of shape (source, target) containing pairwise
            induced deviation from source to target units.
        """

        if not mapping: mapping = self.mapping()
        input_units = self._get_units(group = mapping[0])
        output_units = self._get_units(group = mapping[-1])
        R = numpy.zeros((len(input_units), len(output_units)))

        # get indices of representatives
        rIds = [int((i + 0.5) * int(float(data[0].shape[0])
            / points)) for i in xrange(points)]

        for iId, iUnit in enumerate(input_units):
            iCurve = numpy.take(numpy.sort(data[0][:, iId]), rIds)
            iCurve = amplify * iCurve

            # create output matrix for each output
            C = {oUnit: numpy.zeros((data[0].shape[0], points)) \
                for oUnit in output_units}
            for pId in xrange(points):
                iData  = data[0].copy()
                iData[:, iId] = iCurve[pId]
                oExpect = self._eval_units((iData, data[1]),
                    func = 'expect', mapping = mapping)
                for oUnit in output_units: C[oUnit][:, pId] = oExpect[oUnit]

            # calculate mean of standard deviations of outputs
            for oId, oUnit in enumerate(output_units):

                # calculate sign by correlating input and output
                corr = numpy.zeros(data[0].shape[0])
                for i in xrange(data[0].shape[0]):
                    corr[i] = numpy.correlate(C[oUnit][i, :], iCurve)
                sign = numpy.sign(corr.mean())

                # calculate norm by mean over maximum 5% of data
                bound = int((1. - gauge) * data[0].shape[0])
                subset = numpy.sort(C[oUnit].std(axis = 1))[bound:]
                norm = subset.mean() / data[1][:, oId].std()

                # calculate influence
                R[iId, oId] = sign * norm

        return R

    def mapping(self, src = None, tgt = None):
        """Mapping of units from source to target.

        Args:
            src: name of source unit layer
            tgt: name of target unit layer

        Returns:
            tuple with names of unit layers from source to target.

        """

        mapping = tuple([g['name'] for g in self._params['units']])
        sid = mapping.index(src) \
            if isinstance(src, str) and src in mapping else 0
        tid = mapping.index(tgt) \
            if isinstance(tgt, str) and tgt in mapping else len(mapping)

        return mapping[sid:tid + 1] if sid <= tid \
            else mapping[tid:sid + 1][::-1]

    def _get_test_data(self, dataset):
        """Return tuple with default test data."""

        return dataset.data(
            cols = (self.mapping()[0], self.mapping()[-1]))

    # TODO: create classes for links
    class _LinkLayer():
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

    class _UnitLayerBaseClass():
        """Base Class for Unit Layer.

        Unification of common unit layer functions and attributes.
        """

        params = {}
        source = {}
        target = {}

        def __init__(self): pass

        def expect(self, data, source):

            if source['class'] == 'sigmoid': return \
                self.expect_from_sigmoid_layer(data, source, self.weights(source))
            elif source['class'] == 'gauss': return \
                self.expect_from_gauss_layer(data, source, self.weights(source))

            return False

        def get_updates(self, data, model, source):

            return self.get_param_updates(data, model, self.weights(source))

        def get_delta(self, inData, outDelta, source, target):

            return self.deltaFromBPROP(inData, outDelta,
                self.weights(source), self.weights(target))

        def get_samples_from_input(self, data, source):

            if source['class'] == 'sigmoid': return self.get_samples(
                self.expect_from_sigmoid_layer(data, source, self.weights(source)))
            elif source['class'] == 'gauss': return self.get_samples(
                self.expect_from_gauss_layer(data, source, self.weights(source)))

            return False

        def weights(self, source):

            if 'source' in self.source and source['name'] == self.source['source']:
                return self.source['W']
            elif 'target' in self.target and source['name'] == self.target['target']:
                return self.target['W'].T
            else: return nemoa.log('error', """Could not get links:
                Layers '%s' and '%s' are not connected!
                """ % (source['name'], self.params['name']))

        def links(self, source):

            if 'source' in self.source and source['name'] == self.source['source']:
                return self.source
            elif 'target' in self.target and source['name'] == self.target['target']:
                return {'W': self.target['W'].T, 'A': self.target['A'].T}
            else: return nemoa.log('error', """Could not get links:
                Layers '%s' and '%s' are not connected!
                """ % (source['name'], self.params['name']))

        def adjacency(self, source):

            if 'source' in self.source and source['name'] == self.source['source']:
                return self.source['A']
            elif 'target' in self.target and source['name'] == self.target['target']:
                return self.target['A'].T
            else: return nemoa.log('error', """Could not get links:
                Layers '%s' and '%s' are not connected!
                """ % (source['name'], self.params['name']))

    class _SigmoidUnits(_UnitLayerBaseClass):
        """Sigmoidal Unit Layer.

        Layer of units with sigmoidal activation function and bernoulli
        distributed sampling.

        """

        def initialize(self, data = None):
            """Initialize system parameters of sigmoid distributed units
            using data. """

            size = len(self.params['label'])
            shape = (1, size)
            self.params['bias'] = 0.5 * numpy.ones(shape)
            return True

        def update(self, updates):
            """Update parameter of sigmoid units. """

            if 'bias'in updates:
                self.params['bias'] += updates['bias']

            return True

        def _overwrite(self, params):
            """Merge parameters of sigmoid units."""

            for i, u in enumerate(params['label']):
                if u in self.params['label']:
                    l = self.params['label'].index(u)
                    self.params['bias'][0, l] = params['bias'][0, i]

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

            size = len(self.params['label'])

            return {'bias': numpy.mean(data[1] - model[1], axis = 0).reshape((1, size))}

        def get_updates_from_delta(self, delta):

            size = len(self.params['label'])

            return {'bias': - numpy.mean(delta, axis = 0).reshape((1, size))}

        def deltaFromBPROP(self, data_in, delta_out, W_in, W_out):

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

            id = self.params['label'].index(unit)
            cl = self.params['class']
            visible = self.params['visible']
            bias = self.params['bias'][0, id]

            return {'label': unit, 'id': id, 'class': cl,
                'visible': visible, 'bias': bias}

    class _GaussUnits(_UnitLayerBaseClass):
        """Layer of Gaussian Units.

        Artificial neural network units with linear activation function
        and gaussian sampling.

        """

        def initialize(self, data = None, vSigma = 0.4):
            """Initialize parameters of gauss distributed units. """

            size = len(self.params['label'])
            if data == None:
                self.params['bias'] = numpy.zeros([1, size])
                self.params['lvar'] = numpy.zeros([1, size])
            else:
                self.params['bias'] = \
                    numpy.mean(data, axis = 0).reshape(1, size)
                self.params['lvar'] = \
                    numpy.log((vSigma * numpy.ones((1, size))) ** 2)

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

            shape = (1, len(self.params['label']))
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

            shape = (1, len(self.params['label']))
            bias = - numpy.mean(delta, axis = 0).reshape(shape)

            return { 'bias': bias }

        def _overwrite(self, params):
            """Merge parameters of gaussian units. """

            for i, u in enumerate(params['label']):
                if u in self.params['label']:
                    l = self.params['label'].index(u)
                    self.params['bias'][0, l] = params['bias'][0, i]
                    self.params['lvar'][0, l] = params['lvar'][0, i]

            return True

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

            id = self.params['label'].index(unit)

            cl = self.params['class']
            bias = self.params['bias'][0, id]
            lvar = self.params['lvar'][0, id]
            visible = self.params['visible']

            return {
                'label': unit, 'id': id, 'class': cl,
                'visible': visible, 'bias': bias, 'lvar': lvar }
