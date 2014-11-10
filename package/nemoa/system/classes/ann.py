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
            'ignore_units': [],
            'algorithm': 'bprop',
            'den_corr_enable': False,
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
                and not nemoa.system.commons.units.Gauss.check(layer):
                return False
            elif layer['class'] == 'sigmoid' \
                and not nemoa.system.commons.units.Sigmoid.check(layer):
                return False

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
            nemoa.system.commons.units.Gauss.remove(layer, select)
        elif layer['class'] == 'sigmoid':
            nemoa.system.commons.units.Sigmoid.remove(layer, select)

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
        if config['den_corr_enable']:
            kwargs['noise'] = (config['den_corr_type'],
                config['den_corr_factor'])
        return dataset.get('data', **kwargs)

    def _optimize_get_values(self, data):
        """Forward pass (compute estimated values, from given input). """

        mapping = self.mapping()
        out = {}
        for lid, layer in enumerate(mapping):
            if lid == 0: out[layer] = data
            else: out[layer] = self._calc_units_expect(
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
            (self._get_name(), self._get_type()))
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
                nemoa.system.commons.links.Links.get_updates_from_delta(
                out[src], delta[src, tgt]), rate)

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
                nemoa.system.commons.links.Links.get_updates_from_delta(
                out[src], delta[src, tgt])

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

    #def _get_algorithms(self):
        #return {
            #'system': {
                #'energy': {
                    #'name': 'energy',
                    #'about': 'sum of local unit and link energies',
                    #'method': '_calc_system_energy',
                    #'args': 'all', 'format': '%.3f',
                    #'optimum': 'min'},
                #'error': {
                    #'name': 'average reconstruction error',
                    #'about': 'mean error of reconstructed values',
                    #'method': '_calc_error',
                    #'args': 'all', 'format': '%.3f',
                    #'optimum': 'min'},
                #'accuracy': {
                    #'name': 'average accuracy',
                    #'about': 'mean accuracy of reconstructed values',
                    #'method': '_calc_accuracy',
                    #'args': 'all', 'format': '%.3f',
                    #'optimum': 'max'},
                #'precision': {
                    #'name': 'average precision',
                    #'about': 'mean precision of reconstructed values',
                    #'method': '_calc_precision',
                    #'args': 'all', 'format': '%.3f',
                    #'optimum': 'max'} } }

    @staticmethod
    def _about_system(): return {
        'energy': {
            'name': 'energy',
            'about': 'sum of local unit and link energies',
            'method': '_calc_system_energy',
            'args': 'all', 'format': '%.3f',
            'optimum': 'min'},
        'error': {
            'name': 'average reconstruction error',
            'about': 'mean error of reconstructed values',
            'method': '_calc_error',
            'args': 'all', 'format': '%.3f',
            'optimum': 'min'},
        'accuracy': {
            'name': 'average accuracy',
            'about': 'mean accuracy of reconstructed values',
            'method': '_calc_accuracy',
            'args': 'all', 'format': '%.3f',
            'optimum': 'max'},
        'precision': {
            'name': 'average precision',
            'about': 'mean precision of reconstructed values',
            'method': '_calc_precision',
            'args': 'all', 'format': '%.3f',
            'optimum': 'max'}
        }

    @staticmethod
    def _about_units(): return {
        'energy': {
            'name': 'energy',
            'about': 'energy of units',
            'method': '_calc_units_energy',
            'show': 'diagram',
            'args': 'input', 'return': 'scalar', 'format': '%.3f'},
        'expect': {
            'name': 'expect',
            'about': 'reconstructed values',
            'method': '_calc_units_expect',
            'show': 'histogram',
            'args': 'input', 'return': 'vector', 'format': '%.3f'},
        'values': {
            'name': 'values',
            'about': 'reconstructed values',
            'method': '_calc_units_values',
            'show': 'histogram',
            'args': 'input', 'return': 'vector', 'format': '%.3f'},
        'samples': {
            'name': 'samples',
            'about': 'reconstructed samples',
            'method': '_calc_units_samples',
            'show': 'histogram',
            'args': 'input', 'return': 'vector', 'format': '%.3f'},
        'mean': {
            'name': 'mean values',
            'about': 'mean of reconstructed values',
            'method': '_calc_units_mean',
            'show': 'diagram',
            'args': 'input', 'return': 'scalar', 'format': '%.3f'},
        'variance': {
            'name': 'variance',
            'about': 'variance of reconstructed values',
            'method': '_calc_units_variance',
            'show': 'diagram',
            'args': 'input', 'return': 'scalar', 'format': '%.3f'},
        'residuals': {
            'name': 'residuals',
            'about': 'residuals of reconstructed values',
            'method': '_calc_units_residuals',
            'show': 'histogram',
            'args': 'all', 'return': 'vector', 'format': '%.3f'},
        'error': {
            'name': 'error',
            'about': 'mean error of reconstructed values',
            'method': '_calc_units_error',
            'show': 'diagram',
            'args': 'all', 'return': 'scalar', 'format': '%.3f'},
        'accuracy': {
            'name': 'accuracy',
            'about': 'accuracy of reconstructed values',
            'method': '_calc_units_accuracy',
            'show': 'diagram',
            'args': 'all', 'return': 'scalar', 'format': '%.3f'},
        'precision': {
            'name': 'precision',
            'about': 'precision of reconstructed values',
            'method': '_calc_units_precision',
            'show': 'diagram',
            'args': 'all', 'return': 'scalar', 'format': '%.3f'},
        'correlation': {
            'name': 'correlation',
            'about': 'correlation of reconstructed to real values',
            'method': '_calc_units_correlation',
            'show': 'diagram',
            'args': 'all', 'return': 'scalar', 'format': '%.3f'}
        }

    @staticmethod
    def _about_links(): return {
        'energy': {
            'name': 'energy',
            'about': 'local energy of links',
            'method': '_calc_links_energy',
            'show': 'graph',
            'args': 'input', 'return': 'vector', 'format': '%.3f'}
        }

    @staticmethod
    def _about_relations(): return {
        'correlation': {
            'name': 'correlation',
            'about': """
                undirected data based relation describing
                the 'linearity' between variables (units) """,
            'directed': False, 'signed': True, 'normal': True,
            'method': '_calc_relation_correlation', 'show': 'heatmap',
            'args': 'all', 'return': 'scalar', 'format': '%.3f'},
        'capacity': {
            'name': 'network capacity',
            'about': """
                directed graph based relation describing
                the 'network capacity' between units (variables). """,
            'directed': True, 'signed': True, 'normal': False,
            'method': '_calc_relation_capacity', 'show': 'heatmap',
            'args': 'all', 'return': 'scalar', 'format': '%.3f'},
        'knockout': {
            'name': 'knockout effect',
            'about': """
                directed data manipulation based relation describing
                the increase of the data reconstruction error of a given
                output unit, when setting the values of a given input
                unit to its mean value. """,
            'directed': True, 'signed': True, 'normal': False,
            'method': '_calc_relation_knockout', 'show': 'heatmap',
            'args': 'all', 'return': 'scalar', 'format': '%.3f'},
        'induction': {
            'name': 'induction',
            'about': """
                directed data manipulation based relation describing
                the induced deviation of reconstructed values of a given
                output unit, when manipulating the values of a given
                input unit. """,
            'directed': True, 'signed': True, 'normal': True,
            'method': '_calc_relation_induction', 'show': 'heatmap',
            'args': 'all', 'return': 'scalar', 'format': '%.3f'},
        }

    def _calc_system(self, data, func = 'accuracy', **kwargs):
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

    def _calc_system_energy(self, data, *args, **kwargs):
        """Sum of local link and unit energies."""

        mapping = list(self.mapping())
        energy = 0.

        # sum local unit energies
        for i in xrange(1, len(mapping) + 1):
            energy += numpy.sum(
                self._calc_units_energy(data[0],
                mapping = tuple(mapping[:i])))

        # sum local link energies
        for i in xrange(1, len(mapping)):
            energy += numpy.sum(
                self._calc_links_energy(data[0],
                mapping = tuple(mapping[:i+1])))

        return energy

    def _calc_units(self, data, func = 'accuracy', units = None,
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

    def _calc_units_energy(self, data, mapping = None):
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

        data = self._calc_units_expect(data, mapping)

        return self._units[mapping[-1]].energy(data)

    def _calc_links(self, data, func = 'energy', **kwargs):
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

    def _calc_links_energy(self, data, mapping = None, **kwargs):
        """Return link energies of a layer.

        Args:
            mapping: tuple of strings containing the mapping
                from source unit layer (first argument of tuple)
                to target unit layer (last argument of tuple)

        """

        if len(mapping) == 1:
            # TODO
            return nemoa.log('error', """sorry: bad implementation of
                ann._calc_links_energy""")
        elif len(mapping) == 2:
            d_src  = data
            d_tgt = self._calc_units_values(d_src, mapping)
        else:
            d_src  = self._calc_units_expect(data, mapping[0:-1])
            d_tgt = self._calc_units_values(d_src, mapping[-2:])

        s_id = self.mapping().index(mapping[-2])
        t_id = self.mapping().index(mapping[-1])
        src = self._units[mapping[-2]].params
        tgt = self._units[mapping[-1]].params

        if (s_id, t_id) in self._params['links']:
            links = self._params['links'][(s_id, t_id)]
            return nemoa.system.commons.links.Links.energy(
                d_src, d_tgt, src, tgt, links)
        elif (t_id, s_id) in self._params['links']:
            links = self._params['links'][(t_id, s_id)]
            return nemoa.system.commons.links.Links.energy(
                d_tgt, d_src, tgt, src, links)

    def _calc_relation(self, data, func = 'correlation',
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
                    C = self._calc_relation_correlation(data)
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
