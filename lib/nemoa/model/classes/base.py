# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import copy
import os

from nemoa.common import nclass, nbase

class Model(nbase.ObjectIP):
    """Model base class.

    Attributes:
        about (str): Short description of the content of the resource.
            Hint: Read- & writeable wrapping attribute to get('about')
                and set('about', str).
        accuracy (numpy.float64): Average reconstruction accuracy of
            output units, defined by:
                accuracy := 1 - mean(residuals) / mean(data)
            Hint: Readonly wrapping attribute to get('accuracy')
        author (str): A person, an organization, or a service that is
            responsible for the creation of the content of the resource.
            Hint: Read- & writeable wrapping attribute to get('author')
                and set('author', str).
        branch (str): Name of a duplicate of the original resource.
            Hint: Read- & writeable wrapping attribute to get('branch')
                and set('branch', str).
        dataset (dataset instance):
        email (str): Email address to a person, an organization, or a
            service that is responsible for the content of the resource.
            Hint: Read- & writeable wrapping attribute to get('email')
                and set('email', str).
        error (numpy.float64): Average reconstruction error of
            output units, defined by:
                error := mean(residuals)
            Hint: Readonly wrapping attribute to get('error')
        fullname (str): String concatenation of name, branch and
            version. Branch and version are only conatenated if they
            exist.
            Hint: Readonly wrapping attribute to get('fullname')
        license (str): Namereference to a legal document giving official
            permission to do something with the resource.
            Hint: Read- & writeable wrapping attribute to get('license')
                and set('license', str).
        name (str): Name of the resource.
            Hint: Read- & writeable wrapping attribute to get('name')
                and set('name', str).
        network (network instance):
        path (str):
            Hint: Read- & writeable wrapping attribute to get('path')
                and set('path', str).
        precision (numpy.float64): Average reconstruction precision
            of output units defined by:
                precision := 1 - dev(residuals) / dev(data).
            Hint: Readonly wrapping attribute to get('precision')
        system (system instance):
        type (str): String concatenation of module name and class name
            of the instance.
            Hint: Readonly wrapping attribute to get('type')
        version (int): Versionnumber of the resource.
            Hint: Read- & writeable wrapping attribute to get('version')
                and set('version', int).

    """

    dataset  = None
    network  = None
    system   = None

    _config  = None
    _default = {}
    _attr    = { 'error': 'r', 'accuracy': 'r', 'precision': 'r' }

    def configure(self):
        """Configure model."""

        if not nclass.hasbase(self.dataset, 'Dataset'):
            raise ValueError("dataset is not valid")
        if not nclass.hasbase(self.network, 'Network'):
            raise ValueError("network is not valid")
        if not nclass.hasbase(self.system, 'System'):
            raise ValueError("system is not valid")

        retval = True

        # configure dataset columns to network
        retval &= bool(self.dataset.configure(self.network))
        # configure network to restrict nodes to found columns
        retval &= bool(self.network.configure(self.dataset))
        # configure system to nodes in network
        retval &= bool(self.system.configure(self.network))

        return retval

    def initialize(self):
        """Initialize model parameters."""

        if not nclass.hasbase(self.dataset, 'Dataset'):
            raise ValueError("dataset is not valid")
        if not nclass.hasbase(self.network, 'Network'):
            raise ValueError("network is not valid")
        if not nclass.hasbase(self.system, 'System'):
            raise ValueError("system is not valid")

        retval = True

        # initialize dataset to system including normalization
        retval &= bool(self.dataset.initialize(self.system))
        # initialize system parameters by using statistics from dataset
        retval &= bool(self.system.initialize(self.dataset))
        # initialize network parameters with system parameters
        retval &= bool(self.network.initialize(self.system))

        return retval

    def optimize(self, *args, **kwargs):
        """Optimize model parameters."""

        return nemoa.model.optimize(self, *args, **kwargs)

    def get(self, *args, **kwargs):
        """Get meta information and content."""
        return super(Model, self).get(*args, **kwargs)

    def _get_error(self):
        """Evaluate model error."""
        return self.evaluate('system', 'error')

    def _get_accuracy(self):
        """Evaluate model accuracy."""
        return self.evaluate('system', 'accuracy')

    def _get_precision(self):
        """Evaluate model precision."""
        return self.evaluate('system', 'precision')

    def _get_algorithms(self, *args, **kwargs):
        """Get algorithms provided by model."""
        return {
            'dataset': self.dataset._get_algorithms(*args, **kwargs),
            'network': self.network._get_algorithms(*args, **kwargs),
            'system': self.system._get_algorithms(*args, **kwargs) }

    def _get_algorithms_new(self, *args, **kwargs):
        """Get algorithms provided by model."""
        return {
            'dataset': self.dataset._get_algorithms(*args, **kwargs),
            'network': self.network._get_algorithms(*args, **kwargs),
            'system': self.system._get_algorithms_new(*args, **kwargs) }

    def _get_algorithm(self, *args, **kwargs):
        """Get algorithm."""

        # search algorithm
        found = [self.dataset._get_algorithm(*args, **kwargs),
            self.network._get_algorithm(*args, **kwargs),
            self.system._get_algorithm(*args, **kwargs)]

        # filter results
        found = [x for x in found if x is not None]

        if len(found) == 0: return None
        if len(found) > 1: raise ValueError(
            "algorithm with name '%s' is not unique: "
            "use keyword argument 'category'." % args[0])

        return found[0]

    def _get_copy(self, key = None, *args, **kwargs):
        """Get model copy as dictionary."""

        if key is None: return {
            'config': self._get_config(),
            'dataset': self._get_dataset(),
            'network': self._get_network(),
            'system': self._get_system()
        }

        if key == 'config': return self._get_config(*args, **kwargs)
        if key == 'dataset': return self._get_dataset(*args, **kwargs)
        if key == 'network': return self._get_network(*args, **kwargs)
        if key == 'system': return self._get_system(*args, **kwargs)

        raise ValueError(
            "could not get copy of configuration: "
            "unknown section '%s'." % key)

    def _get_config(self, key = None, *args, **kwargs):
        """Get configuration or configuration value."""

        if key is None: return copy.deepcopy(self._config)

        if isinstance(key, str) and key in list(self._config.keys()):
            if isinstance(self._config[key], dict):
                return self._config[key].copy()
            return self._config[key]

        raise ValueError("""could not get configuration:
            unknown key '%s'.""" % key)

    def _get_dataset(self, type = 'dict'):
        """ """

        if type == 'dataset': return self.dataset.copy()
        if type == 'dict': return self.dataset.get('copy')

        raise Warning(
            "could not get dataset: unknown type '%s'." % type) or None

    def _get_network(self, type = 'dict'):
        """ """

        if type == 'network': return self.network.copy()
        if type == 'dict': return self.network.get('copy')

        raise Warning(
            "could not get network: unknown type '%s'." % type) or None

    def _get_system(self, type: str = 'dict'):
        """ """

        if type == 'system': return self.system.copy()
        if type == 'dict': return self.system.get('copy')

        raise Warning(
            "could not get system: unknown type '%s'." % type) or None

    def _get_sample(self, *args, **kwargs):
        """ """

        # fetch data from dataset using parameters:
        # 'preprocessing', 'statistics'
        if 'preprocessing' in list(kwargs.keys()):
            preprocessing = kwargs['preprocessing']
            del kwargs['preprocessing']
        else: preprocessing = {}
        if not isinstance(preprocessing, dict):
            preprocessing = {}
        if preprocessing:
            dataset_backup = self.dataset.get('copy')
            self.dataset.preprocess(preprocessing)
        if 'statistics' in list(kwargs.keys()):
            statistics = kwargs['statistics']
            del kwargs['statistics']
        else: statistics = 0
        cols = self.system.get('layers', visible = True)
        data = self.dataset.get('data',
            size = statistics, cols = tuple(cols))
        if preprocessing:
            self.dataset.set('copy', dataset_backup)

        return data

    def set(self, key = None, *args, **kwargs):
        """Set meta information and parameters of model."""

        # # set meta information
        # if key in self._attr_meta: return self._set_meta(key, *args, **kwargs)

        # setter methods for meta information attributes
        if key in self._attr_meta and self._attr_meta[key] & 0b10:
            return getattr(self, '_set_' + key)(*args, **kwargs)

        # set model parameters
        if key == 'network': return self.network.set(*args, **kwargs)
        if key == 'dataset': return self.dataset.set(*args, **kwargs)
        if key == 'system': return self.system.set(*args, **kwargs)

        # import configuration
        if key == 'copy': return self._set_copy(*args, **kwargs)
        if key == 'config': return self._set_config(*args, **kwargs)

        raise Warning("unknown key '%s'." % key)

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

        from nemoa.common import ndict

        # initialize or update configuration dictionary
        if not hasattr(self, '_config') or not self._config:
            self._config = self._default.copy()
        if config: self._config = ndict.merge(config, self._config)
        return True

    def _set_dataset(self, dataset):
        """Set dataset to model.

        Create a new dataset from dataset dictionary or reconfigure
        existing dataset with dataset dictionary or copy a dataset
        instance.

        Args:
            dataset (dict or dataset instance): dataset dictionary
                or dataset instance

        Returns:
            bool: True if no error occured

        """

        if nclass.hasbase(dataset, 'Dataset'):
            self.dataset = dataset
            return True

        if not isinstance(dataset, dict): return False

        if nclass.hasbase(self.dataset, 'Dataset'):
            return self.dataset.set('copy', **dataset)

        self.dataset = nemoa.dataset.new(**dataset)

        return True

    def _set_network(self, network):
        """Set network to model.

        Create a new network from network dictionary or reconfigure
        existing network with network dictionary or copy a network
        instance.

        Args:
            network (dict or network instance): network dictionary
                or network instance

        Returns:
            bool: True if no error occured

        """

        if nclass.hasbase(network, 'Network'):
            self.network = network
            return True

        if not isinstance(network, dict): return False

        if nclass.hasbase(self.network, 'Network'):
            return self.network.set('copy', **network)

        self.network = nemoa.network.new(**network)

        return True

    def _set_system(self, system):
        """Set system to model.

        Create a new system from system dictionary or reconfigure
        existing system with system dictionary or copy a system
        instance.

        Args:
            system (dict or system instance): system dictionary
                or system instance

        Returns:
            bool: True if no error occured

        """

        if nclass.hasbase(system, 'System'):
            self.system = system
            return True

        if not isinstance(system, dict): return False

        if nclass.hasbase(self.system, 'System'):
            return self.system.set('copy', **system)

        self.system = nemoa.system.new(**system)

        return True

    def evaluate(self, key = None, *args, **kwargs):
        """Evaluate model."""

        # 2do: evaluate('correlation', *args, **kwargs)
        # 1. get algorithm 'correlation' as func
        # 2a. for datasets -> func(dataset, *args, **kwargs)
        # 2b. for networks -> func(network, *args, **kwargs)
        # 2c. for models ->  func(model, *args, **kwargs)



        if not key: key = 'system'

        # evaluate dataset
        if key == 'dataset':
            return self.dataset.evaluate(*args, **kwargs)
        if key == 'network':
            return self.network.evaluate(*args, **kwargs)
        if key == 'system':

            # get data for system evaluation
            if 'data' in list(kwargs.keys()):
                # get data from keyword argument
                data = kwargs.pop('data')
            else:
                data = self._get_sample(*args, **kwargs)
                kwargs.pop('preprocessing', None)
                kwargs.pop('statistics', None)

            return self.system.evaluate(data, *args, **kwargs)

        raise Warning(
            "could not evaluate model: "
            "evaluation key '%s' is not supported." % key)

    def save(self, *args, **kwargs):
        """Export model to file."""
        return nemoa.model.save(self, *args, **kwargs)

    def show(self, *args, **kwargs):
        """Show model as image."""
        return nemoa.model.show(self, *args, **kwargs)

    def copy(self, *args, **kwargs):
        """Create copy of model."""
        return nemoa.model.copy(self, *args, **kwargs)
