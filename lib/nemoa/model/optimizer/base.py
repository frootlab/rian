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

        # algorithms
        if key == 'algorithm':
            return self._get_algorithm(*args, **kwargs)
        if key == 'algorithms': return self._get_algorithms(
            attribute = 'about', *args, **kwargs)

        if key == 'data': return self._get_data(*args, **kwargs)
        if key == 'epoch': return self._get_epoch()
        if key == 'progress': return self._get_progress()
        if key == 'model': return self._get_model()

        if not key in self._state.keys(): return False
        return self._state[key]

    def _get_algorithms(self, category = None, attribute = None):
        """Get algorithms provided by optimizer."""

        # get unstructured dictionary of all algorithms by prefix
        unstructured = nemoa.common.module.getmethods(self,
            prefix = '_')

        # filter algorithms by supported keys and given category
        for ukey, udata in unstructured.items():
            if not isinstance(udata, dict):
                del unstructured[ukey]
                continue
            if attribute and not attribute in udata.keys():
                del unstructured[ukey]
                continue
            if not 'name' in udata.keys():
                del unstructured[ukey]
                continue
            if not 'category' in udata.keys():
                del unstructured[ukey]
                continue
            if category and not udata['category'] == category:
                del unstructured[ukey]

        # create flat structure id category is given
        structured = {}
        if category:
            for ukey, udata in unstructured.iteritems():
                if attribute: structured[udata['name']] = \
                    udata[attribute]
                else: structured[udata['name']] = udata
            return structured

        # create tree structure if category is not given
        categories = {'optimization': None }
        for ukey, udata in unstructured.iteritems():
            if not udata['category'] in categories.keys(): continue
            ckey = categories[udata['category']]
            if ckey == None:
                if attribute: structured[udata['name']] = \
                    udata[attribute]
                else: structured[udata['name']] = udata
            else:
                if not ckey in structured.keys(): structured[ckey] = {}
                if attribute: structured[ckey][udata['name']] = \
                    udata[attribute]
                else: structured[ckey][udata['name']] = udata

        return structured

    def _get_algorithm(self, key, *args, **kwargs):
        """Get algorithm provided by optimizer."""
        return self._get_algorithms(*args, **kwargs).get(key, None)

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
        """ """

        name = self._config['tracker_eval_function']

        return self.model.system.get('algorithm', name)

    def _get_evaluation_value(self):
        """ """

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
        interval = self._config.get('minibatch_update_interval', 1)

        # get training data from dataset
        if not data or epoch % interval == 0:
            system = self.model.system
            dataset = self.model.dataset
            mapping = system._get_mapping()
            cols = (mapping[0], mapping[-1])
            size = self._config.get('minibatch_size', 0)
            if 'noise_enable' in self._config:
                ntype = self._config.get('noise_type', None)
                nfactor = self._config.get('noise_factor', 0.)
                noise = (ntype, nfactor)
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

    def _get_estimate_time(self):

        import time

        now = time.time()
        runtime = now - self._state['estim_start_time']
        estim = (runtime / (self._state['epoch'] + 1)
            * self._config['updates'])
        estim_str = time.strftime('%H:%M',
            time.localtime(now + estim))

        return estim_str


    def _get_progress(self):
        """Get current optimization progress in percentage.

        Returns:
            Float containing current progress in percentage.

        """

        return float(self._state['epoch']) \
            / float(self._config['updates'])

    def _get_model(self):
        """Get model instance."""
        return self._state.get('model', None)

    def _get_compatibility(self, model):
        """Get compatibility of optimizer to given model instance.

        Args:
            model: nemoa model instance

        Returns:
            True if optimizer is compatible to given model, else False.

        """

        # test type of model instance and subclasses
        if not nemoa.common.type.ismodel(model): return False
        if not nemoa.common.type.isdataset(model.dataset): return False
        if not nemoa.common.type.isnetwork(model.network): return False
        if not nemoa.common.type.issystem(model.system): return False

        # check dataset
        if (not 'check_dataset' in model.system._default['init']
            or model.system._default['init']['check_dataset'] == True) \
            and not model.system._check_dataset(model.dataset):
            return None

        return True

    def _get_schedule(self, key):
        """Get schedule by name."""

        if not 'schedules' in self.model.system._config: return {}

        return self.model.system._config['schedules'].get(key, {})

    def optimize(self, config = None, *args, **kwargs):
        """ """

        if not self._set_config(config): return None
        if not self._set_state_reset(): return None

        # get name of optimization algorithm
        name = self._config.get('algorithm', None)
        if not name:
            return nemoa.log('error', """could not optimize '%s'
                (%s): no optimization algorithm has been set."""
                % (self.model.name, self.model.system.type)) or None

        # get instance of optimization algorithm
        algorithm = self._get_algorithm(name, category = 'optimization')
        if not algorithm:
            return nemoa.log('error', """could not optimize '%s':
                unsupported optimization algorithm '%s'."""
                % (self.model.name, name)) or None

        # start optimization
        if algorithm.get('type', None) == 'algorithm':
            nemoa.log('note', "optimize '%s' (%s) using %s."
                % (self.model.name, self.model.system.type, name))

            # start key events
            if not self._state['key_events_started']:
                nemoa.log('note', """press 'h' for help.""")
                self._state['key_events_started'] = True
                nemoa.set('shell', 'buffmode', 'key')

        # 2Do retval, try / except etc.
        optimizer = algorithm.get('reference', None)
        if not optimizer: return None

        retval = optimizer()
        retval &= self.model.network.initialize(self.model.system)

        return retval

    def set(self, key, *args, **kwargs):
        """ """

        if key == 'model': return self._set_model(*args, **kwargs)
        if key == 'config': return self._set_config(*args, **kwargs)
        if key == 'state': return self._set_state(*args, **kwargs)

        return nemoa.log('warning', "unknown key '%s'" % key) or None

    def _set_config(self, config = None):
        """Set optimizer configuration from dictionary."""

        if not isinstance(config, dict):
            if not config: key = 'default'
            elif isinstance(config, basestring): key = config
            else:
                return nemoa.log('warning', """could not configure
                    optimization: invalid configuration.""") or None
            if not self.model:
                return nemoa.log('warning', """could not configure
                    optimization: no model given.""") or None
            system = self.model.system
            schedules = system._config.get('schedules', {})
            config = schedules.get(key, {}).get(system.type, {})

        self._config = nemoa.common.dict.merge(config, self._default)

        return True

    def _set_model(self, model):
        """Set model."""

        if not self._get_compatibility(model):
            return nemoa.log('warning', """Could not initialize
                optimizer to model: optimizer is not compatible to
                model.""") or None

        # update time and config
        self.model = model

        # initialize evaluation data
        self._get_evaluation_data()

        return True

    def _set_state(self, key, *args, **kwargs):

        if key == 'reset': return self._set_state_reset()

        return self._state.get(key, nemoa.log('warning', """unknown
            attribute '%s'.""" % key) or None)

    def _set_state_reset(self):
        """ """

        now = time.time()
        self._state = {
            'epoch': 0,
            'evaluation_data': None,
            'training_data': None,
            'optimum': {},
            'continue': True,
            'obj_values': None,
            'obj_opt_value': None,
            'key_events': True,
            'key_events_started': False,
            'eval_prev_time': now,
            'eval_values': None,
            'estim_started': False,
            'estim_start_time': now }

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

    #def _update_time_estimation(self):
        #""" """
        #if not self._config['tracker_estimate_time']: return True

        #if not self._state['estim_started']:
            #nemoa.log("""estimating time for calculation of %i
                #updates.""" % (self._config['updates']))
            #self._state['estim_started'] = True
            #self._state['estim_start_time'] = time.time()
            #return True

        #now = time.time()
        #runtime = now - self._state['estim_start_time']
        #if runtime > self._config['tracker_estimate_time_wait']:
            #estim = (runtime / (self._state['epoch'] + 1)
                #* self._config['updates'])
            #estim_str = time.strftime('%H:%M',
                #time.localtime(now + estim))
            #nemoa.log('note', 'estimation: %ds (finishing time: %s)'
                #% (estim, estim_str))
            #self._config['tracker_estimate_time'] = False
            #return True

        #return True

    def update(self):
        """Update epoch and check termination criterions."""

        self._state['epoch'] += 1
        if self._state['epoch'] == self._config['updates']:
            self._state['continue'] = False

        if self._state['key_events']: self._update_keypress()
        #if self._config.get('tracker_estimate_time', False):
            #self._update_time_estimation()
        if self._config.get('tracker_obj_tracking_enable', False):
            self._update_objective_function()
        if self._config.get('tracker_eval_enable', False):
            self._update_evaluation()

        if not self._state['continue']:
            nemoa.set('shell', 'buffmode', 'line')

        return self._state['continue']

    def _update_keypress(self):
        """Check Keyboard."""

        char = nemoa.get('shell', 'inkey')
        if char == 'q':
            progr = 100. * self._get_progress()
            nemoa.log('note', 'aborting optimization at %.1f%%' % progr)
            self._state['continue'] = False
        elif char == 't':
            ftime = self._get_estimate_time()
            nemoa.log('note', 'estimated finishing time %s' % ftime)

        return True

    def _update_objective_function(self):
        """Calculate objective function of system."""

        # check 'continue' flag
        if self._state['continue']:

            # check update interval
            if not not (self._state['epoch'] \
                % self._config['tracker_obj_update_interval'] == 0):
                return True

        # calculate objective function and add value to array
        func = self._config['tracker_obj_function']
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
        if self._config['tracker_obj_keep_optimum']:

            # init optimum with first value
            if self._state['obj_opt_value'] == None:
                self._state['obj_opt_value'] = value
                self._state['optimum'] = \
                    {'params': self.model.system.get(
                    'copy', 'params')}
                return True

            # allways check last optimum
            if self._state['continue'] \
                and progr < self._config['tracker_obj_init_wait']:
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

        now = time.time()

        if not self._state['continue']:
            func = self._get_evaluation_algorithm()
            value = self._get_evaluation_value()
            self._config['tracker_eval_enable'] = False
            return nemoa.log('note', 'found optimum with: %s = %s' % (
                func['name'], func['formater'](value)))

        if ((now - self._state['eval_prev_time']) \
            > self._config['tracker_eval_time_interval']):
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
                progress * 100., func['name'], func['formater'](value)))

        return False
