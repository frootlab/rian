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
        """Get data for optimization."""

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

    @nemoa.common.decorators.attributes(
        name     = 'bprop',
        category = ('system', 'optimization'))
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

    @nemoa.common.decorators.attributes(
        name     = 'rprop',
        category = ('system', 'optimization'))
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

    @nemoa.common.decorators.attributes(
        name     = 'energy',
        category = ('system', 'evaluation'),
        args     = 'all',
        format   = '%.3f',
        optimum  = 'min')
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

    @nemoa.common.decorators.attributes(
        name     = 'energy',
        category = ('system', 'units', 'evaluation'),
        args     = 'input',
        retfmt   = 'scalar',
        format   = '%.3f',
        show     = 'diagram')
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

    @nemoa.common.decorators.attributes(
        name     = 'energy',
        category = ('system', 'links', 'evaluation'),
        args     = 'input',
        retfmt   = 'scalar',
        format   = '%.3f',
        show     = 'diagram')
    def _eval_links_energy(self, data, mapping = None, **kwargs):
        """Return link energies of a layer.

        Args:
            mapping: tuple of strings containing the mapping
                from source unit layer (first argument of tuple)
                to target unit layer (last argument of tuple)

        """

        if len(mapping) == 1:
            # TODO
            return nemoa.log('error', """sorry: bad implementation of
                ann._eval_links_energy""")
        elif len(mapping) == 2:
            d_src  = data
            d_tgt = self._eval_units_values(d_src, mapping)
        else:
            d_src  = self._eval_units_expect(data, mapping[0:-1])
            d_tgt = self._eval_units_values(d_src, mapping[-2:])

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
