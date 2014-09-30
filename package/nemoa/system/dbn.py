# -*- coding: utf-8 -*-
"""Deep Belief Network (DBN).

Deep Beliefe Network implementation for multilayer data modeling,
nonlinear data dimensionality reduction and nonlinear data analysis.

"""

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.system.ann
import numpy

class dbn(nemoa.system.ann.ann):
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
            'pretraining': True,
            'finetuning': True,
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

    def _check_network(self, network):
        return network._is_compatible_dbn()

    def _optimize_params(self, dataset, schedule, tracker):
        """Optimize system parameters."""

        # get configuration dictionary for optimization
        config = self._config['optimize']

        # optionally 'pretraining' of model
        # perform forward optimization of ann using
        # restricted boltzmann machines as subsystems
        if config['pretraining']: self._optimize_pretraining(
            dataset, schedule, tracker)

        # optionally 'finetuning' of model
        # perform backward optimization of ann
        # using backpropagation of error
        if config['finetuning']: self._optimize_finetuning(
            dataset, schedule, tracker)

        return True

    def _optimize_pretraining(self, dataset, schedule, tracker):
        """Pretraining model using restricted boltzmann machines."""

        nemoa.log('note', 'pretraining model')
        nemoa.log('set', indent = '+1')

        # configure subsystems for pretraining
        nemoa.log('configure subsystems')
        nemoa.log('set', indent = '+1')
        if not 'units' in self._params:
            nemoa.log('error', """could not configure subsystems:
                no layers have been defined!""")
            nemoa.log('set', indent = '-1')
            return False

        # create and configure subsystems
        subSystems = []
        for layerID in xrange((len(self._params['units']) - 1)  / 2):
            inUnits = self._params['units'][layerID]
            outUnits = self._params['units'][layerID + 1]
            links = self._params['links'][(layerID, layerID + 1)]

            # create configuration for network of subsystem
            if not inUnits['visible']:
                visible_units = inUnits['label']
            else:
                visible_units = self._params['units'][0]['label'] \
                    + self._params['units'][-1]['label']
            hidden_units = outUnits['label']
            network_nodes = {
                'visible': visible_units,
                'hidden': hidden_units}
            network_edges = {'visible-hidden': []}
            for v in visible_units:
                for h in hidden_units:
                    network_edges['visible-hidden'].append((v, h))
            network_config = {
                'package': 'base',
                'class': 'network',
                'name': '%s ↔ %s' \
                    % (inUnits['name'], outUnits['name']),
                'type': 'layer',
                'layer': ['visible', 'hidden'],
                'nodes': network_nodes,
                'edges': network_edges,
                'add_layer_to_node_labels': False,
                'visible': ['visible'],
                'hidden': ['hidden'],
                'label_format': 'generic:string' }

            # create network of subsystem
            network = nemoa.network.new(config = network_config)

            # create subsystem configuration
            sysType = 'visible' if inUnits['visible'] else 'hidden'
            system_config = {
                'package': \
                    self._config['params'][sysType + 'SystemModule'],
                'class': \
                    self._config['params'][sysType + 'SystemClass'],
                'name': '%s ↔ %s' \
                    % (inUnits['name'], outUnits['name'])}

            # create subsystem instance
            system = nemoa.system.new(config = system_config)

            # configure system to network
            system.configure(network = network)

            unitCount = sum([len(group) for group in system.getUnits()])
            linkCount = len(system.links())
            nemoa.log("adding subsystem: '%s' (%s units, %s links)" %\
                (system.name(), unitCount, linkCount))

            # link subsystem
            subSystems.append(system)

            # link linksparameters of subsystem
            links['init'] = system._params['links'][(0, 1)]

            # link layer parameters of subsystem
            if layerID == 0:
                inUnits['init'] = system.units['visible'].params
                outUnits['init'] = system.units['hidden'].params
                system._config['init']['ignoreUnits'] = []
                system._config['optimize']['ignoreUnits'] = []
            else:
                # do not link params from upper layer!
                # upper layer should be linked with previous subsystem
                # (higher abstraction layer)
                outUnits['init'] = system._params['units'][1]
                system._config['init']['ignoreUnits'] = ['visible']
                system._config['optimize']['ignoreUnits'] = ['visible']

        self._config['check']['subSystems'] = True
        nemoa.log('set', indent = '-1')

        # Optimize subsystems

        # create copy of dataset values (before transformation)
        datasetCopy = dataset._get()

        # optimize subsystems
        for sysID in xrange(len(subSystems)):

            # link subsystem
            system = subSystems[sysID]

            # transform dataset with previous system / fix lower stack
            if sysID > 0:
                prevSys = subSystems[sysID - 1]
                visible_layer = prevSys._params['units'][0]['name']
                hidden_layer = prevSys._params['units'][1]['name']
                mapping = (visible_layer, hidden_layer)
                dataset.transformData(algorithm = 'system',
                    system = prevSys, mapping = mapping,
                    transform = 'expect')

            # add dataset column filter 'visible'
            dataset.setColFilter('visible',
                system.getUnits(group = 'visible'))

            # initialize (free) system parameters
            system.initialize(dataset)

            # optimize (free) system parameter
            system.optimize(dataset, schedule)

        # reset data to initial state (before transformation)
        dataset._set(**datasetCopy)

        # copy and enrolle parameters of subsystems to dbn
        nemoa.log('initialize system with subsystem parameters')
        nemoa.log('set', indent = '+1')

        # keep original inputs and outputs
        mapping = self.mapping()
        inputs = self.units[mapping[0]].params['label']
        outputs = self.units[mapping[-1]].params['label']

        # expand unit parameters to all layers
        nemoa.log("""import unit and link parameters
            from subsystems (enrolling)""")
        units = self._params['units']
        links = self._params['links']

        for id in xrange((len(units) - 1)  / 2):

            # copy unit parameters
            for attrib in units[id]['init'].keys():
                # keep name and visibility of layers
                if attrib in ['name', 'visible', 'id']:
                    continue
                # keep labels of hidden layers
                if attrib == 'label' and not units[id]['visible']:
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

        # remove input units from output layer, and vice versa
        nemoa.log('cleanup unit and linkage parameter arrays')
        self._remove_units(self.mapping()[0], outputs)
        self._remove_units(self.mapping()[-1], inputs)

        nemoa.log('set', indent = '-2')
        return True

    def _optimize_finetuning(self, dataset, schedule, tracker):
        """Finetuning model using backpropagation of error."""

        nemoa.log('note', 'finetuning model')
        nemoa.log('set', indent = '+1')

        # Optimize system parameters

        algorithm = self._config['optimize']['algorithm'].lower()

        if algorithm == 'bprop': self._optimize_bprop(
            dataset, schedule, tracker)
        elif algorithm == 'rprop': self._optimize_rprop(
            dataset, schedule, tracker)
        else: nemoa.log('error', "unknown gradient '%s'!" % (algorithm))

        nemoa.log('set', indent = '-1')
        return True
