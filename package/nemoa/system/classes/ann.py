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
            'w_sigma': 0.5 },
        'optimize': {
            'check_dataset': False,
            'ignore_units': [],
            'algorithm': 'bprop',
            'add_noise_enable': False,
            'minibatch_size': 100,
            'minibatch_update_interval': 10,
            'updates': 10000,
            'schedule': None,
            'visible': None,
            'hidden': None,
            'adjacency_enable': False,
            'tracker_obj_function': 'error',
            'tracker_eval_time_interval': 10. ,
            'tracker_estimate_time': True,
            'tracker_estimate_time_wait': 15. }}

    def _configure_test(self, params):
        """Check if system parameter dictionary is valid. """

        return self._configure_test_units(params) \
            and self._configure_test_links(params)

    def _configure_test_units(self, params):
        """Check if system unit parameter dictionary is valid. """

        if not isinstance(params, dict) \
            or not 'units' in params.keys() \
            or not isinstance(params['units'], list): return False

        for layer_id in xrange(len(params['units'])):

            # test parameter dictionary
            layer = params['units'][layer_id]

            if not isinstance(layer, dict): return False
            for key in ['id', 'layer', 'layer_id', 'visible', 'class']:
                if not key in layer.keys(): return False

            # test unit class
            if layer['class'] == 'gauss' \
                and not self.UnitsGauss.check(layer): return False
            elif layer['class'] == 'sigmoid' \
                and not self.UnitsSigmoid.check(layer): return False

        return True

    def _remove_units(self, layer = None, label = []):
        """Remove units from parameter space. """

        if not layer == None and not layer in self._units.keys():
            return nemoa.log('error', """could not remove units:
                unknown layer '%s'""" % (layer))

        # search for labeled units in given layer
        layer = self._units[layer].params
        select = []
        labels = []
        for id, unit in enumerate(layer['id']):
            if not unit in label:
                select.append(id)
                labels.append(unit)

        # remove units from unit labels
        layer['id'] = labels

        # delete units from unit parameter arrays
        if layer['class'] == 'gauss':
            self.UnitsGauss.remove(layer, select)
        elif layer['class'] == 'sigmoid':
            self.UnitsSigmoid.remove(layer, select)

        # delete units from link parameter arrays
        links = self._links[layer['layer']]

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

    def _configure_test_links(self, params):
        """Check if system link parameter dictionary is valid."""

        if not isinstance(params, dict) \
            or not 'links' in params.keys() \
            or not isinstance(params['links'], dict): return False
        for id in params['links'].keys():
            if not isinstance(params['links'][id], dict): return False
            for attr in ['A', 'W', 'source', 'target']:
                if not attr in params['links'][id].keys(): return False

        return True

    def _get_weights_from_layers(self, source, target):
        """Return ..."""

        srcname = source['name']
        tgtname = target['name']

        if self._config['optimize']['adjacency_enable']:
            if tgtname in self._links[srcname]['target']:
                return self._links[srcname]['target'][tgtname]['W'] \
                    * self._links[srcname]['target'][tgtname]['A']
            elif srcname in self._links[tgtname]['target']:
                return (self._links[tgtname]['target'][srcname]['W'] \
                    * self._links[srcname]['target'][tgtname]['A']).T
        else:
            if tgtname in self._links[srcname]['target']:
                return self._links[srcname]['target'][tgtname]['W']
            elif srcname in self._links[tgtname]['target']:
                return self._links[tgtname]['target'][srcname]['W'].T

        return nemoa.log('error', """Could not get links:
            Layer '%s' and layer '%s' are not connected.
            """ % (srcname, tgtname))

    def _optimize_get_data(self, dataset, **kwargs):

        config = self._config['optimize']
        kwargs['size'] = config['minibatch_size']
        if config['add_noise_enable']:
            kwargs['noise'] = (config['add_noise_type'],
                config['add_noise_factor'])
        return dataset.get('data', **kwargs)

    def _optimize_get_values(self, data):
        """Forward pass (compute estimated values, from given input). """

        mapping = self.mapping()
        out = {}
        for lid, layer in enumerate(mapping):
            if lid == 0: out[layer] = data
            else: out[layer] = self._get_eval_units_expect(
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
            in_data = self._units[tgt].params['bias'] \
                + numpy.dot(out[src],
                self._params['links'][(id, id + 1)]['W'])
            grad = self._units[tgt].grad(in_data)
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

    def _optimize(self, dataset, schedule, tracker):
        """Optimize system parameters."""

        nemoa.log('note', 'optimize model')
        nemoa.log('set', indent = '+1')

        # Optimize system parameters
        cfg = self._config['optimize']
        nemoa.log('note', "optimize '%s' (%s)" % \
            (self.get('name'), self.get('type')))
        nemoa.log('note', """using optimization algorithm '%s'"""
            % (cfg['algorithm']))

        if cfg['algorithm'].lower() == 'bprop':
            self._optimize_bprop(dataset, schedule, tracker)
        elif cfg['algorithm'].lower() == 'rprop':
            self._optimize_rprop(dataset, schedule, tracker)
        else:
            nemoa.log('error', """could not optimize model:
                unknown algorithm '%s'!""" % (cfg['algorithm']))

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
                self.Links.get_updates_from_delta(out[src],
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

        def getUpdate(prevGrad, prev_update, grad, accel, min_factor,
            max_factor):
            update = {}
            for key in grad.keys():
                sign = numpy.sign(grad[key])
                a = numpy.sign(prevGrad[key]) * sign
                magnitude = numpy.maximum(numpy.minimum(
                    prev_update[key] \
                    * (accel[0] * (a == -1) + accel[1] * (a == 0)
                    + accel[2] * (a == 1)), max_factor), min_factor)
                update[key] = magnitude * sign
            return update

        # RProp parameters
        accel = (0.5, 1., 1.2)
        init_rate = 0.001
        min_factor = 0.000001
        max_factor = 50.

        layers = self.mapping()

        # Compute gradient from delta rule
        grad = {'units': {}, 'links': {}}
        for id, src in enumerate(layers[:-1]):
            tgt = layers[id + 1]
            grad['units'][tgt] = \
                self._units[tgt].get_updates_from_delta(delta[src, tgt])
            grad['links'][(src, tgt)] = \
                self.Links.get_updates_from_delta(out[src],
                delta[src, tgt])

        # Get previous gradients and updates
        prev = tracker.read('rprop')
        if not prev:
            prev = {
                'gradient': grad,
                'update': {'units': {}, 'links': {}}}
            for id, src in enumerate(layers[:-1]):
                tgt = layers[id + 1]
                prev['update']['units'][tgt] = \
                    getDict(grad['units'][tgt], init_rate)
                prev['update']['links'][(src, tgt)] = \
                    getDict(grad['links'][(src, tgt)], init_rate)
        prev_gradient = prev['gradient']
        prev_update = prev['update']

        # Compute updates
        update = {'units': {}, 'links': {}}
        for id, src in enumerate(layers[:-1]):
            tgt = layers[id + 1]

            # calculate current rates for units
            update['units'][tgt] = getUpdate(
                prev_gradient['units'][tgt],
                prev_update['units'][tgt],
                grad['units'][tgt],
                accel, min_factor, max_factor)

            # calculate current rates for links
            update['links'][(src, tgt)] = getUpdate(
                prev_gradient['links'][(src, tgt)],
                prev_update['links'][(src, tgt)],
                grad['links'][(src, tgt)],
                accel, min_factor, max_factor)

        # Save updates to store
        tracker.write('rprop', gradient = grad, update = update)

        return update

    def _get_eval_system(self, data, func = 'accuracy', **kwargs):
        """Evaluation of system.

        Args:
            data: 2-tuple of numpy arrays: source data and target data
            func: string containing the name of a supported system
                evaluation function. For a full list of available
                functions use: model.system.about('eval')

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
        eval_args = []
        args_type = methods[func]['args']
        if args_type == 'none': pass
        elif args_type == 'input': eval_args.append(data[0])
        elif args_type == 'output': eval_args.append(data[1])
        elif args_type == 'all': eval_args.append(data)

        # prepare keyword arguments for evaluation function
        eval_kwargs = kwargs.copy()
        if not 'mapping' in eval_kwargs.keys() \
            or eval_kwargs['mapping'] == None:
            eval_kwargs['mapping'] = self.mapping()

        # evaluate system
        return getattr(self, method)(*eval_args, **eval_kwargs)

    @staticmethod
    def _about_system(): return {
        'energy': {
            'name': 'energy',
            'about': 'sum of local unit and link energies',
            'method': '_get_eval_system_energy',
            'args': 'all', 'format': '%.3f',
            'optimum': 'min'},
        'error': {
            'name': 'average reconstruction error',
            'about': 'mean error of reconstructed values',
            'method': '_get_eval_system_error',
            'args': 'all', 'format': '%.3f',
            'optimum': 'min'},
        'accuracy': {
            'name': 'average accuracy',
            'about': 'mean accuracy of reconstructed values',
            'method': '_get_eval_system_accuracy',
            'args': 'all', 'format': '%.3f',
            'optimum': 'max'},
        'precision': {
            'name': 'average precision',
            'about': 'mean precision of reconstructed values',
            'method': '_get_eval_system_precision',
            'args': 'all', 'format': '%.3f',
            'optimum': 'max'}
        }

    def _get_eval_system_error(self, *args, **kwargs):
        """Mean data reconstruction error of output units."""
        return numpy.mean(self._get_eval_units_error(*args, **kwargs))

    def _get_eval_system_accuracy(self, *args, **kwargs):
        """Mean data reconstruction accuracy of output units."""
        return numpy.mean(
            self._get_eval_units_accuracy(*args, **kwargs))

    def _get_eval_system_precision(self, *args, **kwargs):
        """Mean data reconstruction precision of output units."""
        return numpy.mean(
            self._get_eval_units_precision(*args, **kwargs))

    def _get_eval_system_energy(self, data, *args, **kwargs):
        """Sum of local link and unit energies."""

        mapping = list(self.mapping())
        energy = 0.

        # sum local unit energies
        for i in xrange(1, len(mapping) + 1):
            energy += numpy.sum(
                self._get_eval_units_energy(data[0],
                mapping = tuple(mapping[:i])))

        # sum local link energies
        for i in xrange(1, len(mapping)):
            energy += numpy.sum(
                self._get_eval_links_energy(data[0],
                mapping = tuple(mapping[:i+1])))

        return energy

    def _get_eval_units(self, data, func = 'accuracy', units = None,
        **kwargs):
        """Evaluation of target units.

        Args:
            data: 2-tuple with numpy arrays: source and target data
            func: string containing name of unit evaluation function
                For a full list of available system evaluation functions
                see: model.system.about('units')
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
        labels = self._get_units(layer = e_kwargs['mapping'][-1])
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
            'about': 'energy of units',
            'method': '_get_eval_units_energy',
            'show': 'diagram',
            'args': 'input', 'return': 'scalar', 'format': '%.3f'},
        'expect': {
            'name': 'expect',
            'about': 'reconstructed values',
            'method': '_get_eval_units_expect',
            'show': 'histogram',
            'args': 'input', 'return': 'vector', 'format': '%.3f'},
        'values': {
            'name': 'values',
            'about': 'reconstructed values',
            'method': '_get_eval_units_values',
            'show': 'histogram',
            'args': 'input', 'return': 'vector', 'format': '%.3f'},
        'samples': {
            'name': 'samples',
            'about': 'reconstructed samples',
            'method': '_get_eval_units_samples',
            'show': 'histogram',
            'args': 'input', 'return': 'vector', 'format': '%.3f'},
        'mean': {
            'name': 'mean values',
            'about': 'mean of reconstructed values',
            'method': '_get_eval_units_mean',
            'show': 'diagram',
            'args': 'input', 'return': 'scalar', 'format': '%.3f'},
        'variance': {
            'name': 'variance',
            'about': 'variance of reconstructed values',
            'method': '_get_eval_units_variance',
            'show': 'diagram',
            'args': 'input', 'return': 'scalar', 'format': '%.3f'},
        'residuals': {
            'name': 'residuals',
            'about': 'residuals of reconstructed values',
            'method': '_get_eval_units_residuals',
            'show': 'histogram',
            'args': 'all', 'return': 'vector', 'format': '%.3f'},
        'error': {
            'name': 'error',
            'about': 'mean error of reconstructed values',
            'method': '_get_eval_units_error',
            'show': 'diagram',
            'args': 'all', 'return': 'scalar', 'format': '%.3f'},
        'accuracy': {
            'name': 'accuracy',
            'about': 'accuracy of reconstructed values',
            'method': '_get_eval_units_accuracy',
            'show': 'diagram',
            'args': 'all', 'return': 'scalar', 'format': '%.3f'},
        'precision': {
            'name': 'precision',
            'about': 'precision of reconstructed values',
            'method': '_get_eval_units_precision',
            'show': 'diagram',
            'args': 'all', 'return': 'scalar', 'format': '%.3f'},
        'correlation': {
            'name': 'correlation',
            'about': 'correlation of reconstructed to real values',
            'method': '_get_eval_units_correlation',
            'show': 'diagram',
            'args': 'all', 'return': 'scalar', 'format': '%.3f'}
        }

    def _get_eval_units_expect(self, data, mapping = None,
        block = None):
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
        if block == None: in_data = data
        else:
            in_data = numpy.copy(data)
            for i in block: in_data[:,i] = numpy.mean(in_data[:,i])
        if len(mapping) == 2: return self._units[mapping[1]].expect(
            in_data, self._units[mapping[0]].params)
        outData = numpy.copy(in_data)
        for id in xrange(len(mapping) - 1):
            outData = self._units[mapping[id + 1]].expect(
                outData, self._units[mapping[id]].params)

        return outData

    def _get_eval_units_values(self, data, mapping = None, block = None,
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

        if mapping == None: mapping = self.mapping()
        if block == None: in_data = data
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
                self._get_eval_units_values(data, mapping[0:-1]),
                self._units[mapping[-2]].params)
        else:
            if len(mapping) == 1:
                return self._units[mapping[0]].get_values(in_data)
            elif len(mapping) == 2:
                return self._units[mapping[1]].get_values(
                    self._units[mapping[1]].expect(in_data,
                    self._units[mapping[0]].params))
            data = numpy.copy(in_data)
            for id in xrange(len(mapping) - 1):
                data = self._units[mapping[id + 1]].get_values(
                    self._units[mapping[id + 1]].expect(data,
                    self._units[mapping[id]].params))
            return data

    def _get_eval_units_samples(self, data, mapping = None,
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

        if mapping == None: mapping = self.mapping()
        if block == None: in_data = data
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
                self._get_eval_units_samples(data, mapping[0:-1]),
                self._units[mapping[-2]].params)
        else:
            if len(mapping) == 1:
                return self._units[mapping[0]].get_samples(data)
            elif len(mapping) == 2:
                return self._units[mapping[1]].get_samples_from_input(
                    data, self._units[mapping[0]].params)
            data = numpy.copy(data)
            for id in xrange(len(mapping) - 1):
                data = \
                    self._units[mapping[id + 1]].get_samples_from_input(
                    data, self._units[mapping[id]].params)
            return data

    def _get_eval_units_residuals(self, data, mapping = None,
        block = None):
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
        if mapping == None: mapping = self.mapping()

        # set unit values to mean (optional)
        if isinstance(block, list):
            d_src = numpy.copy(d_src)
            for i in block: d_src[:, i] = numpy.mean(d_src[:, i])

        # calculate estimated output values
        mOut = self._get_eval_units_expect(d_src, mapping)

        # calculate residuals
        return d_tgt - mOut

    def _get_eval_units_energy(self, data, mapping = None):
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

        data = self._get_eval_units_expect(data, mapping)

        return self._units[mapping[-1]].energy(data)

    def _get_eval_units_mean(self, data, mapping = None, block = None):
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
            model_out = self._get_eval_units_expect(data[0], mapping)
        else:
            data_in_copy = numpy.copy(data)
            for i in block:
                data_in_copy[:,i] = numpy.mean(data_in_copy[:,i])
            model_out = self._get_eval_units_expect(
                data_in_copy, mapping)

        return model_out.mean(axis = 0)

    def _get_eval_units_variance(self, data, mapping = None,
        block = None, **kwargs):
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

        if mapping == None:
            mapping = self.mapping()
        if block == None:
            model_out = self._get_eval_units_expect(data, mapping)
        else:
            data_in_copy = numpy.copy(data)
            for i in block:
                data_in_copy[:,i] = numpy.mean(data_in_copy[:,i])
            model_out = self._get_eval_units_expect(
                data_in_copy, mapping)

        return model_out.var(axis = 0)

    def _get_eval_units_error(self, data, norm = 'MSE', **kwargs):
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
                residuals. see nemoa.common.data_mean for a list of
                provided norms

        """

        res = self._get_eval_units_residuals(data, **kwargs)
        error = nemoa.common.data_mean(res, norm = norm)

        return error

    def _get_eval_units_accuracy(self, data, norm = 'MSE', **kwargs):
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
                see nemoa.common.data_mean for a list of provided norms

        """

        res = self._get_eval_units_residuals(data, **kwargs)
        normres = nemoa.common.data_mean(res, norm = norm)
        normdat = nemoa.common.data_mean(data[1], norm = norm)

        return 1. - normres / normdat

    def _get_eval_units_precision(self, data, norm = 'SD', **kwargs):
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
            norm: used norm to calculate precision
                see _get_data_deviation for a list of provided norms

        """

        res = self._get_eval_units_residuals(data, **kwargs)
        devres = nemoa.common.data_deviation(res, norm = norm)
        devdat = nemoa.common.data_deviation(data[1], norm = norm)

        return 1. - devres / devdat

    def _get_eval_units_correlation(self, data, mapping = None,
        block = None, **kwargs):
        """Correlation of reconstructed unit values.

        Args:
            data: 2-tuple of numpy arrays containing source and target
                data corresponding to the first and the last layer in
                the mapping
            mapping: n-tuple of strings containing the mapping
                from source unit layer (first argument of tuple)
                to target unit layer (last argument of tuple)
            block: list of string containing labels of units in the
                input layer that are blocked by setting the values to
                their means

        Returns:
            Numpy array with reconstructed correlation of units.

        """

        if mapping == None:
            mapping = self.mapping()
        if block == None:
            model_out = self._get_eval_units_expect(data, mapping)
        else:
            data_in_copy = numpy.copy(data)
            for i in block:
                data_in_copy[:,i] = numpy.mean(data_in_copy[:,i])
            model_out = self._get_eval_units_expect(
                data_in_copy, mapping)

        M = numpy.corrcoef(numpy.hstack(data).T)

        return True

    def _get_eval_links(self, data, func = 'energy', **kwargs):
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
        eval_args = []
        args_type = methods[func]['args']
        if args_type == 'none': pass
        elif args_type == 'input': eval_args.append(data[0])
        elif args_type == 'output': eval_args.append(data[1])
        elif args_type == 'all': eval_args.append(data)

        # prepare keyword arguments for evaluation functions
        eval_kwargs = kwargs.copy()
        if not 'mapping' in eval_kwargs.keys() \
            or eval_kwargs['mapping'] == None:
            eval_kwargs['mapping'] = self.mapping()

        # evaluate
        values = getattr(self, method)(*eval_args, **eval_kwargs)

        # create link dictionary
        in_labels = self._get_units(layer = eval_kwargs['mapping'][-2])
        out_labels = self._get_units(layer = eval_kwargs['mapping'][-1])
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
            'about': 'local energy of links',
            'method': '_get_eval_links_energy',
            'show': 'graph',
            'args': 'input', 'return': 'vector', 'format': '%.3f'}
        }

    def _get_eval_links_energy(self, data, mapping = None, **kwargs):
        """Return link energies of a layer.

        Args:
            mapping: tuple of strings containing the mapping
                from source unit layer (first argument of tuple)
                to target unit layer (last argument of tuple)

        """

        if len(mapping) == 1:
            # TODO
            return nemoa.log('error', """sorry: bad implementation of
                ann._get_eval_links_energy""")
        elif len(mapping) == 2:
            d_src  = data
            d_tgt = self._get_eval_units_values(d_src, mapping)
        else:
            d_src  = self._get_eval_units_expect(data, mapping[0:-1])
            d_tgt = self._get_eval_units_values(d_src, mapping[-2:])

        s_id = self.mapping().index(mapping[-2])
        t_id = self.mapping().index(mapping[-1])
        src = self._units[mapping[-2]].params
        tgt = self._units[mapping[-1]].params

        if (s_id, t_id) in self._params['links']:
            links = self._params['links'][(s_id, t_id)]
            return self.Links.energy(d_src, d_tgt, src, tgt, links)
        elif (t_id, s_id) in self._params['links']:
            links = self._params['links'][(t_id, s_id)]
            return self.Links.energy(d_tgt, d_src, tgt, src, links)

    def _get_eval_relation(self, data, func = 'correlation',
        relations = None, eval_stat = True, **kwargs):
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

        # get evaluation function
        methods = self._about_relations()
        if not func in methods.keys():
            return nemoa.log('error', """could not evaluate relations:
                unknown method '%s'.""" % (func))
        method = methods[func]['method']
        if not hasattr(self, method):
            return nemoa.log('error', """could not evaluate relations:
                unknown method '%s'.""" % (method))

        # prepare arguments for evaluation function
        eval_args = []
        args_type = methods[func]['args']
        if args_type == 'none': pass
        elif args_type == 'input': eval_args.append(data[0])
        elif args_type == 'output': eval_args.append(data[1])
        elif args_type == 'all': eval_args.append(data)

        # extract keyword arguments:
        # 'transform', 'format' and 'eval_stat'
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
        values = getattr(self, method)(*eval_args, **eval_kwargs)
        values_fmt = methods[func]['return']

        # create formated return values as matrix or dict
        # (for scalar relation evaluations)
        if values_fmt == 'scalar':
            # (optional) transform relation using 'transform' string
            if transform:
                M = values
                if 'C' in transform:
                    C = self._get_eval_relation_correlation(data)
                try:
                    T = eval(transform)
                    values = T
                except: return nemoa.log('error',
                    'could not transform relations: invalid syntax!')

            # create formated return values
            if ret_fmt == 'array': ret_val = values
            elif ret_fmt == 'dict':
                in_units = self._get_units(
                    layer = eval_kwargs['mapping'][0])
                out_units = self._get_units(
                    layer = eval_kwargs['mapping'][-1])
                ret_val = nemoa.common.dict_from_array(
                    values, (in_units, out_units))

                # optionally evaluate statistical values over all relations
                if eval_stat:
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
            'about': """
                undirected data based relation describing
                the 'linearity' between variables (units) """,
            'directed': False, 'signed': True, 'normal': True,
            'method': '_get_eval_relation_correlation', 'show': 'heatmap',
            'args': 'all', 'return': 'scalar', 'format': '%.3f'},
        'capacity': {
            'name': 'network capacity',
            'about': """
                directed graph based relation describing
                the 'network capacity' between units (variables). """,
            'directed': True, 'signed': True, 'normal': False,
            'method': '_get_eval_relation_capacity', 'show': 'heatmap',
            'args': 'all', 'return': 'scalar', 'format': '%.3f'},
        'knockout': {
            'name': 'knockout effect',
            'about': """
                directed data manipulation based relation describing
                the increase of the data reconstruction error of a given
                output unit, when setting the values of a given input
                unit to its mean value. """,
            'directed': True, 'signed': True, 'normal': False,
            'method': '_get_eval_relation_knockout', 'show': 'heatmap',
            'args': 'all', 'return': 'scalar', 'format': '%.3f'},
        'induction': {
            'name': 'induction',
            'about': """
                directed data manipulation based relation describing
                the induced deviation of reconstructed values of a given
                output unit, when manipulating the values of a given
                input unit. """,
            'directed': True, 'signed': True, 'normal': True,
            'method': '_get_eval_relation_induction', 'show': 'heatmap',
            'args': 'all', 'return': 'scalar', 'format': '%.3f'},
        }

    def _get_eval_relation_correlation(self, data, mapping = None, **kwargs):
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
        in_labels = self._get_units(layer = mapping[0])
        out_labels = self._get_units(layer = mapping[-1])

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

    def _get_eval_relation_capacity(self, data, mapping = None, **kwargs):
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

    def _get_eval_relation_knockout(self, data, mapping = None, **kwargs):
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
        in_labels = self._get_units(layer = mapping[0])
        out_labels = self._get_units(layer = mapping[-1])

        # prepare knockout matrix
        R = numpy.zeros((len(in_labels), len(out_labels)))

        # calculate unit values without knockout
        if not 'measure' in kwargs: measure = 'error'
        else: measure = kwargs['measure']
        method_name = self.about('units', measure, 'name')
        default = self._get_eval_units(data,
            func = measure, mapping = mapping)

        # calculate unit values with knockout
        for in_id, in_unit in enumerate(in_labels):

            # modify unit and calculate unit values
            knockout = self._get_eval_units(data, func = measure,
                mapping = mapping, block = [in_id])

            # store difference in knockout matrix
            for out_id, out_unit in enumerate(out_labels):
                R[in_id, out_id] = \
                    knockout[out_unit] - default[out_unit]

        return R

    def _get_eval_relation_induction(self, data, mapping = None,
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
        input_units = self._get_units(layer = mapping[0])
        output_units = self._get_units(layer = mapping[-1])
        R = numpy.zeros((len(input_units), len(output_units)))

        # get indices of representatives
        r_ids = [int((i + 0.5) * int(float(data[0].shape[0])
            / points)) for i in xrange(points)]

        for i_id, i_unit in enumerate(input_units):
            i_curve = numpy.take(numpy.sort(data[0][:, i_id]), r_ids)
            i_curve = amplify * i_curve

            # create output matrix for each output
            C = {o_unit: numpy.zeros((data[0].shape[0], points)) \
                for o_unit in output_units}
            for p_id in xrange(points):
                i_data  = data[0].copy()
                i_data[:, i_id] = i_curve[p_id]
                o_expect = self._get_eval_units((i_data, data[1]),
                    func = 'expect', mapping = mapping)
                for o_unit in output_units:
                    C[o_unit][:, p_id] = o_expect[o_unit]

            # calculate mean of standard deviations of outputs
            for o_id, o_unit in enumerate(output_units):

                # calculate sign by correlating input and output
                corr = numpy.zeros(data[0].shape[0])
                for i in xrange(data[0].shape[0]):
                    corr[i] = numpy.correlate(C[o_unit][i, :], i_curve)
                sign = numpy.sign(corr.mean())

                # calculate norm by mean over maximum 5% of data
                bound = int((1. - gauge) * data[0].shape[0])
                subset = numpy.sort(C[o_unit].std(axis = 1))[bound:]
                norm = subset.mean() / data[1][:, o_id].std()

                # calculate influence
                R[i_id, o_id] = sign * norm

        return R

    def mapping(self, src = None, tgt = None):
        """Mapping of units from source to target.

        Args:
            src: name of source unit layer
            tgt: name of target unit layer

        Returns:
            tuple with names of unit layers from source to target.

        """

        mapping = tuple([l['layer'] for l in self._params['units']])
        sid = mapping.index(src) \
            if isinstance(src, str) and src in mapping else 0
        tid = mapping.index(tgt) \
            if isinstance(tgt, str) and tgt in mapping else len(mapping)

        return mapping[sid:tid + 1] if sid <= tid \
            else mapping[tid:sid + 1][::-1]

    def _get_test_data(self, dataset):
        """Return tuple with default test data."""

        return dataset.get('data',
            cols = (self.mapping()[0], self.mapping()[-1]))
