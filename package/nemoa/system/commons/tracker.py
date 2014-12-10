# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import numpy
import time

class Tracker:

    _system = None # linked nemoa system instance
    _config = None # linked nemoa system optimization configuration
    _state = {}    # dictionary for tracking variables
    _store = {}    # dictionary for storage of optimization parameters

    def __init__(self, system):
        """Configure tracker to given nemoa system instance."""

        _state = {}
        _store = {}

        if not nemoa.type.issystem(system): return nemoa.log('warning',
            'could not configure tracker: system is not valid!')
        if not hasattr(system, '_config'): return nemoa.log('warning',
            'could not configure tracker: system contains no configuration!')
        if not 'optimize' in system._config: return nemoa.log('warning',
            'could not configure tracker: system contains no configuration for optimization!')

        # link system and system config
        self._system = system
        self._config = system._config['optimize']

        # init state
        now = time.time()

        self._state = {
            'epoch': 0,
            'data': None,
            'optimum': {},
            'continue': True,
            'obj_enable': self._config['tracker_obj_tracking_enable'],
            'obj_init_wait': self._config['tracker_obj_init_wait'],
            'obj_values': None,
            'obj_opt_value': None,
            'key_events': True,
            'key_events_started': False,
            'eval_enable': self._config['tracker_eval_enable'],
            'eval_prev_time': now,
            'eval_values': None,
            'estim_enable': self._config['tracker_estimate_time'],
            'estim_started': False,
            'estim_start_time': now
        }

    def get(self, key):
        if not key in self._state.keys(): return False
        return self._state[key]

    def set(self, **kwargs):
        found = True
        for key in kwargs.keys():
            if key in self._state.keys():
                self._state[key] = kwargs[key]
            else: found = False
        return found

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
            nemoa.log("""estimating time for calculation
                of %i updates.""" % (self._config['updates']))
            self._state['estim_started'] = True
            self._state['estim_start_time'] = time.time()
            return True

        now = time.time()
        runtime = now - self._state['estim_start_time']
        if runtime > self._config['tracker_estimate_time_wait']:
            estim = (runtime / (self._state['epoch'] + 1)
                * self._config['updates'])
            estim_str = time.strftime('%H:%M',
                time.localtime(now + estim))
            nemoa.log('note', 'estimation: %ds (finishing time: %s)'
                % (estim, estim_str))
            self._state['estim_enable'] = False
            return True

        return True

    def update(self):
        """Update epoch and check termination criterions."""
        self._update_epoch()
        if self._state['key_events']: self._update_keypress()
        if self._state['estim_enable']: self._update_time_estimation()
        if self._state['obj_enable']: self._update_objective_function()
        if self._state['eval_enable']: self._update_evaluation()

        if not self._state['continue']:
            nemoa.common.console.cleanup()

        return self._state['continue']

    def _update_epoch(self):
        self._state['epoch'] += 1
        if self._state['epoch'] == self._config['updates']:
            self._state['continue'] = False
        return True

    def _update_keypress(self):
        """Check Keyboard."""
        if not self._state['key_events_started']:
            nemoa.log('note', """press 'q' if you want to abort
                the optimization""")
            self._state['key_events_started'] = True

        char = nemoa.common.getch()
        if isinstance(char, str):
            if char == 'q':
                nemoa.log('note', '... aborting optimization')
                self._state['continue'] = False

        return True

    def _update_objective_function(self):
        """Calculate objective function of system."""

        # check testdata
        if self._state['data'] == None:
            nemoa.log('warning', """tracking the objective function
                is not possible: testdata is needed.""")
            self._state['obj_enable'] = False
            return False

        # check 'continue' flag
        if self._state['continue']:

            # check update interval
            if not not (self._state['epoch'] \
                % self._config['tracker_obj_update_interval'] == 0):
                return True

        # calculate objective function and add value to array
        func = self._config['tracker_obj_function']
        value = self._system.evaluate(data = self._state['data'],
            func = func)
        progr = float(self._state['epoch']) \
            / float(self._config['updates'])
        if self._state['obj_values'] == None:
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
                    {'params': self._system.get('copy', 'params')}
                return True

            # allways check last optimum
            if self._state['continue'] \
                and progr < self._config['tracker_obj_init_wait']:
                return True

            type_of_optimum = self._system.get('algorithm', func,
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
                self._state['optimum'] = \
                    {'params': self._system.get('copy', 'params')}

            # set system parameters to optimum on last update
            if not self._state['continue']:
                return self._system.set('copy', **self._state['optimum'])

        return True

    def _update_evaluation(self):
        """Calculate evaluation function of system."""

        cfg = self._config
        now = time.time()

        if self._state['data'] == None:
            nemoa.log('warning', """tracking the evaluation function
                is not possible: testdata is needed!""")
            self._state['eval_enable'] = False
            return False

        if not self._state['continue']:
            func = cfg['tracker_eval_function']
            prop = self._system.get('algorithm', func)
            value = self._system.evaluate(data = self._state['data'],
                func = func)
            self._state['eval_enable'] = False
            return nemoa.log('note', 'found optimum with: %s = %s' % (
                prop['name'], prop['formater'](value)))

        if ((now - self._state['eval_prev_time']) \
            > cfg['tracker_eval_time_interval']):
            func = cfg['tracker_eval_function']
            prop = self._system.get('algorithm', func)
            value = self._system.evaluate(data = self._state['data'],
                func = func)
            progr = float(self._state['epoch']) \
                / float(cfg['updates']) * 100.

            # update time of last evaluation
            self._state['eval_prev_time'] = now

            # add evaluation to array
            if self._state['eval_values'] == None:
                self._state['eval_values'] = \
                    numpy.array([[progr, value]])
            else:
                self._state['eval_values'] = \
                    numpy.vstack((self._state['eval_values'], \
                    numpy.array([[progr, value]])))

            return nemoa.log('note', 'finished %.1f%%: %s = %s' % (
                progr, prop['name'], prop['formater'](value)))

        return False

