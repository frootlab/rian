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

    def _export_data(self, *args, **kwargs):
        """Export data to file."""
        # copy dataset
        settings = self.dataset.get('copy')
        self.dataset._transform(system = self.system)
        self.dataset.export(*args, **kwargs)
        self.dataset.set('copy', settings)
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
                    dataset_backup = self.dataset.get('copy')
                    self.dataset.preprocess(preprocessing)
                if 'statistics' in kwargs.keys():
                    statistics = kwargs['statistics']
                    del kwargs['statistics']
                else: statistics = 0
                cols = self.system.get('layers', visible = True)
                data = self.dataset.get('data',
                    size = statistics, cols = tuple(cols))
                if preprocessing:
                    self.dataset.set('copy', dataset_backup)

            return self.system.evaluate(data, *trailer, **kwargs)

        return nemoa.log('warning', 'could not evaluate model')

    def save(self, file = None):
        """Save model settings to file and return filepath."""

        nemoa.log('save model to file')
        nemoa.log('set', indent = '+1')

        # get filename
        if file == None:
            file_ext = 'nmm'
            file_name = '%s.%s' % (self._config['name'], file_ext)
            file_path = nemoa.workspace.path('models')
            file = file_path + file_name
        file = nemoa.common.get_unused_file_path(file)

        # save model parameters and configuration to file
        nemoa.common.dict_to_file(self._get_copy(), file)

        # create console message
        nemoa.log("save model as: '%s'" %
            (os.path.basename(file)[:-(len(file_ext) + 1)]))

        nemoa.log('set', indent = '-1')
        return file

    def show(self, key = None, *args, **kwargs):
        """Create plot of model with output to display."""
        if key == 'network': return self.network.show(*args, **kwargs)

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
            plot_name, plot_params = nemoa.common.str_split_params(plot)
            merge_dict = plot_params
            for param in kwargs.keys(): plot_params[param] = kwargs[param]
            obj_plot = self._get_plot(*args, params = plot_params)
            if not obj_plot:
                nemoa.log('warning', "could not create plot: unknown configuration '%s'" % (plot_name))
                nemoa.log('set', indent = '-1')
                return None
        elif isinstance(plot, dict): obj_plot = self._get_plot(config = plot)
        else: obj_plot = self._get_plot()
        if not obj_plot: return None

        # prepare filename
        if output == 'display': file = None
        elif output == 'file' and not file:
            file = nemoa.common.get_unused_file_path(
                nemoa.workspace.path('plots') + \
                self._config['name'] + '/' + obj_plot.cfg['name'] + \
                '.' + obj_plot.settings['fileformat'])

        # create plot
        ret_val = obj_plot.create(self, file = file)
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
                        'about': 'data distribution',
                        'name': 'distribution',
                        'id': 0})
                elif args[0] == 'network':
                    cfg = nemoa.common.dict_merge(params, {
                        'package': 'network',
                        'class': 'graph',
                        'params': {},
                        'about': '',
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
                                'about': relation['about'],
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
                        'about': relation['about'],
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

        # get generic information about model
        if key == 'name': return self._get_name()
        if key == 'type': return self._get_type()
        if key == 'about': return self._get_about()

        # get information about model parameters
        if key == 'network': return self.network.get(*args, **kwargs)
        if key == 'dataset': return self.dataset.get(*args, **kwargs)
        if key == 'system': return self.system.get(*args, **kwargs)

        # get copy of model configuration and parameters
        if key == 'copy': return self._get_copy(*args, **kwargs)

        return nemoa.log('warning', "unknown key '%s'" % (key))

    def _get_name(self):
        """Get name of model."""
        return self._config['name'] if 'name' in self._config else None

    def _get_type(self):
        """Get type of model, using module and class name."""
        module_name = self.__module__.split('.')[-1]
        class_name = self.__class__.__name__
        return module_name + '.' + class_name

    def _get_about(self):
        """Get docstring of model."""
        return self.__doc__

    def _get_copy(self, section = None, *args, **kwargs):
        """Get model copy as dictionary."""
        if section == None: return {
            'config': copy.deepcopy(self._config),
            'dataset': self.dataset.get('copy'),
            'network': self.network.get('copy'),
            'system': self.system.get('copy') }
        elif section == 'dataset':
            return self.dataset.get('copy', *args, **kwargs)
        elif section == 'network':
            return self.network.get('copy', *args, **kwargs)
        elif section == 'system':
            return self.system.get('copy', *args, **kwargs)
        return nemoa.log('error', """could not get copy of
            configuration: unknown section '%s'.""" % (section))

    def set(self, key = None, *args, **kwargs):

        if key == 'name': return self._set_name(*args, **kwargs)
        if key == 'copy': return self._set_copy(*args, **kwargs)

        if not key == None: return nemoa.log('warning',
            "unknown key '%s'" % (key))
        return None

    def _set_name(self, name):
        """Set name of model."""
        if not isinstance(name, str): return False
        self._config['name'] = name
        return True

    def _set_copy(self, **kwargs):
        """Set configuration, parameters and data of model.

        Returns:
            Bool which is True if and only if no error occured.

        """

        ret_val = True

        if 'config' in kwargs:
            ret_val &= self._set_config(kwargs['config'])
        if 'dataset' in kwargs:
            ret_val &= self._set_dataset(kwargs['dataset'])
        if 'network' in kwargs:
            ret_val &= self._set_network(kwargs['network'])
        if 'system' in kwargs:
            ret_val &= self._set_system(kwargs['system'])

        return ret_val

    def _set_config(self, config = None):
        """Set configuration from dictionary."""

        # initialize or update configuration dictionary
        if not hasattr(self, '_config') or not self._config:
            self._config = self._default.copy()
        if config:
            config_copy = copy.deepcopy(config)
            nemoa.common.dict_merge(config_copy, self._config)
        return True

    def _set_dataset(self, dataset_copy):
        """Configure dataset from dictionary."""
        if not nemoa.type.is_dataset(self.dataset):
            return nemoa.log('error', """could not configure dataset:
                model does not contain dataset instance.""")
        return self.dataset.set('copy', **dataset_copy)

    def _set_network(self, network_copy):
        """Configure network from dictionary."""
        if not nemoa.type.is_network(self.network):
            return nemoa.log('error', """could not configure network:
                model does not contain network instance.""")
        return self.network.set('copy', **network_copy)

    def _set_system(self, system_copy):
        """Configure system from dictionary."""
        if not nemoa.type.is_dataset(self.dataset):
            return nemoa.log('error', """could not configure system:
                model does not contain dataset instance.""")
        if not nemoa.type.is_network(self.network):
            return nemoa.log('error', """could not configure system:
                model does not contain network instance.""")

        # TODO: make copy of system if allready exists
        # create system
        self.system = nemoa.system.new(
            config = system_copy['config'],
            network = self.network,
            dataset = self.dataset )

        return self.system.set('copy', **system_copy)

    def about(self, *args):
        """Return generic information about various parts of the model.

        Args:
            *args: tuple of strings, containing a breadcrump trail to
                a specific information about the model

        Examples:
            Get a description of the "error" measurement function of the
            systems units:
                model.about('system', 'units', 'error', 'about')

        """

        if not args: return {
            'system': self.system.about(*args[1:])
        }

        if args[0] == 'system': return self.system.about(*args[1:])

        return None
