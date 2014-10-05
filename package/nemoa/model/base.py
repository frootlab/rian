# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import numpy
import copy
import time
import os

class model:
    """nemoa model class.

    Attributes:
        dataset: nemoa dataset instance
        network: nemoa network instance
        system: nemoa system instance

    """

    dataset = None
    network = None
    system = None

    def __init__(self, config = {}, dataset = None, network = None,
        system = None, name = None):
        """Initialize model and configure dataset, network and system.

        Args:
            dataset: nemoa dataset instance
            network: nemoa network instance
            system: nemoa system instance

        """

        self._config = {'name': name} # initialize class attributes

        nemoa.log("""linking dataset, network and system instances
            to model""")
        self.dataset = dataset
        self.network = network
        self.system = system

        if self._is_empty(): return
        if not self._check_model(): return
        self._update_config()

    def _set_config(self, config):
        """Set configuration from dictionary."""
        self._config = config.copy()
        return True

    def _export_data(self, *args, **kwargs):
        """Export data to file."""
        # copy dataset
        settings = self.dataset.get('backup')
        self.dataset._transform(system = self.system)
        self.dataset.export(*args, **kwargs)
        self.dataset.set('backup', settings)
        return True

    def _import_config_from_dict(self, dict):
        """Import numpy configuration from dictionary."""
        # copy dataset, network and system configuration
        keys = ['config', 'dataset', 'network', 'system']
        for key in keys:
            if not key in dict: return nemoa.log('error',
                """could not import configuration:
                given dictionary does not contain '%s' information!
                """ % (key))
        return {key: dict[key].copy() for key in keys}

    def _check_model(self, allow_none = False):
        if (allow_none and self.dataset == None) \
            or not nemoa.type.is_dataset(self.dataset): return False
        if (allow_none and self.network == None) \
            or not nemoa.type.is_network(self.network): return False
        if (allow_none and self.system == None) \
            or not nemoa.type.is_system(self.system): return False
        return True

    def _update_config(self):
        """Update model configuration."""

        # set version of model
        self._config['version'] = nemoa.version

        # set name of model
        if not 'name' in self._config or not self._config['name']:
            if not self.network.get('name'):
                self._set_name('%s-%s' % (
                    self.dataset.get('name'),
                    self.system.get('name')))
            else:
                self._set_name('%s-%s-%s' % (
                    self.dataset.get('name'),
                    self.network.get('name'),
                    self.system.get('name')))
        return True

    def _configure(self):
        """Configure model."""
        nemoa.log("configure model '%s'" % (self._config['name']))
        nemoa.log('set', indent = '+1')
        if not 'check' in self._config:
            self._config['check'] = {'dataset': False,
                'network': False, 'System': False}
        self._config['check']['dataset'] = \
            self.dataset.configure(network = self.network)
        if not self._config['check']['dataset']:
            nemoa.log('error', """could not configure model: dataset
                could not be configured!""")
            nemoa.log('set', indent = '-1')
            return False
        self._config['check']['network'] = \
            self.network._configure(dataset = self.dataset,
                system = self.system)
        if not self._config['check']['network']:
            nemoa.log('error', """could not configure model: network
                could not be configured!""")
            nemoa.log('set', indent = '-1')
            return False
        self._config['check']['system'] = \
            self.system.configure(
                network = self.network,
                dataset = self.dataset)
        if not self._config['check']['system']:
            nemoa.log('error', """could not configure model: system
                could not be configured!""")
            nemoa.log('set', indent = '-1')
            return False
        nemoa.log('set', indent = '-1')
        return True

    def _is_configured(self):
        """Return True if model is allready configured."""
        return 'check' in self._config \
            and self._config['check']['dataset'] \
            and self._config['check']['network'] \
            and self._config['check']['system']

    def _initialize(self):
        """Initialize model parameters and return self."""

        # TODO: check if system is configured

        # check if model is empty and can not be initialized
        if (self.dataset == None or self.system == None) \
            and self._is_empty(): return self

        # check if model is configured
        if not self._is_configured():
            return nemoa.log('error', """could not initialize model:
                model is not yet configured.""")

        # check dataset
        if not nemoa.type.is_dataset(self.dataset):
            return nemoa.log('error', """could not initialize model:
                dataset is not yet configured.""")

        # check system
        if not nemoa.type.is_system(self.system):
            return nemoa.log('error', """could not initialize model:
                system is not yet configured.""")

        # check if system is empty
        if self.system._is_empty(): return False

        # initialize system parameters with dataset
        self.system._initialize(self.dataset)

        # update network with initial system parameters
        self.network._update(system = self.system)

        return self

    def optimize(self, schedule = None, **kwargs):
        """Optimize system parameters."""

        nemoa.log('optimize model')
        nemoa.log('set', indent = '+1')

        # check if model is empty
        if self._is_empty():
            nemoa.log('warning', "empty models can not be optimized!")
            nemoa.log('set', indent = '-1')
            return self

        # check if model is configured
        if not self._is_configured():
            nemoa.log('error', """could not optimize model:
                model is not yet configured.""")
            nemoa.log('set', indent = '-1')
            return False

        # get optimization schedule
        if schedule == None:
            schedule = self.system.get('type') + '.default'
        elif not '.' in schedule:
            schedule = self.system.get('type') + '.' + schedule
        schedule = nemoa.workspace._get_config(
            type = 'schedule', config = schedule,
            merge = ['params', self.system.get('type')],
            **kwargs)
        if not schedule:
            nemoa.log('error', """could not optimize system parameters:
                optimization schedule is not valid!""")
            nemoa.log('set', indent = '-1')
            return self

        # optimization of system parameters
        nemoa.log("starting optimization schedule: '%s'"
            % (schedule['name']))
        nemoa.log('set', indent = '+1')

        # TODO: find better solution for multistage optimization
        if 'stage' in schedule and len(schedule['stage']) > 0:
            for stage, params in enumerate(config['stage']):
                self.system.optimize(self.dataset, **params)
        elif 'params' in schedule:
            self.system.optimize(
                dataset = self.dataset, schedule = schedule)

        nemoa.log('set', indent = '-1')

        self.network._update(system = self.system)
        nemoa.log('set', indent = '-1')

        return self

    def evaluate(self, *args, **kwargs):
        """Evaluate model."""

        if len(args) == 0:
            header = 'system'
            trailer = args
        else:
            header = args[0]
            trailer = args[1:]

        # Evaluate dataset
        if header == 'dataset':
            return self.dataset.evaluate(*trailer, **kwargs)

        # Evaluate network
        if header == 'network':
            return self.network.evaluate(*trailer, **kwargs)

        # Evaluate system
        if header == 'system':
            # get data for system evaluation
            if 'data' in kwargs.keys():
                # get data from keyword argument
                data = kwargs['data']
                del kwargs['data']
            else:
                # fetch data from dataset using parameters:
                # 'preprocessing', 'statistics'
                if 'preprocessing' in kwargs.keys():
                    preprocessing = kwargs['preprocessing']
                    del kwargs['preprocessing']
                else: preprocessing = {}
                if not isinstance(preprocessing, dict):
                    preprocessing = {}
                if preprocessing:
                    dataset_backup = self.dataset.get('backup')
                    self.dataset.preprocess(preprocessing)
                if 'statistics' in kwargs.keys():
                    statistics = kwargs['statistics']
                    del kwargs['statistics']
                else: statistics = 0
                cols = self.system.get('layers', visible = True)
                data = self.dataset.data(
                    size = statistics, cols = tuple(cols))
                if preprocessing:
                    self.dataset.set('backup', dataset_backup)

            return self.system.evaluate(data, *trailer, **kwargs)

        return nemoa.log('warning', 'could not evaluate model')

    def _get_backup(self, sec = None):
        dict = {
            'config': copy.deepcopy(self._config),
            'network': self.network.get('backup'),
            'dataset': self.dataset.get('backup'),
            'system': self.system.get('backup')
        }

        if not sec: return dict
        if sec in dict: return dict[sec]
        return None

    def _set_backup(self, dict):
        """Set configuration, parameters and data of model from given dictionary
        return true if no error occured"""

        # get config from dict
        model_backup = self._import_config_from_dict(dict)

        # check self
        if not nemoa.type.is_dataset(self.dataset):
            return nemoa.log('error', """could not configure dataset:
                model does not contain dataset instance.""")
        if not nemoa.type.is_network(self.network):
            return nemoa.log('error', """could not configure network:
                model does not contain network instance.""")
        if not nemoa.type.is_system(self.system):
            return nemoa.log('error', """could not configure system:
                model does not contain system instance.""")

        self._config = model_backup['config'].copy()
        self.network.set('backup', **model_backup['network'])
        self.dataset.set('backup', **model_backup['dataset'])

        # prepare
        # TODO: system.set('backup', ...) should do this
        if not 'update' in model_backup['system']['config']:
            model_backup['system']['config']['update'] = {'A': False}

        # TODO: system.set('backup', ...) shall create system and do
        # something like self.configure ...

        # create system
        self.system = nemoa.system.new(
            config = model_backup['system']['config'].copy(),
            network = self.network,
            dataset = self.dataset )
        self.system.set('backup', **model_backup['system'])

        return self

    def save(self, file = None):
        """Save model settings to file and return filepath."""

        nemoa.log('save model to file')
        nemoa.log('set', indent = '+1')

        # get filename
        if file == None:
            fileExt  = 'nmm'
            fileName = '%s.%s' % (self._config['name'], fileExt)
            filePath = nemoa.workspace.path('models')
            file = filePath + fileName
        file = nemoa.common.get_empty_file(file)

        # save model parameters and configuration to file
        nemoa.common.dict_to_file(self._get_backup(), file)

        # create console message
        nemoa.log("save model as: '%s'" %
            (os.path.basename(file)[:-(len(fileExt) + 1)]))

        nemoa.log('set', indent = '-1')
        return file

    def show(self, *args, **kwargs):
        """Create plot of model with output to display."""
        kwargs['output'] = 'show'
        return self.plot(*args, **kwargs)

    def plot(self, *args, **kwargs):
        """Create plot of model."""
        nemoa.log('create plot of model')
        nemoa.log('set', indent = '+1')

        # check args and kwargs
        if 'output' in kwargs:
            output = kwargs['output']
            del(kwargs['output'])
        else: output = 'file'
        if 'file' in kwargs:
            file = kwargs['file']
            del(kwargs['file'])
        else: file = None
        if len(args): plot = args[0]
        else: plot = None

        # check if model is configured
        if not self._is_configured():
            nemoa.log('error', """could not create plot of model:
                model is not yet configured!""")
            nemoa.log('set', indent = '-1')
            return False

        # get plot instance
        nemoa.log('create plot instance')
        nemoa.log('set', indent = '+1')

        if plot == None: plot = self.system.get('type') + '.default'
        if isinstance(plot, str):
            plotName, plotParams = nemoa.common.str_split_params(plot)
            mergeDict = plotParams
            for param in kwargs.keys(): plotParams[param] = kwargs[param]
            objPlot = self._get_plot(*args, params = plotParams)
            if not objPlot:
                nemoa.log('warning', "could not create plot: unknown configuration '%s'" % (plotName))
                nemoa.log('set', indent = '-1')
                return None
        elif isinstance(plot, dict): objPlot = self._get_plot(config = plot)
        else: objPlot = self._get_plot()
        if not objPlot: return None

        # prepare filename
        if output == 'display': file = None
        elif output == 'file' and not file:
            file = nemoa.common.get_empty_file(nemoa.workspace.path('plots') + \
                self._config['name'] + '/' + objPlot.cfg['name'] + \
                '.' + objPlot.settings['fileformat'])

        # create plot
        ret_val = objPlot.create(self, file = file)
        if not file == None: nemoa.log('save plot: ' + file)

        nemoa.log('set', indent = '-2')
        return ret_val

    def _get_plot(self, *args, **kwargs):
        """Return new plot instance"""

        # return empty plot instance if no configuration was given
        if not args and not 'config' in kwargs: return nemoa.plot.new()

        if 'params' in kwargs:
            params = kwargs['params']
            del(kwargs['params'])
        else: params = None
        if 'config' in kwargs:
            config = kwargs['config']
            del(kwargs['config'])
        else: config = None
        options = kwargs

        # get plot configuration from plot name
        if isinstance(args[0], str):
            cfg = None

            # search for given configuration
            for plot in [args[0],
                '%s.%s' % (self.system.get('type'), args[0]),
                'base.' + args[0]]:
                cfg = nemoa.workspace.get('plot', \
                   name = plot, params = params)
                if isinstance(cfg, dict): break

            # search in model / system relations
            if not isinstance(cfg, dict):
                if args[0] == 'dataset':
                    cfg = nemoa.common.dict_merge(params, {
                        'package': 'dataset',
                        'class': 'histogram',
                        'params': {},
                        'description': 'data distribution',
                        'name': 'distribution',
                        'id': 0})
                elif args[0] == 'network':
                    cfg = nemoa.common.dict_merge(params, {
                        'package': 'network',
                        'class': 'graph',
                        'params': {},
                        'description': '',
                        'name': 'structure',
                        'id': 0})
                elif args[0] == 'system':
                    if len(args) == 1:
                        pass #2Do
                    elif args[1] == 'relations':
                        if len(args) == 2:
                            pass
                        elif args[2] in self.about('system',
                            'relations').keys():
                            relation = self.about('system',
                                'relations')[args[2]]
                            if len(args) > 3: rel_class = args[3]
                            else: rel_class = relation['show']
                            cfg = nemoa.common.dict_merge(params, {
                                'package': 'system',
                                'class': rel_class,
                                'params': {'relation': args[0]},
                                'description': relation['description'],
                                'name': relation['name'],
                                'id': 0})
                elif args[0] in self.about('system', 'relations').keys():
                    relation = self.about('system', 'relations')[args[0]]
                    if len(args) > 1: rel_class = args[1]
                    else: rel_class = relation['show']
                    cfg = nemoa.common.dict_merge(params, {
                        'package': 'system',
                        'class': rel_class,
                        'params': {'relation': args[0]},
                        'description': relation['description'],
                        'name': relation['name'],
                        'id': 0})

            # could not find configuration
            if not isinstance(cfg, dict):
                return nemoa.log('error', """could not create plot:
                    unsupported plot '%s'""" % (args[0]))
        elif isinstance(config, dict): cfg = config

        # overwrite config with given params
        if isinstance(params, dict):
            for key in params.keys(): cfg['params'][key] = params[key]

        return nemoa.plot.new(config = cfg)


    def _is_empty(self):
        """Return true if model is empty."""
        return not 'name' in self._config or not self._config['name']

    def get(self, key = None, *args, **kwargs):

        if key == 'name': return self._config['name']
        if key == 'about': return self.__doc__
        if key == 'backup': return self._get_backup(*args, **kwargs)
        if key == 'network': return self.network.get(*args, **kwargs)
        if key == 'dataset': return self.dataset.get(*args, **kwargs)
        if key == 'system': return self.system.get(*args, **kwargs)

        if not key == None: return nemoa.log('warning',
            "unknown key '%s'" % (key))
        return None

    def set(self, key = None, *args, **kwargs):

        if key == 'name': return self._set_name(*args, **kwargs)
        if key == 'backup': return self._set_backup(*args, **kwargs)

        if not key == None: return nemoa.log('warning',
            "unknown key '%s'" % (key))
        return None

    def _set_name(self, name):
        """Set name of model."""

        if not isinstance(self._config, dict): return False
        self._config['name'] = name
        return True

    def about(self, *args):
        """Return generic information about various parts of the model.

        Arg:
            *args: tuple of strings, containing a breadcrump trail to
                a specific information about the model

        Examples:
            Get a description of the "error" measurement function of the
            systems units:
                model.about('system', 'units', 'error', 'description')

        """

        if not args: return {
            'name': self._config['name'],
            'description': '',
            'dataset': self.dataset.about(*args[1:]),
            'network': self.network.about(*args[1:]),
            'system': self.system.about(*args[1:])
        }

        if args[0] == 'name': return self._config['name']
        if args[0] == 'description': return ''
        if args[0] == 'dataset': return self.dataset.get(*args[1:])
        if args[0] == 'network': return self.network.get(*args[1:])
        if args[0] == 'system': return self.system.about(*args[1:])

        return None
