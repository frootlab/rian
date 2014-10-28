# -*- coding: utf-8 -*-
"""Deep Belief Network (DBN).

Deep Beliefe Network implementation for multilayer data modeling,
nonlinear data dimensionality reduction and nonlinear data analysis.

"""

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.system.classes.ann
import numpy

class DBN(nemoa.system.classes.ann.ANN):
    """Deep Belief Network (DBN).

    'Deep Belief Networks' are layered feed forward Artificial Neural
    Networks with hidden layers, a symmetric graph structure and
    optimization in two steps. The first step, known as 'pretraining',
    utilizes Restricted Boltzmann Machines as builing blocks to
    initialize the optimization parameters. This allows the introduction
    of energy based weak constraints on direct unit interactions and
    improves the ability to overcome bad local optima. The second step,
    known as 'finetuning', uses a gradient descent by Backpropagation of
    Error to optimize the reconstruction of output data.

    DBNs are typically used for data classification tasks and nonlinear
    dimensionality reduction (1). By using data manipulation tests, DBNs
    can also be utilized to find and analyse nonlinear dependency
    sructures in data.

    References:
        (1) "Reducing the dimensionality of data with neural networks",
            G. E. Hinton, R. R. Salakhutdinov, Science, 2006

    """

    _default = {
        'params': {
            'visible': 'auto',
            'hidden': 'auto',
            'visible_class': 'gauss',
            'hidden_class': 'sigmoid',
            'visible_system_type': 'rbm.GRBM',
            'hidden_system_type': 'rbm.RBM' },
        'init': {
            'check_dataset': False,
            'ignore_units': [],
            'w_sigma': 0.5 },
        'optimize': {
            'pretraining': True,
            'finetuning': True,
            'check_dataset': False,
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

    def _check_network(self, network):
        return network._is_compatible_dbn()

    def _optimize(self, dataset, schedule, tracker):
        """Optimize system parameters."""

        # get configuration dictionary for optimization
        config = self._config['optimize']

        # (optional) pretraining of system parameters
        # perform forward optimization of ann using
        # restricted boltzmann machines as subsystems
        if config['pretraining']:
            self._optimize_pretraining(dataset, schedule, tracker)

        # (optional) finetuning of system parameters
        # perform backward optimization of ann
        # using backpropagation of error
        if config['finetuning']:
            self._optimize_finetuning(dataset, schedule, tracker)

        return True

    def _optimize_pretraining(self, dataset, schedule, tracker):
        """Pretraining model using Restricted Boltzmann Machines."""

        if not 'units' in self._params:
            return nemoa.log('error', """could not configure subsystems:
                no layers have been defined!""")

        # create and configure subsystems
        subsystems = []

        all_visible = self._params['units'][0]['id'] \
            + self._params['units'][-1]['id']

        for layer_id in xrange((len(self._params['units']) - 1)  / 2):
            src = self._params['units'][layer_id]
            tgt = self._params['units'][layer_id + 1]
            links = self._params['links'][(layer_id, layer_id + 1)]

            # create network of subsystem
            name = '%s ↔ %s' % (src['layer'], tgt['layer'])
            visible_nodes = all_visible if src['visible'] else src['id']
            network = nemoa.network.create('factor', name = name,
                visible_nodes = visible_nodes,
                visible_type = src['class'],
                hidden_nodes = tgt['id'],
                hidden_type = tgt['class'])

            # create subsystem and configure with network
            config = { 'name': name, 'type': None }
            if src['class'] == 'gauss':
                if tgt['class'] == 'sigmoid':
                    config['type'] = 'rbm.GRBM'
            elif src['class'] == 'sigmoid':
                if tgt['class'] == 'sigmoid':
                    config['type'] = 'rbm.RBM'
            if not config['type']:
                return nemoa.log('error', """could not create
                    rbm: unsupported pair of unit classes '%s ↔ %s'"""
                    % (src['class'], tgt['class']))

            system = nemoa.system.new(config = config)
            system.configure(network)

            # link subsystem
            subsystems.append(system)

            # link parameters of links of subsystem
            links['init'] = system._params['links'][(0, 1)]

            # link parameters of layer of subsystem
            if layer_id == 0:
                src['init'] = system._units['visible'].params
                tgt['init'] = system._units['hidden'].params
                system._config['init']['ignore_units'] = []
                system._config['optimize']['ignore_units'] = []
            else:
                # do not link params from upper layer!
                # upper layer should be linked with previous subsystem
                # (higher abstraction layer)
                tgt['init'] = system._params['units'][1]
                system._config['init']['ignore_units'] = ['visible']
                system._config['optimize']['ignore_units'] = ['visible']

        # Optimize subsystems

        # create backup of dataset values (before transformation)
        dataset_backup = dataset.get('copy')

        # optimize subsystems
        for sys_id in xrange(len(subsystems)):

            # link subsystem
            system = subsystems[sys_id]

            # transform dataset with previous system / fix lower stack
            if sys_id > 0:
                prev_sys = subsystems[sys_id - 1]
                visible_layer = prev_sys._params['units'][0]['layer']
                hidden_layer = prev_sys._params['units'][1]['layer']
                mapping = (visible_layer, hidden_layer)

                dataset._initialize_transform_system(
                    system = prev_sys, mapping = mapping,
                    func = 'expect')

            # add / update dataset group 'visible'
            visible_columns = system.get('units', layer = 'visible')
            dataset.set('colfilter', visible = visible_columns)

            # initialize system parameters
            system.initialize(dataset)

            # optimize system parameter
            system.optimize(dataset, schedule)

        # reset data to initial state (before transformation)
        dataset.set('copy', **dataset_backup)

        # keep original inputs and outputs
        mapping = self.mapping()
        inputs = self._units[mapping[0]].params['id']
        outputs = self._units[mapping[-1]].params['id']

        # initialize ann with rbm optimized parameters
        units = self._params['units']
        links = self._params['links']
        central_layer_id = (len(units) - 1) / 2

        # initialize units and links until central unit layer
        for id in xrange(central_layer_id):

            # copy unit parameters
            for attrib in units[id]['init'].keys():
                # keep name and visibility of layers
                if attrib in ['layer', 'layer_id', 'visible', 'class']:
                    continue
                # keep labels of hidden layers
                if attrib == 'id' and not units[id]['visible']:
                    continue
                units[id][attrib] = units[id]['init'][attrib]
                units[-(id + 1)][attrib] = units[id][attrib]
            del units[id]['init']

            # copy link parameters and transpose numpy arrays
            for attrib in links[(id, id + 1)]['init'].keys():
                if attrib in ['source', 'target']:
                    continue
                links[(id, id + 1)][attrib] = \
                    links[(id, id + 1)]['init'][attrib]
                links[(len(units) - id - 2,
                    len(units) - id - 1)][attrib] = \
                    links[(id, id + 1)]['init'][attrib].T
            del links[(id, id + 1)]['init']

        # initialize central unit layer
        for attrib in units[central_layer_id]['init'].keys():
            # keep name and visibility of layers
            if attrib in ['id', 'layer', 'layer_id', 'visible',
                'class']: continue
            units[central_layer_id][attrib] = \
                units[central_layer_id]['init'][attrib]
        del units[central_layer_id]['init']

        # remove output units from input layer, and vice versa
        nemoa.log('cleanup unit and linkage parameter arrays')
        self._remove_units(self.mapping()[0], outputs)
        self._remove_units(self.mapping()[-1], inputs)

        return True

    def _optimize_finetuning(self, dataset, schedule, tracker):
        """Finetuning model using backpropagation of error."""


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
        else: nemoa.log('error', "unknown gradient '%s'!"
            % (cfg['algorithm']))

        return True
