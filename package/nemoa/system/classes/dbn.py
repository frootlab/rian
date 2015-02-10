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
            'hidden_class': 'sigmoid',
            'visible_system_type': 'rbm.GRBM',
            'hidden_system_type': 'rbm.RBM' },
        'init': {
            'check_dataset': False,
            'ignore_units': [],
            'w_sigma': 0.5 },
        'optimize': {
            'ignore_units': [],
            'meta_algorithm': 'dbn',
            'pretraining': True,
            'finetuning': True,
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

    @nemoa.common.decorators.attributes(
        name     = 'dbn',
        category = ('system', 'optimization'),
        netcheck = lambda net: net._is_compatible_dbn()
    )
    def _algorithm_dbn(self, dataset, schedule, tracker):
        """Optimize system parameters."""

        # get configuration dictionary for optimization
        config = self._config['optimize']

        # (optional) pretraining of system parameters
        # perform forward optimization of ann using
        # restricted boltzmann machines as subsystems
        if config['pretraining']:
            self._algorithm_dbn_pretraining(dataset, schedule, tracker)

        # (optional) finetuning of system parameters
        # perform backward optimization of ann
        # using backpropagation of error
        if config['finetuning']:
            self._algorithm_dbn_finetuning(dataset, schedule, tracker)

        return True

    def _algorithm_dbn_pretraining(self, dataset, schedule, tracker):
        """Pretraining model using Restricted Boltzmann Machines."""

        def _copy_attributes(from_dict, to_dict):
            for attrib in from_dict.keys():

                # keep name and visibility of layers
                if attrib in ['id', 'layer', 'layer_id', 'visible',
                    'class']:
                    continue

                to_dict[attrib] = from_dict[attrib]
            return True

        if not 'units' in self._params:
            return nemoa.log('error', """could not configure subsystems:
                no layers have been defined!""")

        # create and configure subsystems
        subsystems = []

        # create backup of dataset values (before transformation)
        dataset_backup = dataset.get('copy')

        all_visible = self._params['units'][0]['id'] \
            + self._params['units'][-1]['id']

        cid = (len(self._units) - 1) / 2

        rbmparams = { 'units': [], 'links': [] }
        params = self._params.copy()

        for lid in xrange(cid):

            src = self._params['units'][lid]
            tgt = self._params['units'][lid + 1]
            links = self._params['links'][(lid, lid + 1)]

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

            # add system to list of subsystems
            subsystems.append(system)

            # link rbm parameters
            # in first layer link visible, links and hidden
            # in other layers only link links and hidden
            links['init'] = system._params['links'][(0, 1)]
            if lid == 0: src['init'] = system._units['visible'].params
            tgt['init'] = system._units['hidden'].params

            if lid: ignore_units = ['visible']
            else: ignore_units = []
            system._config['init']['ignore_units'] = ignore_units
            system._config['optimize']['ignore_units'] = ignore_units

            # transform dataset with previous system / fix lower stack
            if lid:
                prev_sys = subsystems[lid - 1]
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

            if lid:
                _copy_attributes(rbmparams['units'][-1],
                    system._params['units'][0])

            # optimize system parameter
            system.optimize(dataset, schedule)

            if not lid:
                rbmparams['units'].append(
                    system.get('layer', 'visible'))
            rbmparams['links'].append(system._params['links'][(0, 1)])
            rbmparams['units'].append(system.get('layer', 'hidden'))

        # reset data to initial state (before transformation)
        dataset.set('copy', **dataset_backup)

        # keep original inputs and outputs
        mapping = self._get_mapping()
        inputs = self._units[mapping[0]].params['id']
        outputs = self._units[mapping[-1]].params['id']

        # initialize ann with rbm optimized parameters
        units = self._params['units']
        links = self._params['links']
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
        nemoa.log('cleanup unit and linkage parameter arrays')
        mapping = self._get_mapping()
        self._remove_units(mapping[0], outputs)
        self._remove_units(mapping[-1], inputs)

        return True

    def _algorithm_dbn_finetuning(self, dataset, schedule, tracker):
        """Finetuning model using backpropagation of error."""

        # optimize system parameters
        force = self._config['optimize']['meta_algorithm']
        self._config['optimize']['meta_algorithm'] = None
        self.optimize(dataset, schedule)
        self._config['optimize']['meta_algorithm'] = force

        return True
