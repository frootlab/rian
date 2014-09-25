# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import numpy
import time
import copy

class system:

    def __init__(self, *args, **kwargs):
        """Configure system and system parameters."""

        # set configuration and update units and links
        self._set_config(kwargs['config'] if 'config' in kwargs else {})

    def configure(self, dataset = None, network = None, *args, **kwargs):
        """Configure system and subsystems to network and dataset."""
        if not hasattr(self.__class__, '_configure') \
            or not callable(getattr(self.__class__, '_configure')):
            return True
        nemoa.log("configure system '%s'" % (self.name()))
        nemoa.log('set', indent = '+1')
        if not self._check_network(network):
            nemoa.log('error', """system could not be configured:
                network is not valid!""")
            nemoa.log('set', indent = '-1')
            return False
        if not self._check_dataset(dataset):
            nemoa.log('error', """system could not be configured:
                dataset is not valid!""")
            nemoa.log('set', indent = '-1')
            return False
        retVal = self._configure(dataset = dataset, network = network,
            *args, **kwargs)
        nemoa.log('set', indent = '-1')
        return retVal

    def setName(self, name):
        """Set name of system."""
        if not isinstance(name, str): return False
        self._config['name'] = name
        return True

    def getConfig(self):
        """Return system configuration as dictionary."""
        return self._config.copy()

    def _set_config(self, config):
        """Set configuration."""
        # create local configuration dictionary
        if not hasattr(self, '_config'):
            self._config = {'check': {}}
            for key in ['params', 'init', 'optimize']:
                if not key in self._config:
                    self._config[key] = self._default(key)

        # overwrite / merge local with given configuration
        nemoa.common.dictMerge(config, self._config)

        # create / update local unit and link dictionaries
        if not hasattr(self, '_params'): self._params = {}
        self.setUnits(self._get_units_from_config())
        self.setLinks(self._get_links_from_config())

        self._config['check']['config'] = True
        return True

    def _is_configured(self):
        """Return configuration state of system."""
        return self._config['check']['config'] \
            and self._config['check']['network'] \
            and self._config['check']['dataset']

    def setNetwork(self, *args, **kwargs):
        """Update units and links to network instance."""
        return self._set_network(*args, **kwargs)

    def updateNetwork(self, network):
        """update params in network."""
        if not nemoa.type.isNetwork(network): return False
        G = network.graph
        for u, v, d in G.edges(data = True):
            params = self._getLink((u, v))
            if not params: params = self._getLink((v, u))
            if not params: continue
            nemoa.common.dictMerge(params, G[u][v]['params'])
            G[u][v]['weight'] = params['weight']
        return True

    def setDataset(self, *args, **kwargs):
        """Update units and links to dataset instance."""
        return self._set_dataset(*args, **kwargs)

    def _check_network(self, network, *args, **kwargs):
        """Check if network is valid for system."""
        if not nemoa.type.isNetwork(network): return False
        return True

    #2do: there is more to check
    def _check_dataset(self, dataset, *args, **kwargs):
        """Check if network is valid for system."""
        if not nemoa.type.isDataset(dataset): return False
        return True

    def _is_empty(self):
        """Return true if system is a dummy."""
        return False

    def getUnits(self, **kwargs):
        """.

        Returns:
            Tuple with lists of units that match a given property

        Examples:
            return visible units: getUnits(visible = True)

        """

        filter = []
        for key in kwargs.keys():
            if key == 'group':
                key = 'name'
                kwargs['name'] = kwargs['group']
            if key in self._params['units'][0].keys():
                filter.append((key, kwargs[key]))

        groups = ()
        for group in self._params['units']:
            valid = True
            for key, val in filter:
                if not group[key] == val:
                    valid = False
                    break
            if valid: groups += (group['label'], )

        return groups

    def setUnits(self, units = None, initialize = True):
        """Set units and update system parameters."""
        if not 'units' in self._params: self._params['units'] = []
        if not hasattr(self, 'units'): self.units = {}
        if initialize: return self._set_units(units) and self._init_units()
        return self._set_units(units)

    def unlinkUnit(self, unit):
        """Unlink unit (if present)."""
        return self._unlink_unit(unit)

    def removeUnits(self, type, label):
        """Remove unit."""
        return self._removeUnit(type, label)

    def getGroups(self, **kwargs):
        """.

        Returns:
            Tuple with groups of units that match a given property

        Examples:
            return visible groups:
                getGroups(visible = True)
            search for group 'MyGroup':
                getGroups(name = 'MyGroup')
        """

        filter = []
        for key in kwargs.keys():
            if key in self._params['units'][0].keys():
                filter.append((key, kwargs[key]))

        groups = ()
        for group in self._params['units']:
            valid = True
            for key, val in filter:
                if not group[key] == val:
                    valid = False
                    break
            if valid: groups += (group['name'], )

        return groups

    def getGroupOfUnit(self, unit):
        """Return name of unit group of given unit."""
        for id in range(len(self._params['units'])):
            if unit in self._params['units'][id]['label']:
                return self._params['units'][id]['name']
        return None

    def setLinks(self, links = None, initialize = True):
        """Set links using list with 2-tuples containing unit labels."""
        if not 'links' in self._params: self._params['links'] = {}
        if not hasattr(self, 'links'): self.links = {}
        if initialize: return self._set_links(links) \
            and self._index_links() and self._init_links()
        return self._index_links()

    def getLinks(self, *args, **kwargs):
        """Return list with 2-tuples containing unit labels."""
        return self._get_links_from_config()

    def removeLinks(self, links = [], *args, **kwargs):
        """Remove links from system using list with 2-tuples containing unit labels."""
        return self._remove_links(links)

    def _getLink(self, link):
        srcUnit = link[0]
        tgtUnit = link[1]
        srcGrp  = self.getGroupOfUnit(srcUnit)
        tgtGrp  = self.getGroupOfUnit(tgtUnit)
        if not srcGrp in self._links \
            or not tgtGrp in self._links[srcGrp]['target']: return None
        linkGrp = self._links[srcGrp]['target'][tgtGrp]
        srcID   = self.units[srcGrp].params['label'].index(srcUnit)
        tgtID   = self.units[tgtGrp].params['label'].index(tgtUnit)
        weight  = linkGrp['W'][srcID, tgtID]
        norm    = float(numpy.sum(linkGrp['A'])) / numpy.sum(
            numpy.abs(linkGrp['W']))
        return {
            'adjacency': linkGrp['A'][srcID, tgtID],
            'weight':    weight,
            'normal':    norm * weight}

    def _get(self, section = None):
        """Return system settings as dictionary."""
        dict = {
            'config': copy.deepcopy(self._config),
            'params': copy.deepcopy(self._params) }
        if not section: return dict
        if section in dict: return dict[section]
        return False

    def _set(self, **kwargs):
        """Set system settings from dictionary."""
        if 'config' in kwargs:
            self._config = copy.deepcopy(kwargs['config'])
        if 'params' in kwargs:
            self._params = copy.deepcopy(kwargs['params'])
        return self._update_units_and_links()

    def initialize(self, dataset = None):
        """Initialize system parameters.

        Initialize all system parameters to dataset.

        Args:
            dataset: nemoa dataset instance
        """
        if not nemoa.type.isDataset(dataset): return nemoa.log('error',
            """could not initilize system parameters:
            invalid dataset instance given!""")
        return self._init_params(dataset)

    def getParams(self, *args, **kwargs):
        """Return dictinary with all system parameters."""
        return copy.deepcopy(self._params)

    def setParams(self, params, update = True):
        """Set system parameters using from dictionary."""
        if not self._check_params(params): return nemoa.log('error',
            """could not set system parameters:
            invalid 'params' dictionary given!""")
        if update: self._set_params(params)
        else: self._params = copy.deepcopy(params)
        return True

    def resetParams(self, dataset):
        """Reset system parameters using dataset instance."""
        return self.initialize(dataset)

    def optimize(self, dataset, schedule):
        """Optimize system parameters using data and given schedule."""

        # check if optimization schedule exists for current system
        # and merge default, existing and given schedule
        if not 'params' in schedule:
            config = self._default('optimize')
            nemoa.common.dictMerge(self._config['optimize'], config)
            self._config['optimize'] = config
        elif not self.getType() in schedule['params']: return nemoa.log(
            'error', """could not optimize model:
            optimization schedule '%s' does not include system '%s'
            """ % (schedule['name'], self.getType()))
        else:
            config = self._default('optimize')
            nemoa.common.dictMerge(self._config['optimize'], config)
            nemoa.common.dictMerge(schedule['params'][self.getType()], config)
            self._config['optimize'] = config

        # check dataset
        if (not 'checkDataset' in config
            or config['checkDataset'] == True) \
            and not self._check_dataset(dataset): return False

        # initialize tracker
        tracker = nemoa.system.base.tracker(self)
        tracker.setTestData(self._get_test_data(dataset))

        # optimize system parameters
        algorithm = config['algorithm'].title()
        nemoa.log('note', "optimize '%s' (%s) using algorithm '%s'" % \
            (self.name(), self.getType(), algorithm))
        nemoa.log('set', indent = '+1')
        retVal = self._optimize_params(dataset, schedule, tracker)
        nemoa.log('set', indent = '-1')

        return retVal

    def eval(self, data, *args, **kwargs):
        if len(args) == 0:
            return self._eval_system(data, **kwargs)

        # System unit evaluation
        if args[0] == 'units':
            return self._eval_units(data, *args[1:], **kwargs)

        # System link evaluation
        if args[0] == 'links':
            return self._eval_links(data, *args[1:], **kwargs)

        # System relation evaluation
        if args[0] == 'relations':
            return self._eval_relation(data, *args[1:], **kwargs)

        # System evaluation
        if args[0] in self._about_system().keys():
            return self._eval_system(data, *args, **kwargs)

        return nemoa.log('warning',
            "unsupported system evaluation '%s'" % (args[0]))

    @staticmethod
    def _get_data_sum(data, norm = 'S'):
        """Return sum of data.

        Args:
            data: numpy array containing data
            norm: data mean norm
                'S': Sum of Values
                'SE': Sum of Errors / L1 Norm
                'SSE': Sum of Squared Errors
                'RSSE': Root Sum of Squared Errors
        """

        norm = norm.upper()

        # Sum of Values (S)
        if norm == 'S':
            return numpy.sum(data, axis = 0)

        # Sum of Errors (SE) / L1-Norm (L1)
        if norm == 'SE':
            return numpy.sum(numpy.abs(data), axis = 0)

        # Sum of Squared Errors (SSE)
        if norm == 'SSE':
            return numpy.sum(data ** 2, axis = 0)

        # Root Sum of Squared Errors (RSSE)
        if norm == 'RSSE':
            return numpy.sqrt(numpy.sum(data ** 2, axis = 0))

        return nemoa.log('error',
            "unsupported data sum norm '%s'" % (norm))

    @staticmethod
    def _get_data_mean(data, norm = 'M'):
        """Return mean of data.

        Args:
            data: numpy array containing data
            norm: data mean norm
                'M': Arithmetic Mean of Values
                'ME': Mean of Errors
                'MSE': Mean of Squared Errors
                'RMSE': Root Mean of Squared Errors / L2 Norm
        """

        norm = norm.upper()

        # Mean of Values (M)
        if norm == 'M':
            return numpy.mean(data, axis = 0)

        # Mean of Errors (ME)
        if norm == 'ME':
            return numpy.mean(numpy.abs(data), axis = 0)

        # Mean of Squared Errors (MSE)
        if norm == 'MSE':
            return numpy.mean(data ** 2, axis = 0)

        # Root Mean of Squared Errors (RMSE) / L2-Norm
        if norm == 'RMSE':
            return numpy.sqrt(numpy.mean(data ** 2, axis = 0))

        return nemoa.log('error',
            "unsupported data mean norm '%s'" % (norm))

    @staticmethod
    def _get_data_deviation(data, norm = 'SD'):
        """Return deviation of data.

        Args:
            data: numpy array containing data
            norm: data deviation norm
                'SD': Standard Deviation of Values
                'SDE': Standard Deviation of Errors
                'SDSE': Standard Deviation of Squared Errors
        """

        norm = norm.upper()

        # Standard Deviation of Data (SD)
        if norm == 'SD':
            return numpy.std(data, axis = 0)

        # Standard Deviation of Errors (SDE)
        if norm == 'SDE':
            return numpy.std(numpy.abs(data), axis = 0)

        # Standard Deviation of Squared Errors (SDSE)
        if norm == 'SDSE':
            return numpy.std(data ** 2, axis = 0)

        return nemoa.log('error',
            "unsupported data deviation norm '%s'" % (deviation))

    def mapData(self, data, mapping = None, transform = 'expect'):
        """Return system representation of data.

        Args:
            mapping: tuple of strings describing the mapping function
            transform: mapping algorithm
        """

        if mapping == None:
            mapping = self.mapping()
        if transform == 'expect':
            return self._eval_unit_expect(data, mapping)
        if transform == 'value':
            return self._eval_unit_values(data, mapping)
        if transform == 'sample':
            return self._eval_unit_samples(data, mapping)
        return nemoa.log('error', """could not map data:
            unknown mapping algorithm '%s'""" % (transform))

    def about(self, *args):
        """Metainformation of the system.

        Args:
            *args: strings, containing a breadcrump trail to
                a specific information about the system

        Examples:
            about('units', 'error')
                Returns information about the 'error' measurement
                function of the systems units.

        Returns:
            Dictionary containing generic information about various
            parts of the system.
        """

        # create information dictionary
        about = nemoa.common.dictMerge({
            'name': self.name(),
            'description': self.__doc__,
            'class': self._config['class'],
            'type': self.getType(),
            'units': self._about_units(),
            'links': self._about_links(),
            'relations': self._about_relations()
        }, self._about_system())

        retDict = about
        path = ['system']
        for arg in args:
            if not isinstance(retDict, dict): return retDict
            if not arg in retDict.keys(): return nemoa.log('warning',
                "%s has no property '%s'" % (' → '.join(path), arg))
            path.append(arg)
            retDict = retDict[arg]
        if not isinstance(retDict, dict): return retDict
        return {key: retDict[key] for key in retDict.keys()}

    def name(self):
        """Return name of system."""
        return self._config['name']

    def getType(self):
        """Return sytem type."""
        return '%s.%s' % (self._config['package'],
            self._config['class'])

class tracker:

    _data   = None # data used for objective tracking and evaluation
    _system = None # linked nemoa system instance
    _config = None # linked nemoa system optimization configuration
    _state  = {}   # dictionary for tracking variables
    _store  = {}   # dictionary for storage of optimization parameters

    def __init__(self, system):
        """Configure tracker to given nemoa system instance."""
        if not nemoa.type.isSystem(system): return nemoa.log('warning',
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
            'optimum': {},
            'continue': True,
            'objEnable': self._config['tracker_obj_tracking_enable'],
            'objInitWait': self._config['tracker_obj_init_wait'],
            'objValues': None,
            'objOptValue': None,
            'keyEvents': True,
            'keyEventsStarted': False,
            'evalEnable': self._config['tracker_eval_enable'],
            'evalPrevTime': now,
            'evalValues': None,
            'estimateTime': self._config['tracker_estimate_time'],
            'estimateStarted': False,
            'estimateStartTime': now
        }

    def setTestData(self, data):
        """Set numpy array with destdata."""
        self._data = data

    def get(self, key):
        if not key in self._state.keys(): return False
        return self._state[key]

    def set(self, key, val):
        if not key in self._state.keys(): return False
        self._state[key] = val
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
        if not self._state['estimateTime']: return True

        if not self._state['estimateStarted']:
            nemoa.log("""estimating time for calculation
                of %i updates.""" % (self._config['updates']))
            self._state['estimateStarted'] = True
            self._state['estimateStartTime'] = time.time()
            return True

        now = time.time()
        runtime = now - self._state['estimateStartTime']
        if runtime > self._config['tracker_estimate_timeWait']:
            estim = (runtime / (self._state['epoch'] + 1)
                * self._config['updates'])
            estimStr = time.strftime('%H:%M',
                time.localtime(now + estim))
            nemoa.log('note', 'estimation: %ds (finishing time: %s)'
                % (estim, estimStr))
            self._state['estimateTime'] = False
            return True

        return True

    def update(self):
        """Update epoch and check termination criterions."""
        self._update_epoch()
        if self._state['keyEvents']: self._update_keypress()
        if self._state['estimateTime']: self._update_time_estimation()
        if self._state['objEnable']: self._update_objective_function()
        if self._state['evalEnable']: self._update_evaluation()
        return self._state['continue']

    def _update_epoch(self):
        self._state['epoch'] += 1
        if self._state['epoch'] == self._config['updates']:
            self._state['continue'] = False
        return True

    def _update_keypress(self):
        """Check Keyboard."""
        if not self._state['keyEventsStarted']:
            nemoa.log('note', """press 'q' if you want to abort
                the optimization""")
            self._state['keyEventsStarted'] = True

        c = nemoa.common.getch()
        if isinstance(c, str):
            if c == 'q':
                nemoa.log('note', '... aborting optimization')
                self._state['continue'] = False

        return True

    def _update_objective_function(self):
        """Calculate objective function of system."""

        if self._data == None:
            nemoa.log('warning', """tracking the objective function
                is not possible: testdata is needed!""")
            self._state['objEnable'] = False
            return False

        cfg = self._config
        interval = cfg['tracker_obj_update_interval']
        if self._state['continue'] \
            and not (self._state['epoch'] % interval == 0): return True

        # calculate objective function value
        func  = cfg['tracker_obj_function']
        value = self._system.eval(data = self._data, func = func)
        progr = float(self._state['epoch']) / float(cfg['updates'])

        # add objective function value to array
        if self._state['objValues'] == None:
            self._state['objValues'] = numpy.array([[progr, value]])
        else: self._state['objValues'] = \
            numpy.vstack((self._state['objValues'], \
            numpy.array([[progr, value]])))

        # (optional) check for new optimum
        if cfg['tracker_obj_keep_optimum']:
            # init optimum with first value
            if self._state['objOptValue'] == None:
                self._state['objOptValue'] = value
                self._state['optimum'] = \
                    {'params': self._system._get('params')}
                return True
            # allways check last optimum
            if self._state['continue'] \
                and float(self._state['epoch']) / float(cfg['updates']) \
                < cfg['tracker_obj_init_wait']: return True
            type_of_optimum = self._system.about(func)['optimum']
            current_optimum = self._state['objOptValue']

            if type_of_optimum == 'min' and value < current_optimum:
                new_optimum = True
            elif type_of_optimum == 'max' and value > current_optimum:
                new_optimum = True
            else: new_optimum = False

            if new_optimum:
                self._state['objOptValue'] = value
                self._state['optimum'] = \
                    {'params': self._system._get('params')}

            # set system parameters to optimum on last update
            if not self._state['continue']:
                return self._system._set(**self._state['optimum'])

        return True

    def _update_evaluation(self):
        """Calculate evaluation function of system."""

        cfg = self._config
        now = time.time()

        if self._data == None:
            nemoa.log('warning', """tracking the evaluation function
                is not possible: testdata is needed!""")
            self._state['evalEnable'] = False
            return False

        if not self._state['continue']:
            func  = cfg['tracker_eval_function']
            prop  = self._system.about(func)
            value = self._system.eval(data = self._data, func = func)
            out   = 'found optimum with: %s = ' + prop['format']
            self._state['evalEnable'] = False
            return nemoa.log('note', out % (prop['name'], value))

        if ((now - self._state['evalPrevTime']) \
            > cfg['tracker_eval_time_interval']):
            func  = cfg['tracker_eval_function']
            prop  = self._system.about(func)
            value = self._system.eval(data = self._data, func = func)
            progr = float(self._state['epoch']) \
                / float(cfg['updates']) * 100.

            # update time of last evaluation
            self._state['evalPrevTime'] = now

            # add evaluation to array
            if self._state['evalValues'] == None:
                self._state['evalValues'] = numpy.array([[progr, value]])
            else: self._state['evalValues'] = \
                numpy.vstack((self._state['evalValues'], \
                numpy.array([[progr, value]])))

            out = 'finished %.1f%%: %s = ' + prop['format']
            return nemoa.log('note', out % (progr, prop['name'], value))

        return False
