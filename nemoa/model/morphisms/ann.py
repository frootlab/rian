# -*- coding: utf-8 -*-
"""Artificial Neuronal Network (ANN)."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

import numpy
import nemoa.model.morphisms.base
from flab.base import catalog

class ANN(nemoa.model.morphisms.base.Optimizer):

    _default = {
        'algorithm': 'bprop',
        'updates': 10000,
        'noise_enable': False,
        'minibatch_size': 100,
        'minibatch_update_interval': 10,
        'schedule': None,
        'visible': None,
        'hidden': None,
        'adjacency_enable': False,
        'bprop_rate': .1,
        'rprop_accel': (.5, 1., 1.2),
        'rprop_init_rate': .001,
        'rprop_min_factor': .000001,
        'rprop_max_factor': 50.,
        'tracker_estimate_time': False,
        'tracker_estimate_time_wait': 15.,
        'tracker_obj_tracking_enable': True,
        'tracker_obj_init_wait': 0.01,
        'tracker_obj_function': 'accuracy',
        'tracker_obj_keep_optimum': True,
        'tracker_obj_update_interval': 100,
        'tracker_eval_enable': True,
        'tracker_eval_function': 'accuracy',
        'tracker_eval_time_interval': 10.,
        'ignore_units': [] }

    @catalog.custom(
        name     = 'bprop',
        longname = 'backpropagation of error',
        category = 'optimization',
        type     = 'algorithm',
        syscheck = None)

    def _bprop(self):
        """Optimize parameters using backpropagation of error."""

        while self.update():
            # get training data (sample from stratified minibatches)
            data = self._get_data_training()
            # forward pass (compute estimations from given input)
            values = self._bprop_forward(data[0])
            # backward pass (compute deltas to given output)
            deltas = self._bprop_backward(data[1], values)
            # compute parameter updates
            updates = self._bprop_get_updates(values, deltas)
            # update parameters
            self._bprop_update(updates)

        return True

    def _bprop_forward(self, data):
        """Backpropagation of error forward pass.

        Compute expectation values for all layers, from given data
        on input layer using current system parameters.

        Returns:
            Dictionary with layers names as keys and expectation values
            of (the units of) the layers as values, stored in numpy
            arrays.

        """

        mapping = self.model.system._get_mapping()
        values = {}
        for lid, layer in enumerate(mapping):
            if lid == 0:
                values[layer] = data
                continue
            values[layer] = self.model.system._get_unitexpect(
                values[mapping[lid - 1]], mapping[lid - 1:lid + 1])

        return values

    def _bprop_backward(self, tgtdata, values):
        """Backpropagation of error backward pass.

        Returns:
            Weight delta from backpropagation of error.

        """

        system = self.model.system

        layers = system._get_mapping()
        delta = {}
        for id in range(len(layers) - 1)[::-1]:
            src = layers[id]
            tgt = layers[id + 1]
            if id == len(layers) - 2:
                delta[(src, tgt)] = values[tgt] - tgtdata
                continue
            srcdata = system._units[tgt].params['bias'] \
                + numpy.dot(values[src],
                system._params['links'][(id, id + 1)]['W'])
            grad = system._units[tgt].grad(srcdata)
            delta[(src, tgt)] = numpy.dot(delta[(tgt, layers[id + 2])],
                system._params['links'][(id + 1, id + 2)]['W'].T) * grad

        return delta

    def _bprop_update(self, updates):
        """Update parameters from dictionary."""

        system = self.model.system

        layers = system._get_mapping()
        for id, layer in enumerate(layers[:-1]):
            src = layer
            tgt = layers[id + 1]
            system._params['links'][(id, id + 1)]['W'] += \
                updates['links'][(src, tgt)]['W']
            system._units[tgt].update(updates['units'][tgt])

        return True

    def _bprop_get_updates(self, out, delta):
        """Compute parameter update directions from weight deltas."""

        system = self.model.system

        rate = self._config.get('bprop_rate', .1)

        layers = system._get_mapping()
        links = {}
        units = {}
        for id, src in enumerate(layers[:-1]):
            tgt = layers[id + 1]
            updu = system._units[tgt].get_updates_delta(delta[src, tgt])
            updl = nemoa.system.commons.links.Links.get_updates_delta(
                out[src], delta[src, tgt])
            units[tgt] = {key: rate * updu[key]
                for key in updu.keys()}
            links[(src, tgt)] = {key: rate * updl[key]
                for key in updl.keys()}

        return { 'units': units, 'links': links }

    @catalog.custom(
        name     = 'rprop',
        longname = 'resiliant backpropagation of error',
        category = 'optimization',
        type     = 'algorithm',
        syscheck = None
    )
    def _rprop(self):
        """Optimize parameters using resiliant backpropagation (RPROP).

        resiliant backpropagation ...

        2Do: self._config['resilience'] = True; return self._bprob()

        """

        while self.update():
            data = self._get_data_training()
            # forward pass (compute estimations from given input)
            values = self._bprop_forward(data[0])
            # backward pass (compute deltas to given output)
            deltas = self._bprop_backward(data[1], values)
            # compute parameter updates
            updates = self._rprop_get_updates(values, deltas)
            # update parameters
            self._bprop_update(updates)

        return True

    def _rprop_get_updates(self, out, delta):
        """ """

        def _get_dict(dict, val): return {key: val * numpy.ones(
            shape = dict[key].shape) for key in list(dict.keys())}

        def _get_update(prevGrad, prev_update, grad, accel, min_factor,
            max_factor):
            update = {}
            for key in list(grad.keys()):
                sign = numpy.sign(grad[key])
                a = numpy.sign(prevGrad[key]) * sign
                magnitude = numpy.maximum(numpy.minimum(
                    prev_update[key] \
                    * (accel[0] * (a == -1) + accel[1] * (a == 0)
                    + accel[2] * (a == 1)), max_factor), min_factor)
                update[key] = magnitude * sign
            return update

        # RProp parameters
        accel = self._config.get('rprop_accel', (.5, 1., 1.2))
        init_rate = self._config.get('rprop_init_rate', .001)
        min_factor = self._config.get('rprop_min_factor', .000001)
        max_factor = self._config.get('rprop_max_factor', 50.)

        system = self.model.system
        layers = system._get_mapping()

        # compute gradient from delta rule
        grad = {'units': {}, 'links': {}}
        for id, src in enumerate(layers[:-1]):
            tgt = layers[id + 1]
            grad['units'][tgt] = \
                system._units[tgt].get_updates_delta(delta[src, tgt])
            grad['links'][(src, tgt)] = \
                nemoa.system.commons.links.Links.get_updates_delta(
                out[src], delta[src, tgt])

        # get previous gradients and updates
        prev = self.read('rprop')
        if not prev:
            prev = {
                'gradient': grad,
                'update': {'units': {}, 'links': {}}}
            for id, src in enumerate(layers[:-1]):
                tgt = layers[id + 1]
                prev['update']['units'][tgt] = \
                    _get_dict(grad['units'][tgt], init_rate)
                prev['update']['links'][(src, tgt)] = \
                    _get_dict(grad['links'][(src, tgt)], init_rate)
        prev_gradient = prev['gradient']
        prev_update = prev['update']

        # compute updates
        update = {'units': {}, 'links': {}}
        for id, src in enumerate(layers[:-1]):
            tgt = layers[id + 1]

            # calculate current rates for units
            update['units'][tgt] = _get_update(
                prev_gradient['units'][tgt],
                prev_update['units'][tgt],
                grad['units'][tgt],
                accel, min_factor, max_factor)

            # calculate current rates for links
            update['links'][(src, tgt)] = _get_update(
                prev_gradient['links'][(src, tgt)],
                prev_update['links'][(src, tgt)],
                grad['links'][(src, tgt)],
                accel, min_factor, max_factor)

        # save updates to store
        self.write('rprop', gradient = grad, update = update)

        return update
