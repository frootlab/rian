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

    def _algorithm_bprop_forward(self, data):
        """Backpropagation of error forward pass.

        Compute (most) estimated values for all layers, from given data
        on input layer.

        Returns:
            Dictionary with layers names as keys and expectation values
            of (the units of) the layers as values, stored in numpy
            arrays.

        """

        mapping = self._get_mapping()
        values = {}
        for lid, layer in enumerate(mapping):
            if lid == 0:
                values[layer] = data
                continue
            values[layer] = self._algorithm_unitexpect(
                values[mapping[lid - 1]], mapping[lid - 1:lid + 1])

        return values

    def _algorithm_bprop_backward(self, outputData, out):
        """Backpropagation of error backward pass.

        Returns:
            Weight delta from backpropagation of error.

        """

        layers = self._get_mapping()
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

    def _algorithm_update_params(self, updates):
        """Update parameters from dictionary."""

        layers = self._get_mapping()
        for id, layer in enumerate(layers[:-1]):
            src = layer
            tgt = layers[id + 1]
            self._params['links'][(id, id + 1)]['W'] += \
                updates['links'][(src, tgt)]['W']
            self._units[tgt].update(updates['units'][tgt])

        return True

    @nemoa.common.decorators.attributes(
        name     = 'bprop',
        category = ('system', 'optimization')
    )
    def _algorithm_bprop(self, dataset, schedule, tracker):
        """Optimize parameters using backpropagation of error."""

        # update parameters
        while tracker.update():

            # get training data (sample from minibatches)
            data = tracker.get('data', 'training')
            # forward pass (compute estimations from given input)
            values = self._algorithm_bprop_forward(data[0])
            # backward pass (compute deltas from given output)
            delta = self._algorithm_bprop_backward(data[1], values)
            # compute parameter updates
            updates = self._algorithm_bprop_update(values, delta)
            # update parameters
            self._algorithm_update_params(updates)

        return True

    def _algorithm_bprop_update(self, out, delta, rate = 0.1):
        """Compute parameter update directions from weight deltas."""

        layers = self._get_mapping()
        links = {}
        units = {}
        for id, src in enumerate(layers[:-1]):
            tgt = layers[id + 1]
            updu = self._units[tgt].get_updates_delta(delta[src, tgt])
            updl = nemoa.system.commons.links.Links.get_updates_delta(
                out[src], delta[src, tgt])
            units[tgt] = {key: rate * updu[key]
                for key in updu.iterkeys()}
            links[(src, tgt)] = {key: rate * updl[key]
                for key in updl.iterkeys()}

        return {'units': units, 'links': links}

    @nemoa.common.decorators.attributes(
        name     = 'rprop',
        category = ('system', 'optimization')
    )
    def _algorithm_rprop(self, dataset, schedule, tracker):
        """Optimize parameters using resiliant backpropagation (RPROP).

        resiliant backpropagation ...

        """

        # update parameters
        while tracker.update():

            # get training data (sample from minibatches)
            data = tracker.get('data', 'training')
            # forward pass (compute estimations from given input)
            values = self._algorithm_bprop_forward(data[0])
            # backward pass (compute deltas from given output)
            delta = self._algorithm_bprop_backward(data[1], values)
            # compute parameter updates
            updates = self._algorithm_rprop_get_updates(values, delta,
                tracker)
            # update parameters
            self._algorithm_update_params(updates)

        return True

    def _algorithm_rprop_get_updates(self, out, delta, tracker):

        def _get_dict(dict, val): return {key: val * numpy.ones(
            shape = dict[key].shape) for key in dict.keys()}

        def _get_update(prevGrad, prev_update, grad, accel, min_factor,
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
        accel = (.5, 1., 1.2)
        init_rate = .001
        min_factor = .000001
        max_factor = 50.

        layers = self._get_mapping()

        # compute gradient from delta rule
        grad = {'units': {}, 'links': {}}
        for id, src in enumerate(layers[:-1]):
            tgt = layers[id + 1]
            grad['units'][tgt] = \
                self._units[tgt].get_updates_delta(delta[src, tgt])
            grad['links'][(src, tgt)] = \
                nemoa.system.commons.links.Links.get_updates_delta(
                out[src], delta[src, tgt])

        # get previous gradients and updates
        prev = tracker.read('rprop')
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
        tracker.write('rprop', gradient = grad, update = update)

        return update

    @nemoa.common.decorators.attributes(
        name     = 'energy',
        category = ('system', 'evaluation'),
        args     = 'all',
        formater = lambda val: '%.3f' % (val),
        optimum  = 'min'
    )
    def _algorithm_energy(self, data, *args, **kwargs):
        """Sum of local link and unit energies."""

        mapping = list(self._get_mapping())
        energy = 0.

        # sum local unit energies
        for i in xrange(1, len(mapping) + 1):
            energy += self._algorithm_units_energy(data[0],
                mapping = tuple(mapping[:i])).sum(axis = 1)

        # sum local link energies
        for i in xrange(1, len(mapping)):
            energy += self._algorithm_links_energy(data[0],
                mapping = tuple(mapping[:i + 1])).sum(axis = (1, 2))

        # calculate (pseudo) energy of system
        return numpy.log(1. + numpy.exp(-energy).sum())

    @nemoa.common.decorators.attributes(
        name     = 'energy',
        category = ('system', 'units', 'evaluation'),
        args     = 'input',
        retfmt   = 'scalar',
        formater = lambda val: '%.3f' % (val),
        plot     = 'diagram'
    )
    def _algorithm_units_energy(self, data, mapping = None):
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
        if mapping == None: mapping = self._get_mapping()
        data = self._algorithm_unitexpect(data, mapping)
        return self._units[mapping[-1]].energy(data)

    @nemoa.common.decorators.attributes(
        name     = 'energy',
        category = ('system', 'links', 'evaluation'),
        args     = 'input',
        retfmt   = 'scalar',
        formater = lambda val: '%.3f' % (val),
        plot     = 'diagram'
    )
    def _algorithm_links_energy(self, data, mapping = None, **kwargs):
        """Return link energies of a layer.

        Args:
            mapping: tuple of strings containing the mapping
                from source unit layer (first argument of tuple)
                to target unit layer (last argument of tuple)

        """

        if len(mapping) == 1:
            # TODO
            return nemoa.log('error', """sorry: bad implementation of
                ann._algorithm_links_energy""")
        elif len(mapping) == 2:
            sdata = data
            tdata = self._algorithm_unitvalues(sdata, mapping)
        else:
            sdata = self._algorithm_unitexpect(data, mapping[0:-1])
            tdata = self._algorithm_unitvalues(sdata, mapping[-2:])

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
