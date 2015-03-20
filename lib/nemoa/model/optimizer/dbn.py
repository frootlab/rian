# -*- coding: utf-8 -*-
"""Deep Belief Network (DBN).

Deep Beliefe Network implementation for multilayer data modeling,
nonlinear data dimensionality reduction and nonlinear data analysis.

"""

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.model.optimizer.ann

class DBN(nemoa.model.optimizer.ann.ANN):
    """Deep Belief Network (DBN) Optimizer."""

    _default = {
        'meta_algorithm': 'dbn',
        'algorithm': 'bprop',
        'updates': 10000,
        'pretraining': True,
        'finetuning': True,
        'noise_enable': False,
        'minibatch_size': 100,
        'minibatch_update_interval': 10,
        'schedule': None,
        'visible': None,
        'hidden': None,
        'adjacency_enable': False,
        'schedule_rbm.rbm': 'default',
        'schedule_rbm.grbm': 'default',
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

    @nemoa.common.decorators.attributes(
        name = 'dbn', category = 'optimization',
        netcheck = lambda net: net._is_compatible_dbn())
    def _dbn(self):
        """Optimize system parameters."""

        # (optional) pretraining of system parameters
        # perform forward optimization of ann using
        # restricted boltzmann machines as subsystems
        if self._config['pretraining']: self._dbn_pretraining()

        # (optional) finetuning of system parameters
        # perform backward optimization of ann
        # using backpropagation of error
        if self._config['finetuning']: self._dbn_finetuning()

        return True

    def _dbn_pretraining(self):
        """Pretraining model using Restricted Boltzmann Machines."""

        system = self.model.system
        config = self._config

        if not 'units' in system._params:
            return nemoa.log('error', """could not configure subsystems:
                no layers have been defined!""") or None

        # create backup of dataset (before transformation)
        dataset = self.model.dataset
        dataset_backup = dataset.get('copy')
        cid = (len(system._units) - 1) / 2
        rbmparams = { 'units': [], 'links': [] }

        for lid in xrange(cid):

            src = system._params['units'][lid]
            srcnodes = src['id'] + system._params['units'][-1]['id'] \
                if src['visible'] else src['id']
            tgt = system._params['units'][lid + 1]
            tgtnodes = tgt['id']
            links = system._params['links'][(lid, lid + 1)]
            linkclass = (src['class'], tgt['class'])
            name = '%s <-> %s' % (src['layer'], tgt['layer'])
            systype = {
                ('gauss', 'sigmoid'): 'rbm.GRBM',
                ('sigmoid', 'sigmoid'): 'rbm.RBM' }.get(
                    linkclass, None)
            if not systype:
                return nemoa.log('error', """could not create
                    rbm: unsupported pair of unit classes '%s <-> %s'"""
                    % linkclass) or None

            # create subsystem
            subsystem = nemoa.system.new(config = {
                'name': name, 'type': systype,
                'init': { 'ignore_units': ['visible'] if lid else [] }})

            # create subnetwork and configure subsystem with network
            network = nemoa.network.create('factor', name = name,
                visible_nodes = srcnodes, visible_type = src['class'],
                hidden_nodes = tgtnodes, hidden_type = tgt['class'])
            subsystem.configure(network)

            # transform dataset with previous system and initialize
            # subsystem with dataset
            if lid:
                vlayer = prevsys._params['units'][0]['layer']
                hlayer = prevsys._params['units'][1]['layer']
                dataset._initialize_transform_system(
                    system = prevsys, mapping = (vlayer, hlayer),
                    func = 'expect')
            dataset.set('colfilter', visible = srcnodes)

            # create model
            model = nemoa.model.new(
                config = {'type': 'base.Model', 'name': name},
                dataset = dataset, network = network,
                system = subsystem)

            # copy parameters from perantal subsystems hidden units
            # to current subsystems visible units
            if lid:
                dsrc = rbmparams['units'][-1]
                dtgt = model.system._params['units'][0]
                lkeep = ['id', 'layer', 'layer_id', 'visible', 'class']
                lcopy = [key for key in dsrc.keys() if not key in lkeep]
                for key in lcopy: dtgt[key] = dsrc[key]

            # reference parameters of current subsystem
            # in first layer reference visible, links and hidden
            # in other layers only reference links and hidden
            links['init'] = model.system._params['links'][(0, 1)]
            if lid == 0:
                src['init'] = model.system._units['visible'].params
            tgt['init'] = model.system._units['hidden'].params

            # optimize model
            schedule = self._get_schedule(self._config.get(
                'schedule_%s' % systype.lower(), 'default'))
            if systype in schedule: model.optimize(schedule[systype])
            else: model.optimize()

            if not lid:
                rbmparams['units'].append(
                    model.system.get('layer', 'visible'))
            rbmparams['links'].append(
                model.system._params['links'][(0, 1)])
            rbmparams['units'].append(
                model.system.get('layer', 'hidden'))

            prevsys = model.system

        # reset data to initial state (before transformation)
        dataset.set('copy', **dataset_backup)

        # keep original inputs and outputs
        mapping = system._get_mapping()
        inputs = system._units[mapping[0]].params['id']
        outputs = system._units[mapping[-1]].params['id']

        # initialize ann with rbm optimized parameters
        units = system._params['units']
        links = system._params['links']
        central_lid = (len(units) - 1) / 2

        # initialize units and links until central unit layer
        for id in xrange(central_lid):

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
        for attrib in units[central_lid]['init'].keys():
            # keep name and visibility of layers
            if attrib in ['id', 'layer', 'layer_id', 'visible',
                'class']: continue
            units[central_lid][attrib] = \
                units[central_lid]['init'][attrib]
        del units[central_lid]['init']

        # remove output units from input layer, and vice versa
        nemoa.log('cleanup unit and linkage parameter arrays.')
        system._remove_units(mapping[0], outputs)
        system._remove_units(mapping[-1], inputs)

        return True

    def _dbn_finetuning(self):
        """Finetuning model using backpropagation of error."""

        # optimize system parameters
        algorithm = self._config['algorithm']
        optimizer = self._get_algorithm(algorithm,
            category = 'optimization')
        optimizer['reference']()

        return True
