#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nemoa, numpy, time

class __base:

    __inspect = True
    __estimate = True
    __data = None
    __config = None
    __system = None
    __state = {}
    __store = []

    def __init__(self, system = None):
        self.__configure(system)

    def __configure(self, system):
        """Configure tracker to given nemoa.system instance."""
        if not nemoa.type.isSystem(system): return nemoa.log('warning',
            'could not configure tracker: system is not valid!')
        if not hasattr(system, '_config'): return nemoa.log('warning',
            'could not configure tracker: system contains no configuration!')
        if not 'optimize' in system._config: return nemoa.log('warning',
            'could not configure tracker: system contains no configuration for optimization!')

        # link system
        self.__system = system
        self.__inspect = system._config['optimize']['inspect'] \
            if 'inspect' in system._config['optimize'] \
            else True
        self.__estimate = system._config['optimize']['inspectEstimateTime'] \
            if 'inspectEstimateTime' in system._config['optimize'] \
            else True

    def setTestData(self, data):
        """Set numpy array with destdata."""
        self.__data = data

    def reset(self):
        """Reset inspection."""
        self.__state = {}
        self.__store = []

    def write(self, id = -1, append = False, **kwargs):
        if len(self.__store) == (abs(id) - 1) or append == True:
            self.__store.append(kwargs)
            return True
        if len(self.__store) < id: return nemoa.log('error',
            'could not write to store, wrong index!')
        self.__store[id] = kwargs
        return True

    def read(self, id = -1):
        return self.__store[id] if len(self.__store) >= abs(id) else {}

    def difference(self):
        if not 'inspection' in self.__state: return 0.0
        if self.__state['inspection'] == None: return 0.0
        if self.__state['inspection'].shape[0] < 2: return 0.0
        return self.__state['inspection'][-1, 1] - \
            self.__state['inspection'][-2, 1]

    def trigger(self):
        """Update epoch and time and calculate """

        cfg = self.__system._config['optimize']
        epochTime = time.time()
        if self.__state == {}: self.__initState()
        self.__state['epoch'] += 1
        self.__triggerKeyEvent() # check keyboard input

        # estimate time needed to finish current optimization schedule
        if self.__estimate and not self.__state['estimateEnded']:
            if not self.__state['estimateStarted']:
                nemoa.log("""estimating time for calculation
                    of %i updates.""" % (cfg['updates']))
                self.__state['estimateStarted'] = True
            if (epochTime - self.__state['startTime']) \
                > cfg['inspectEstimateTimeWait']:
                estim = ((epochTime - self.__state['startTime']) \
                    / (self.__state['epoch'] + 1)
                    * cfg['updates'] * cfg['iterations'])
                estimStr = time.strftime('%H:%M',
                    time.localtime(time.time() + estim))
                nemoa.log('note', 'estimation: %ds (finishing time: %s)'
                    % (estim, estimStr))
                self.__state['estimateEnded'] = True

        # evaluate model (in a given time interval)
        if self.__inspect: self.__triggerEval()
        if self.__state['abort']: return 'abort'

        return True

    def __initState(self):

        epochTime = time.time()

        nemoa.log('note', "press 'q' if you want to abort the optimization")
        self.__state = {
            'startTime': epochTime,
            'epoch': 0,
            'inspection': None,
            'abort': False}
        if self.__inspect: self.__state['inspectTime'] = epochTime
        if self.__estimate:
            self.__state['estimateStarted'] = False
            self.__state['estimateEnded'] = False

        return True

    def __triggerKeyEvent(self):
        """Check Keyboard."""

        c = nemoa.common.getch()
        if isinstance(c, str):
            if c == 'q':
                nemoa.log('note', '... aborting optimization')
                self.__system._config['optimize']['updates'] = \
                    self.__state['epoch']
                self.__state['abort'] = True

        return True

    def __triggerEval(self):
        """Evaluate Model."""

        cfg = self.__system._config['optimize']
        epochTime = time.time()

        if self.__data == None:
            nemoa.log('warning', """
                monitoring the process of optimization is not possible:
                testdata is needed!""")
            self.__inspect = False
            return False

        if self.__state['epoch'] == cfg['updates']:
            func  = cfg['inspectFunction']
            prop  = self.__system.about(func)
            value = self.__system.eval(data = self.__data, func = func)
            out   = 'final: %s = ' + prop['format']
            return nemoa.log('note', out % (prop['name'], value))

        if ((epochTime - self.__state['inspectTime']) \
            > cfg['inspectTimeInterval']) \
            and not (self.__estimate \
            and self.__state['estimateStarted'] \
            and not self.__state['estimateEnded']):
            func  = cfg['inspectFunction']
            prop  = self.__system.about(func)
            value = self.__system.eval(data = self.__data, func = func)
            progr = float(self.__state['epoch']) / float(cfg['updates']) * 100.0

            # update time of last evaluation
            self.__state['inspectTime'] = epochTime

            # add evaluation to array
            if self.__state['inspection'] == None:
                self.__state['inspection'] = numpy.array([[progr, value]])
            else: self.__state['inspection'] = \
                numpy.vstack((self.__state['inspection'], \
                numpy.array([[progr, value]])))

            out = 'finished %.1f%%: %s = ' + prop['format']
            return nemoa.log('note', out % (progr, prop['name'], value))

        return False

def new(*args, **kwargs):
    """Return new tracker instance."""
    return __base(*args, **kwargs)
