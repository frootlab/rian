# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import copy
import os

class Model:
    """nemoa model class.

    Attributes:
        dataset (dataset instance):
        network (network instance):
        system (system instance):

    """

    _default = {}
    _config = None

    dataset = None
    network = None
    system = None

    def __init__(self, **kwargs):
        """Initialize model and configure dataset, network and system."""

        self._set_copy(**kwargs)
        self.dataset.configure(network = self.network)
        self.network._configure(dataset = self.dataset,
            system = self.system)
        self.system.configure(network = self.network)

    def _configure(self):
        """Configure model."""
        nemoa.log("configure model '%s'" % (self._config['name']))
        nemoa.log('set', indent = '+1')
        if not 'check' in self._config:
            self._config['check'] = {'dataset': False,
                'network': False, 'system': False}
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
            self.system.configure(network = self.network)
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
        self.system.initialize(self.dataset)

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

    #def save(self, file = None):
        #"""Save model settings to file and return filepath."""

        #nemoa.log('save model to file')
        #nemoa.log('set', indent = '+1')

        ## get filename
        #if file == None:
            #file_ext = 'nmm'
            #file_name = '%s.%s' % (self._config['name'], file_ext)
            #file_path = nemoa.workspace.path('models')
            #file = file_path + file_name
        #file = nemoa.common.get_unused_file_path(file)

        ## save model parameters and configuration to file
        #nemoa.common.dict_to_file(self._get_copy(), file)

        ## create console message
        #nemoa.log("save model as: '%s'" %
            #(os.path.basename(file)[:-(len(file_ext) + 1)]))

        #nemoa.log('set', indent = '-1')
        #return file

    #def show(self, key = None, *args, **kwargs):
        #"""Create plot of model with output to display."""

        #if key == 'network': return self.network.show(*args, **kwargs)
        #if key == 'dataset': return self.dataset.show(*args, **kwargs)

        #kwargs['output'] = 'show'
        #return self.plot(key, *args, **kwargs)



    def _is_empty(self):
        """Return true if model is empty."""
        return not 'name' in self._config or not self._config['name']

    def get(self, key = 'name', *args, **kwargs):
        """Get meta information and parameters of model."""

        # get meta information
        if key == 'fullname': return self._get_fullname()
        if key == 'name': return self._get_name()
        if key == 'branch': return self._get_branch()
        if key == 'version': return self._get_version()
        if key == 'about': return self._get_about()
        if key == 'author': return self._get_author()
        if key == 'email': return self._get_email()
        if key == 'license': return self._get_license()
        if key == 'type': return self._get_type()

        # get information about model parameters
        if key == 'network': return self.network.get(*args, **kwargs)
        if key == 'dataset': return self.dataset.get(*args, **kwargs)
        if key == 'system': return self.system.get(*args, **kwargs)

        # export configuration and parameters
        if key == 'copy': return self._get_copy(*args, **kwargs)
        if key == 'config': return self._get_config(*args, **kwargs)

        return nemoa.log('warning', "unknown key '%s'" % (key))

    def _get_fullname(self):
        """Get fullname of model."""
        fullname = ''
        name = self._get_name()
        if name: fullname += name
        branch = self._get_branch()
        if branch: fullname += '.' + branch
        version = self._get_version()
        if version: fullname += '.' + str(version)
        return fullname

    def _get_name(self):
        """Get name of model."""
        if 'name' in self._config: return self._config['name']
        return None

    def _get_branch(self):
        """Get branch of model."""
        if 'branch' in self._config: return self._config['branch']
        return None

    def _get_version(self):
        """Get version number of model branch."""
        if 'version' in self._config: return self._config['version']
        return None

    def _get_about(self):
        """Get description of model."""
        if 'about' in self._config: return self._config['about']
        return None

    def _get_author(self):
        """Get author of model."""
        if 'author' in self._config: return self._config['author']
        return None

    def _get_email(self):
        """Get email of author of model."""
        if 'email' in self._config: return self._config['email']
        return None

    def _get_license(self):
        """Get license of model."""
        if 'license' in self._config: return self._config['license']
        return None

    def _get_type(self):
        """Get type of model, using module and class name."""
        module_name = self.__module__.split('.')[-1]
        class_name = self.__class__.__name__
        return module_name + '.' + class_name

    def _get_copy(self, key = None, *args, **kwargs):
        """Get model copy as dictionary."""

        if key == None: return {
            'config': self._get_config(),
            'dataset': self._get_dataset(),
            'network': self._get_network(),
            'system': self._get_system()
        }

        if key == 'config': return self._get_config(*args, **kwargs)
        if key == 'dataset': return self._get_dataset(*args, **kwargs)
        if key == 'network': return self._get_network(*args, **kwargs)
        if key == 'system': return self._get_system(*args, **kwargs)

        return nemoa.log('error', """could not get copy of
            configuration: unknown section '%s'.""" % (key))

    def _get_config(self, key = None, *args, **kwargs):
        """Get configuration or configuration value."""

        if key == None: return copy.deepcopy(self._config)

        if isinstance(key, str) and key in self._config.keys():
            if isinstance(self._config[key], dict):
                return self._config[key].copy()
            return self._config[key]

        return nemoa.log('error', """could not get configuration:
            unknown key '%s'.""" % (key))

    def _get_dataset(self, type = 'dict'):

        if type == 'dataset': return self.dataset.copy()
        if type == 'dict': return self.dataset.get('copy')

    def _get_network(self, type = 'dict'):

        if type == 'network': return self.network.copy()
        if type == 'dict': return self.network.get('copy')

    def _get_system(self, type = 'dict'):

        if type == 'dataset': return self.system.copy()
        if type == 'dict': return self.system.get('copy')

    def set(self, key = None, *args, **kwargs):
        """Set meta information and parameters of model."""

        # set meta information
        if key == 'name': return self._set_name(*args, **kwargs)
        if key == 'branch': return self._set_branch(*args, **kwargs)
        if key == 'version': return self._set_version(*args, **kwargs)
        if key == 'about': return self._set_about(*args, **kwargs)
        if key == 'author': return self._set_author(*args, **kwargs)
        if key == 'email': return self._set_email(*args, **kwargs)
        if key == 'license': return self._set_license(*args, **kwargs)

        # set model parameters
        if key == 'network': return self.network.set(*args, **kwargs)
        if key == 'dataset': return self.dataset.set(*args, **kwargs)
        if key == 'system': return self.system.set(*args, **kwargs)

        # import configuration
        if key == 'copy': return self._set_copy(*args, **kwargs)
        if key == 'config': return self._set_config(*args, **kwargs)

        return nemoa.log('warning', "unknown key '%s'" % (key))

    def _set_name(self, name):
        """Set name of model."""
        if not isinstance(name, str): return False
        self._config['name'] = name
        return True

    def _set_branch(self, branch):
        """Set branch of model."""
        if not isinstance(branch, str): return False
        self._config['branch'] = branch
        return True

    def _set_version(self, version):
        """Set version number of model branch."""
        if not isinstance(version, int): return False
        self._config['version'] = version
        return True

    def _set_about(self, about):
        """Get description of model."""
        if not isinstance(about, str): return False
        self._config['about'] = about
        return True

    def _set_author(self, author):
        """Set author of model."""
        if not isinstance(author, str): return False
        self._config['author'] = author
        return True

    def _set_email(self, email):
        """Set email of author of model."""
        if not isinstance(email, str): return False
        self._config['email'] = email
        return True

    def _set_license(self, model_license):
        """Set license of model."""
        if not isinstance(model_license, str): return False
        self._config['license'] = model_license
        return True

    def _set_copy(self, config = None, dataset = None, network = None,
        system = None):
        """Set configuration, parameters and data of model.

        Args:
            config (dict or None, optional): model configuration
            dataset (dict or None, optional): dataset copy as dictionary
            network (dict or None, optional): network copy as dictionary
            system (dict or None, optional): system copy as dictionary

        Returns:
            Bool which is True if and only if no error occured.

        """

        retval = True

        if config: retval &= self._set_config(config)
        if dataset: retval &= self._set_dataset(dataset)
        if network: retval &= self._set_network(network)
        if system: retval &= self._set_system(system)

        return retval

    def _set_config(self, config = None):
        """Set configuration from dictionary."""

        # initialize or update configuration dictionary
        if not hasattr(self, '_config') or not self._config:
            self._config = self._default.copy()
        if config:
            config_copy = copy.deepcopy(config)
            nemoa.common.dict_merge(config_copy, self._config)
        return True

    def _set_dataset(self, dataset):
        """Configure dataset from dictionary."""
        if nemoa.type.is_dataset(dataset):
            self.dataset = dataset
            return True
        if not nemoa.type.is_dataset(self.dataset):
            return nemoa.log('error', """could not configure dataset:
                model does not contain dataset instance.""")
        return self.dataset.set('copy', **dataset)

    def _set_network(self, network):
        """Configure network from dictionary."""
        if nemoa.type.is_network(network):
            self.network = network
            return True
        if not nemoa.type.is_network(self.network):
            return nemoa.log('error', """could not configure network:
                model does not contain network instance.""")
        return self.network.set('copy', **network)

    def _set_system(self, system):
        """Configure system from dictionary."""
        if nemoa.type.is_system(system):
            self.system = system
            return True
        if not nemoa.type.is_dataset(self.dataset):
            return nemoa.log('error', """could not configure system:
                model does not contain dataset instance.""")
        if not nemoa.type.is_network(self.network):
            return nemoa.log('error', """could not configure system:
                model does not contain network instance.""")

        self.system = nemoa.system.new(
            config = system_copy['config'], network = self.network)

        return self.system.set('copy', **system)

    def save(self, *args, **kwargs):
        """Export model to file."""
        return nemoa.model.save(self, *args, **kwargs)

    def show(self, *args, **kwargs):
        """Show model as image."""
        return nemoa.model.show(self, *args, **kwargs)

    def copy(self, *args, **kwargs):
        """Create copy of model."""
        return nemoa.model.copy(self, *args, **kwargs)
