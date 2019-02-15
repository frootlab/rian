# -*- coding: utf-8 -*-
"""Deep Belief Network (DBN).

Deep Beliefe Network implementation for multilayer data modeling,
nonlinear data dimensionality reduction and nonlinear data analysis.

"""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

from flab.base import catalog
from nemoa.core import ui
import nemoa.model.morphisms.ann

class DBN(nemoa.model.morphisms.ann.ANN):
    """Deep Belief Network (DBN) Optimizer."""

    _default = {
        'algorithm': 'dbn',
        'pretraining': True,
        'finetuning': True,
        'schedule': None,
        'visible': None,
        'hidden': None,
        'schedule_rbm.rbm': 'default',
        'schedule_rbm.grbm': 'default' }

    @catalog.custom(
        name = 'dbn',
        longname = 'deep belief network optimization',
        category = 'optimization',
        type = 'metaalgorithm',
        syscheck = lambda net: net._is_compatible_dbn())
    def _dbn(self):
        """Deep belief network optimization."""

        retval = True

        if retval and self._config['pretraining']:
            retval &= self.optimize(algorithm = 'pretraining')
        if retval and self._config['finetuning']:
            retval &= self.optimize(algorithm = 'finetuning')

        return retval

    @catalog.custom(
        name     = 'pretraining',
        longname = 'deep belief network pretraining',
        category = 'optimization',
        type     = 'metaalgorithm',
        syscheck = None)
    def _dbn_pretraining(self):
        """Deep belief network pretraining.

        Deep belief network pretraining is a meta algorithm that wraps
        unittype specific optimization schedules, intended to perform
        system local optimization from outer layers to inner layers.
        The default optimization schedules uses restricted boltzmann
        machines and contrastive divergency optimization.

        """

        system = self.model.system
        config = self._config

        if 'units' not in system._params:
            raise ValueError("""could not configure subsystems:
                no layers have been defined!""") or None

        # create backup of dataset (before transformation)
        dataset = self.model.dataset
        dataset_backup = dataset.get('copy')

        # create layerwise subsystems for RBM pretraining
        cid = int((len(system._units) - 1) / 2)
        rbmparams = { 'units': [], 'links': [] }
        for lid in range(cid):

            src = system._params['units'][lid]
            srcnodes = src['id'] + system._params['units'][-1]['id'] \
                if src['visible'] else src['id']
            tgt = system._params['units'][lid + 1]
            tgtnodes = tgt['id']
            cpy = system._params['units'][-(lid + 1)]
            links = system._params['links'][(lid, lid + 1)]
            linkclass = (src['class'], tgt['class'])
            name = '%s <-> %s <-> %s' % (src['layer'], tgt['layer'],
                cpy['layer'])
            systype = {
                ('gauss', 'sigmoid'): 'rbm.GRBM',
                ('sigmoid', 'sigmoid'): 'rbm.RBM' }.get(
                    linkclass, None)
            if not systype:
                raise ValueError("""could not create
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
                lcopy = [key for key in list(dsrc.keys()) if not key in lkeep]
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

            if systype in schedule:
                model.optimize(schedule[systype])
            else:
                model.optimize()

            if not lid: rbmparams['units'].append(
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

        # initialize units and links until central unit layer
        cid = int((len(units) - 1) / 2)
        for id in range(cid):

            # copy unit parameters
            for attrib in list(units[id]['init'].keys()):
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
            for attrib in list(links[(id, id + 1)]['init'].keys()):
                if attrib in ['source', 'target']:
                    continue
                links[(id, id + 1)][attrib] = \
                    links[(id, id + 1)]['init'][attrib]
                links[(len(units) - id - 2,
                    len(units) - id - 1)][attrib] = \
                    links[(id, id + 1)]['init'][attrib].T
            del links[(id, id + 1)]['init']

        # initialize central unit layer
        for attrib in list(units[cid]['init'].keys()):
            # keep name and visibility of layers
            if attrib in ['id', 'layer', 'layer_id', 'visible',
                'class']: continue
            units[cid][attrib] = \
                units[cid]['init'][attrib]
        del units[cid]['init']

        # remove output units from input layer, and vice versa
        ui.info('cleanup unit and linkage parameter arrays.')
        system._remove_units(mapping[0], outputs)
        system._remove_units(mapping[-1], inputs)

        return True

    @catalog.custom(
        name     = 'finetuning',
        longname = 'deep belief network finetuning',
        category = 'optimization',
        type     = 'metaalgorithm',
        syscheck = None)
    def _dbn_finetuning(self):
        """Deep belief network finetuning.

        Deep belief network Finetuning is a meta algorithm that wraps an
        arbitrary optimization schedule, intended to perform system
        global optimization. The default optimization schedule uses
        backpropagation of error.

        """

        schedulename = 'default'
        sysname = self._config.get('finetuning', 'ann.ANN')
        schedule = self._get_schedule('default') or {}
        config = schedule.get(sysname, {})
        algorithm = config.get('algorithm', None)

        if algorithm == 'dbn':
            raise Warning("""could not finetune model:
                recursion detected.""")

        return self.optimize(config = config)
