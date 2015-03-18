# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import numpy
import time

class Optimizer:

    _config = None # linked nemoa system optimization configuration
    _state = {}    # dictionary for tracking variables
    _store = {}    # dictionary for storage of optimization parameters

    def __init__(self, model = None, *args, **kwargs):
        """Configure tracker to given nemoa system instance."""
        if model: self._set_model(model)

    def get(self, key, *args, **kwargs):

        ## algorithms
        #if key == 'algorithm':
            #return self._get_algorithm(*args, **kwargs)
        #if key == 'algorithms': return self._get_algorithms(
            #attribute = 'about', *args, **kwargs)

        if key == 'data': return self._get_data(*args, **kwargs)
        if key == 'epoch': return self._get_epoch()
        if key == 'progress': return self._get_progress()
        if key == 'model': return self._get_model()

        if not key in self._state.keys(): return False
        return self._state[key]

    #def _get_algorithms(self, category = None, attribute = None):
        #"""Get algorithms provided by optimizer."""

        ## get unstructured dictionary of all algorithms by prefix
        #unstructured = nemoa.common.module.getmethods(self,
            #prefix = '_algorithm_')

        ## filter algorithms by supported keys and given category
        #for ukey, udata in unstructured.items():
            #if not isinstance(udata, dict):
                #del unstructured[ukey]
                #continue
            #if attribute and not attribute in udata.keys():
                #del unstructured[ukey]
                #continue
            #if not 'name' in udata.keys():
                #del unstructured[ukey]
                #continue
            #if not 'category' in udata.keys():
                #del unstructured[ukey]
                #continue
            #if category and not udata['category'] == category:
                #del unstructured[ukey]

        ## create flat structure id category is given
        #structured = {}
        #if category:
            #for ukey, udata in unstructured.iteritems():
                #if attribute: structured[udata['name']] = \
                    #udata[attribute]
                #else: structured[udata['name']] = udata
            #return structured

        ## create tree structure if category is not given
        #categories = {
            #('system', 'evaluation'): None,
            #('system', 'units', 'evaluation'): 'units',
            #('system', 'links', 'evaluation'): 'links',
            #('system', 'relation', 'evaluation'): 'relation' }
        #for ukey, udata in unstructured.iteritems():
            #if not udata['category'] in categories.keys(): continue
            #ckey = categories[udata['category']]
            #if ckey == None:
                #if attribute: structured[udata['name']] = \
                    #udata[attribute]
                #else: structured[udata['name']] = udata
            #else:
                #if not ckey in structured.keys(): structured[ckey] = {}
                #if attribute: structured[ckey][udata['name']] = \
                    #udata[attribute]
                #else: structured[ckey][udata['name']] = udata

        #return structured

    #def _get_algorithm(self, key, *args, **kwargs):
        #"""Get algorithm provided by optimizer."""
        #return self._get_algorithms(*args, **kwargs).get(key, None)

    def _get_data(self, key, *args, **kwargs):
        """Get data for training or evaluation.

        Args:
            key (string): purpose of data: 'training' or 'evaluation'

        Returns:
            Tuple of numpy arrays containing data for training or
            evaluation.

        """

        if key == 'evaluation':
            return self._get_evaluation_data(*args, **kwargs)
        if key == 'training':
            return self._get_data_training(*args, **kwargs)

        return nemoa.log('warning', "unknown key '%s'" % key) or None

    def _get_evaluation_data(self):
        """Get evaluation data.

        Returns:
            Tuple of numpy arrays containing evaluation data or None
            if evaluation data could not be retrieved from dataset.

        """

        data = self._state.get('evaluation_data', None)

        # get evaluation data from dataset
        if not data:
            system = self.model.system
            dataset = self.model.dataset
            mapping = system._get_mapping()
            cols = (mapping[0], mapping[-1])
            data = dataset.get('data', cols = cols)
            if data: self._state['evaluation_data'] = data

        return data or None

    def _get_evaluation_algorithm(self):
        config = self.model.system._config['optimize']
        name = config['tracker_eval_function']
        return self.model.system.get('algorithm', name)

    def _get_evaluation_value(self):
        data = self._get_evaluation_data()
        func = self._get_evaluation_algorithm()['name']
        return self.model.system.evaluate(data = data, func = func)

    def _get_data_training(self, *args, **kwargs):
        """Get training data.

        Returns:
            Tuple of numpy arrays containing training data or None
            if training data could not be retrieved from dataset.

        """

        data = self._state.get('training_data', None)
        epoch = self._get_epoch()
        interval = self._get_schedule('minibatch_update_interval')

        # get training data from dataset
        if not data or epoch % interval == 0:
            system = self.model.system
            dataset = self.model.dataset
            mapping = system._get_mapping()
            cols = (mapping[0], mapping[-1])
            schedule = system._config['optimize']
            size = schedule.get('minibatch_size', 0)
            if schedule.get('den_corr_enable', None):
                noisetype = schedule.get('den_corr_type', None)
                noisefactor = schedule.get('den_corr_factor', 0.)
                noise = (noisetype, noisefactor)
            else:
                noise = (None, 0.)
            data = dataset.get('data', cols = cols,
                size = size, noise = noise)
            if data: self._state['training_data'] = data

        return data or None

    def _get_epoch(self):
        """Get current training epoch.

        Returns:
            Integer containing current training epoch.

        """

        return self._state.get('epoch', 0)

    def _get_progress(self):
        """Get current progress in percentage.

        Returns:
            Float containing current progress in percentage.

        """

        return float(self._state['epoch']) \
            / float(self._state['schedule']['updates'])

    def _get_model(self):
        """Get model instance."""
        return self._state.get('model', None)

    def _get_schedule(self, key):
        """Get value from current training schedule."""
        return self.model.system._config['optimize'].get(
            key, None)

    def set(self, key, *args, **kwargs):

        if key == 'model': return self._set_model(*args, **kwargs)

        found = True
        for key in kwargs.keys():
            if key in self._state.keys():
                self._state[key] = kwargs[key]
            else: found = False

        return found

    def _set_model(self, model):
        """Set model."""

        if not nemoa.common.type.ismodel(model):
            return nemoa.log('warning',
                'could not configure optimizer: model is not valid!')

        self.model = model

        # update time and schedule
        now = time.time()
        schedule = model.system._config['optimize']
        self._state = {
            'epoch': 0,
            'evaluation_data': None,
            'schedule': model.system._config['optimize'],
            'training_data': None,
            'optimum': {},
            'continue': True,
            'obj_enable': schedule['tracker_obj_tracking_enable'],
            'obj_init_wait': schedule['tracker_obj_init_wait'],
            'obj_values': None,
            'obj_opt_value': None,
            'key_events': True,
            'key_events_started': False,
            'eval_enable': schedule['tracker_eval_enable'],
            'eval_prev_time': now,
            'eval_values': None,
            'estim_enable': schedule['tracker_estimate_time'],
            'estim_started': False,
            'estim_start_time': now }

        # update evaluation data
        self._get_evaluation_data()

        return True

    def read(self, key, id = -1):
        if not key in self._store.keys():
            self._store[key] = []
        elif len(self._store[key]) >= abs(id):
            return self._store[key][id]
        return {}

    def write(self, key, id = -1, append = False, **kwargs):
        if not key in self._store.keys():
            self._store[key] = []
        if len(self._store[key]) == (abs(id) - 1) or append == True:
            self._store[key].append(kwargs)
            return True
        if len(self._store[key]) < id: return nemoa.log('error',
            'could not write to store, wrong index!')
        self._store[key][id] = kwargs
        return True

    def _update_time_estimation(self):
        if not self._state['estim_enable']: return True

        if not self._state['estim_started']:
            nemoa.log("""estimating time for calculation of %i
                updates.""" % (self._state['schedule']['updates']))
            self._state['estim_started'] = True
            self._state['estim_start_time'] = time.time()
            return True

        now = time.time()
        runtime = now - self._state['estim_start_time']
        if runtime > self._state['schedule']['tracker_estimate_time_wait']:
            estim = (runtime / (self._state['epoch'] + 1)
                * self._state['schedule']['updates'])
            estim_str = time.strftime('%H:%M',
                time.localtime(now + estim))
            nemoa.log('note', 'estimation: %ds (finishing time: %s)'
                % (estim, estim_str))
            self._state['estim_enable'] = False
            return True

        return True

    def update(self):
        """Update epoch and check termination criterions."""

        self._state['epoch'] += 1
        if self._state['epoch'] == self._state['schedule']['updates']:
            self._state['continue'] = False

        if self._state['key_events']: self._update_keypress()
        if self._state['estim_enable']: self._update_time_estimation()
        if self._state['obj_enable']: self._update_objective_function()
        if self._state['eval_enable']: self._update_evaluation()

        if not self._state['continue']:
            nemoa.common.console.stopgetch()

        return self._state['continue']

    def _update_keypress(self):
        """Check Keyboard."""
        if not self._state['key_events_started']:
            nemoa.log('note', """press 'q' if you want to abort
                the optimization""")
            self._state['key_events_started'] = True

        char = nemoa.common.console.getch()
        if isinstance(char, str):
            if char == 'q':
                nemoa.log('note', '... aborting optimization')
                self._state['continue'] = False

        return True

    def _update_objective_function(self):
        """Calculate objective function of system."""

        # check 'continue' flag
        if self._state['continue']:

            # check update interval
            if not not (self._state['epoch'] \
                % self._state['schedule']['tracker_obj_update_interval'] == 0):
                return True

        # calculate objective function and add value to array
        func = self._state['schedule']['tracker_obj_function']
        data = self._get_evaluation_data()
        value = self.model.system.evaluate(
            data = data, func = func)
        progr = self._get_progress()
        if not isinstance(self._state['obj_values'], numpy.ndarray):
            self._state['obj_values'] = numpy.array([[progr, value]])
        else: self._state['obj_values'] = \
            numpy.vstack((self._state['obj_values'], \
            numpy.array([[progr, value]])))

        # (optional) check for new optimum
        if self._state['schedule']['tracker_obj_keep_optimum']:

            # init optimum with first value
            if self._state['obj_opt_value'] == None:
                self._state['obj_opt_value'] = value
                self._state['optimum'] = \
                    {'params': self.model.system.get(
                    'copy', 'params')}
                return True

            # allways check last optimum
            if self._state['continue'] \
                and progr < self._state['schedule']['tracker_obj_init_wait']:
                return True

            type_of_optimum = self.model.system.get(
                'algorithm', func,
                category = ('system', 'evaluation'),
                attribute = 'optimum')
            current_optimum = self._state['obj_opt_value']

            if type_of_optimum == 'min' and value < current_optimum:
                new_optimum = True
            elif type_of_optimum == 'max' and value > current_optimum:
                new_optimum = True
            else:
                new_optimum = False

            if new_optimum:
                self._state['obj_opt_value'] = value
                self._state['optimum'] = { 'params':
                    self.model.system.get('copy', 'params') }

            # set system parameters to optimum on last update
            if not self._state['continue']:
                return self.model.system.set('copy',
                    **self._state['optimum'])

        return True

    def _update_evaluation(self):
        """Calculate evaluation function of system."""

        cfg = self.model.system._config['optimize']
        now = time.time()

        if not self._state['continue']:
            func = self._get_evaluation_algorithm()
            value = self._get_evaluation_value()
            self._state['eval_enable'] = False
            return nemoa.log('note', 'found optimum with: %s = %s' % (
                func['name'], func['formater'](value)))

        if ((now - self._state['eval_prev_time']) \
            > cfg['tracker_eval_time_interval']):
            func = self._get_evaluation_algorithm()
            value = self._get_evaluation_value()
            progress = self._get_progress()

            # update time of last evaluation
            self._state['eval_prev_time'] = now

            # add evaluation to array
            if not isinstance(self._state['eval_values'],
                numpy.ndarray):
                self._state['eval_values'] = \
                    numpy.array([[progress, value]])
            else:
                self._state['eval_values'] = \
                    numpy.vstack((self._state['eval_values'], \
                    numpy.array([[progress, value]])))

            return nemoa.log('note', 'finished %.1f%%: %s = %s' % (
                progress, func['name'], func['formater'](value)))

        return False


    #@nemoa.common.decorators.attributes(
        #name     = 'dbn',
        #category = ('system', 'optimization'),
        #netcheck = lambda net: net._is_compatible_dbn()
    #)
    #def _algorithm_dbn(self, schedule):
        #"""Optimize system parameters."""

        ## get configuration dictionary for optimization
        #config = self.model.system._config['optimize']

        ## (optional) pretraining of system parameters
        ## perform forward optimization of ann using
        ## restricted boltzmann machines as subsystems
        #if config['pretraining']:
            #self._algorithm_dbn_pretraining(schedule)

        ## (optional) finetuning of system parameters
        ## perform backward optimization of ann
        ## using backpropagation of error
        #if config['finetuning']:
            #self._algorithm_dbn_finetuning(schedule)

        #return True

    #def _algorithm_dbn_pretraining(self, schedule):
        #"""Pretraining model using Restricted Boltzmann Machines."""

        #config = self.model.system._config
        #params = self.model.system._params

        #if not 'units' in params:
            #return nemoa.log('error', """could not configure subsystems:
                #no layers have been defined!""") or None

        ## create backup of dataset (before transformation)
        #dataset_backup = dataset.get('copy')

        #cid = (len(self._units) - 1) / 2
        #rbmparams = { 'units': [], 'links': [] }

        #import copy
        #params = copy.deepcopy(self._params)

        #for lid in xrange(cid):

            #src = self._params['units'][lid]
            #srcnodes = src['id'] + self._params['units'][-1]['id'] \
                #if src['visible'] else src['id']
            #tgt = self._params['units'][lid + 1]
            #tgtnodes = tgt['id']
            #links = self._params['links'][(lid, lid + 1)]
            #linkclass = (src['class'], tgt['class'])
            #name = '%s <-> %s' % (src['layer'], tgt['layer'])
            #systype = {
                #('gauss', 'sigmoid'): 'rbm.GRBM',
                #('sigmoid', 'sigmoid'): 'rbm.RBM' }.get(
                    #linkclass, None)
            #if not systype:
                #return nemoa.log('error', """could not create
                    #rbm: unsupported pair of unit classes '%s <-> %s'"""
                    #% linkclass) or None

            ## create subsystem
            #system = nemoa.system.new(config = {
                #'name': name, 'type': systype,
                #'init': { 'ignore_units': ['visible'] if lid else [] }})

            ## create subnetwork and configure subsystem with network
            #network = nemoa.network.create('factor', name = name,
                #visible_nodes = srcnodes, visible_type = src['class'],
                #hidden_nodes = tgtnodes, hidden_type = tgt['class'])
            #system.configure(network)

            ## transform dataset with previous system and initialize
            ## subsystem with dataset
            #if lid:
                #vlayer = prevsys._params['units'][0]['layer']
                #hlayer = prevsys._params['units'][1]['layer']
                #dataset._initialize_transform_system(
                    #system = prevsys, mapping = (vlayer, hlayer),
                    #func = 'expect')
            #dataset.set('colfilter', visible = srcnodes)
            #system.initialize(dataset)

            ## copy parameters from perantal subsystems hidden units
            ## to current subsystems visible units
            #if lid:
                #dsrc = rbmparams['units'][-1]
                #dtgt = system._params['units'][0]
                #lkeep = ['id', 'layer', 'layer_id', 'visible', 'class']
                #lcopy = [key for key in dsrc.keys() if not key in lkeep]
                #for key in lcopy: dtgt[key] = dsrc[key]

            ## reference parameters of current subsystem
            ## in first layer reference visible, links and hidden
            ## in other layers only reference links and hidden
            #links['init'] = system._params['links'][(0, 1)]
            #if lid == 0: src['init'] = system._units['visible'].params
            #tgt['init'] = system._units['hidden'].params

            ## update current optimization schedule from given schedule
            #ddef = system._default['optimize']
            #dcur = system._config['optimize']
            #darg = schedule[system.type]
            #config = nemoa.common.dict.merge(dcur, ddef)
            #config = nemoa.common.dict.merge(darg, config)
            #config['ignore_units'] = ['visible'] if lid else []
            #system._config['optimize'] = config

            ## optimize current subsystem
            #algorithm = system._config['optimize']['algorithm']
            #optimizer = system._get_algorithm(algorithm,
                #category = ('system', 'optimization'))
            #optimizer['reference'](dataset, schedule, tracker)

            #if not lid:
                #rbmparams['units'].append(
                    #system.get('layer', 'visible'))
            #rbmparams['links'].append(system._params['links'][(0, 1)])
            #rbmparams['units'].append(system.get('layer', 'hidden'))

            #prevsys = system

        ## reset data to initial state (before transformation)
        #dataset.set('copy', **dataset_backup)

        ## keep original inputs and outputs
        #mapping = self._get_mapping()
        #inputs = self._units[mapping[0]].params['id']
        #outputs = self._units[mapping[-1]].params['id']

        ## initialize ann with rbm optimized parameters
        #units = self._params['units']
        #links = self._params['links']
        #central_lid = (len(units) - 1) / 2

        ## initialize units and links until central unit layer
        #for id in xrange(central_lid):

            ## copy unit parameters
            #for attrib in units[id]['init'].keys():
                ## keep name and visibility of layers
                #if attrib in ['layer', 'layer_id', 'visible', 'class']:
                    #continue
                ## keep labels of hidden layers
                #if attrib == 'id' and not units[id]['visible']:
                    #continue
                #units[id][attrib] = units[id]['init'][attrib]
                #units[-(id + 1)][attrib] = units[id][attrib]
            #del units[id]['init']

            ## copy link parameters and transpose numpy arrays
            #for attrib in links[(id, id + 1)]['init'].keys():
                #if attrib in ['source', 'target']:
                    #continue
                #links[(id, id + 1)][attrib] = \
                    #links[(id, id + 1)]['init'][attrib]
                #links[(len(units) - id - 2,
                    #len(units) - id - 1)][attrib] = \
                    #links[(id, id + 1)]['init'][attrib].T
            #del links[(id, id + 1)]['init']

        ## initialize central unit layer
        #for attrib in units[central_lid]['init'].keys():
            ## keep name and visibility of layers
            #if attrib in ['id', 'layer', 'layer_id', 'visible',
                #'class']: continue
            #units[central_lid][attrib] = \
                #units[central_lid]['init'][attrib]
        #del units[central_lid]['init']

        ## remove output units from input layer, and vice versa
        #nemoa.log('cleanup unit and linkage parameter arrays.')
        #mapping = self._get_mapping()
        #self._remove_units(mapping[0], outputs)
        #self._remove_units(mapping[-1], inputs)

        #return True

    #def _algorithm_dbn_finetuning(self, dataset, schedule, tracker):
        #"""Finetuning model using backpropagation of error."""

        ## optimize system parameters
        #force = self._config['optimize']['meta_algorithm']
        #self._config['optimize']['meta_algorithm'] = None
        #algorithm = self._config['optimize']['algorithm']
        #optimizer = self._get_algorithm(algorithm,
            #category = ('system', 'optimization'))
        #optimizer['reference'](dataset, schedule, tracker)
        #self._config['optimize']['meta_algorithm'] = force

        #return True


