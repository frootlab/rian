# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

import time
import numpy
import nemoa
from flab.base import otree
from nemoa.core import ui

class Optimizer:

    _config = None
    _buffer = {}

    def __init__(self, model = None, *args, **kwds):
        """Configure tracker to given nemoa system instance."""
        if model: self._set_model(model)

    def get(self, key, *args, **kwds):
        """ """

        # algorithms
        if key == 'algorithm':
            return self._get_algorithm(*args, **kwds)
        if key == 'algorithms':
            return self._get_algorithms(
                attribute = 'about', *args, **kwds)

        if key == 'data':
            return self._get_data(*args, **kwds)
        if key == 'epoch':
            return self._get_epoch()
        if key == 'estimatetime':
            return self._get_estimatetime()
        if key == 'progress':
            return self._get_progress()
        if key == 'model':
            return self._get_model()

        if key in self._buffer: return self._buffer[key]

        return False

    def _get_algorithms(self, category = None, attribute = None):
        """Get optimization algorithms."""
        algorithms = self._buffer['algorithms'].get(attribute, None)
        if not algorithms:
            algorithms = otree.get_methods(self, key = 'name', val = attribute,
                groupby = 'category')
            self._buffer['algorithms'][attribute] = algorithms
        if category:
            if category not in algorithms: return {}
            algorithms = algorithms[category]

        return algorithms

    def _get_algorithm(self, key, *args, **kwds):
        """Get algorithm provided by transformation."""
        return self._get_algorithms(*args, **kwds).get(key, None)

    def _get_data(self, key, *args, **kwds):
        """Get data for training or evaluation.

        Args:
            key (string): purpose of data: 'training' or 'evaluation'

        Returns:
            Tuple of numpy arrays containing data for training or
            evaluation.

        """

        if key == 'training':
            return self._get_data_training(*args, **kwds)

        raise KeyError(f"unknown key '{key}'")

    def _get_evaluation_algorithm(self, key = None):
        """ """

        algorithm = self._buffer.get('evaluation_algorithm', None)
        if not algorithm:
            name = self._config['tracker_eval_function']
            algorithm = self.evaluation.get('algorithm', name,
                category = 'model')
            self._buffer['evaluation_algorithm'] = algorithm
        if key: return algorithm.get(key, None)
        return algorithm

    def _get_evaluation_value(self):
        """ """

        algorithm = self._get_evaluation_algorithm('name')
        return self.evaluation.evaluate(algorithm)

    def _get_objective_algorithm(self, key = None):
        """ """

        algorithm = self._buffer.get('objective_algorithm', None)
        if not algorithm:
            name = self._config['tracker_obj_function']
            algorithm = self.evaluation.get('algorithm', name,
                category = 'model')
            self._buffer['objective_algorithm'] = algorithm
        if key: return algorithm.get(key, None)
        return algorithm

    def _get_objective_value(self):
        """ """

        algorithm = self._get_objective_algorithm('name')
        return self.evaluation.evaluate(algorithm)

    def _get_data_training(self, *args, **kwds):
        """Get training data.

        Returns:
            Tuple of numpy arrays containing training data or None
            if training data could not be retrieved from dataset.

        """

        data = self._buffer.get('training_data', None)
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

            if data: self._buffer['training_data'] = data

        return data or None

    def _get_epoch(self):
        """Get current training epoch.

        Returns:
            Integer containing current training epoch.

        """

        return self._buffer.get('epoch', 0)

    def _get_estimatetime(self):
        """ """

        now = time.time()

        runtime = now - self._buffer['estim_start_time']
        estim = (runtime / (self._buffer['epoch'] + 1)
            * self._config['updates'])
        estim_str = time.strftime('%H:%M',
            time.localtime(now + estim))

        return estim_str


    def _get_progress(self):
        """Get current optimization progress in percentage.

        Returns:
            Float containing current progress in percentage.

        """

        return float(self._buffer['epoch']) \
            / float(self._config['updates'])

    def _get_model(self):
        """Get model instance."""
        return self._buffer.get('model', None)

    def _get_compatibility(self, model):
        """Test compatibility of transformation with model instance.

        Args:
            model: nemoa model instance

        Returns:
            True if transformation is compatible with model, else False.

        """

        # test type of model instance and subclasses
        if not otree.has_base(model, 'Model'): return False
        if not otree.has_base(model.dataset, 'Dataset'): return False
        if not otree.has_base(model.network, 'Network'): return False
        if not otree.has_base(model.system, 'System'): return False

        # check dataset
        if (not 'check_dataset' in model.system._default['init']
            or model.system._default['init']['check_dataset'] == True) \
            and not model.system._check_dataset(model.dataset):
            return False

        return True

    def _get_schedule(self, key):
        """Get schedule by name."""

        if 'schedules' not in self.model.system._config: return {}

        return self.model.system._config['schedules'].get(key, {})

    def optimize(self, config = None, **kwds):
        """ """

        if not self._set_config(config, **kwds):
            return None
        if not self._set_buffer_reset():
            return None

        # get name of optimization algorithm
        name = self._config.get('algorithm', None)
        if not name:
            raise ValueError("""could not optimize '%s'
                (%s): no optimization algorithm has been set."""
                % (self.model.name, self.model.system.type)) or None

        # get instance of optimization algorithm
        algorithm = self._get_algorithm(name, category = 'optimization')
        if not algorithm:
            raise ValueError("""could not optimize '%s':
                unsupported optimization algorithm '%s'."""
                % (self.model.name, name)) or None

        # start optimization
        if algorithm.get('type', None) == 'algorithm':
            ui.info("optimize '%s' (%s) using %s."
                % (self.model.name, self.model.system.type, name))

            # start key events
            if not self._buffer['key_events_started']:
                ui.info("press 'h' for help or 'q' to quit.")
                self._buffer['key_events_started'] = True
                nemoa.set('shell', 'buffmode', 'key')

        # TODO: retval, try / except etc.
        run_optimizer = algorithm.get('reference', None)
        if not run_optimizer:
            return None

        retval = True
        try:
            retval &= run_optimizer()
            retval &= self.model.network.initialize(self.model.system)
        except KeyboardInterrupt:
            retval = False
            nemoa.set('shell', 'buffmode', 'line')

        return retval

    def set(self, key, *args, **kwds):
        """ """

        if key == 'model':
            return self._set_model(*args, **kwds)
        if key == 'config':
            return self._set_config(*args, **kwds)
        if key == 'buffer':
            return self._set_buffer(*args, **kwds)

        raise KeyError(f"unknown key '{key}'")

    def _set_config(self, config = None, **kwds):
        if not isinstance(config, dict):
            if not config: key = 'default'
            elif isinstance(config, str):
                key = config
            else:
                raise Warning(
                    "could not configure transformation: "
                    "invalid configuration.")
            if not self.model:
                raise Warning(
                    "could not configure transformation: "
                    "no model given.")
            system = self.model.system
            schedules = system._config.get('schedules', {})
            config = schedules.get(key, {}).get(system.type, {})

        self._config = {**self._default, **config, **kwds}

        return True

    def _set_model(self, model):
        import nemoa.model.evaluation

        if not self._get_compatibility(model):
            raise Warning(
                "Could not apply transformation: "
                "transformation is not compatible with model.")

        self.model = model
        self.evaluation = nemoa.model.evaluation.new(model)

        # initialize evaluation data
        #self._get_evaluation_data()

        return True

    def _set_buffer(self, key, value = None):
        if key == 'reset':
            return self._set_buffer_reset()
        if key in self._buffer:
            self._buffer[key] = value
            return True

        raise KeyError(f"unknown key '{key}'")

    def _set_buffer_reset(self):
        now = time.time()

        self._buffer = {
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
            'estim_start_time': now,
            'store': {},
            'algorithms': {} }

        return True

    def read(self, key, id = -1):
        """Read value from queue."""

        if key not in self._buffer['store']: return None
        queue = self._buffer['store'][key]
        if len(queue) < abs(id):
            raise Warning("""could not read from store:
                invaid id '%s' in key '%s'.""" % (id, key)) or None

        return queue[id]

    def write(self, key, id = -1, append = False, **kwds):
        """Write value to queue."""

        if key not in self._buffer['store']: self._buffer['store'][key] = []
        queue = self._buffer['store'][key]
        if len(queue) == (abs(id) - 1) or append == True:
            queue.append(kwds)
            return True
        if len(queue) < id:
            raise Warning(
                'could not write to store, wrong index.')
        queue[id] = kwds

        return True

    def update(self):
        """Update epoch and check termination criterions."""
        self._buffer['epoch'] += 1
        if self._buffer['epoch'] >= self._config['updates']:
            self._buffer['continue'] = False

        if self._buffer['key_events']:
            self._update_keypress()
        if self._config.get('tracker_obj_tracking_enable', False):
            self._update_objective_function()
        if self._config.get('tracker_eval_enable', False):
            self._update_evaluation()

        if not self._buffer['continue']:
            nemoa.set('shell', 'buffmode', 'line')

        return self._buffer['continue']

    def _update_keypress(self):
        """Check Keyboard."""

        char = nemoa.get('shell', 'inkey')
        if not char:
            return True

        if char == 'e':
            pass
        elif char == 'h':
            ui.info(
                "Keyboard Shortcuts\n"
                "'e' -- calculate evaluation function\n"
                "'h' -- show this\n"
                "'q' -- quit optimization\n"
                "'t' -- estimate finishing time")
        elif char == 'q':
            ui.info('aborting optimization')
            self._buffer['continue'] = False
        elif char == 't':
            ftime = self._get_estimatetime()
            ui.info('estimated finishing time %s' % ftime)

        return True

    def _update_objective_function(self):
        """Calculate objective function of system."""

        # check 'continue' flag
        if self._buffer['continue']:

            # check update interval
            if not (self._buffer['epoch'] \
                % self._config['tracker_obj_update_interval'] == 0):
                return True

        # calculate objective function and add value to array
        value = self._get_objective_value()
        progr = self._get_progress()
        if not isinstance(self._buffer['obj_values'], numpy.ndarray):
            self._buffer['obj_values'] = numpy.array([[progr, value]])
        else: self._buffer['obj_values'] = \
            numpy.vstack((self._buffer['obj_values'], \
            numpy.array([[progr, value]])))

        # (optional) check for new optimum
        if self._config['tracker_obj_keep_optimum']:

            # init optimum with first value
            if self._buffer['obj_opt_value'] is None:
                self._buffer['obj_opt_value'] = value
                self._buffer['optimum'] = \
                    {'params': self.model.system.get(
                    'copy', 'params')}
                return True

            # allways check last optimum
            if self._buffer['continue'] \
                and progr < self._config['tracker_obj_init_wait']:
                return True

            #type_of_optimum = self.model.system.get(
                #'algorithm', func,
                #category = ('system', 'evaluation'),
                #attribute = 'optimum')

            type_of_optimum = self._get_objective_algorithm('optimum')
            current_optimum = self._buffer['obj_opt_value']

            if type_of_optimum == 'min' and value < current_optimum:
                new_optimum = True
            elif type_of_optimum == 'max' and value > current_optimum:
                new_optimum = True
            else:
                new_optimum = False

            if new_optimum:
                self._buffer['obj_opt_value'] = value
                self._buffer['optimum'] = { 'params':
                    self.model.system.get('copy', 'params') }

            # set system parameters to optimum on last update
            if not self._buffer['continue']:
                return self.model.system.set('copy',
                    **self._buffer['optimum'])

        return True

    def _update_evaluation(self):
        """Calculate evaluation function of system."""

        now = time.time()

        if not self._buffer['continue']:
            func = self._get_evaluation_algorithm()
            value = self._get_evaluation_value()
            self._config['tracker_eval_enable'] = False
            return ui.info('found optimum with: %s = %s' % (
                func['name'], func['formater'](value)))

        if ((now - self._buffer['eval_prev_time'])
            > self._config['tracker_eval_time_interval']):
            func = self._get_evaluation_algorithm()
            value = self._get_evaluation_value()
            progress = self._get_progress()

            # update time of last evaluation
            self._buffer['eval_prev_time'] = now

            # add evaluation to array
            if not isinstance(self._buffer['eval_values'],
                numpy.ndarray):
                self._buffer['eval_values'] = \
                    numpy.array([[progress, value]])
            else:
                self._buffer['eval_values'] = \
                    numpy.vstack((self._buffer['eval_values'], \
                    numpy.array([[progress, value]])))

            return ui.info('finished %.1f%%: %s = %s' % (
                progress * 100., func['name'], func['formater'](value)))

        return False
