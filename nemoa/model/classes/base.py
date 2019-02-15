# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

from typing import Any, Dict
from flab.base import otree
import nemoa
from nemoa.base import nbase

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

    _attr: Dict[str, int] = {
        'error': 0b01, 'accuracy': 0b01, 'precision': 0b01
    }

    _copy: Dict[str, str] = {
        'dataset': 'dataset', 'network': 'network', 'system': 'system'
    }

    def __init__(self, *args: Any, **kwds: Any) -> None:
        """Initialize model with content from arguments."""

        # get attribute and storage defaults from parent
        self._attr = {**getattr(super(), '_attr', {}), **self._attr}
        self._copy = {**getattr(super(), '_copy', {}), **self._copy}

        super().__init__(*args, **kwds)

    def configure(self):
        """Configure model."""

        if not otree.has_base(self.dataset, 'Dataset'):
            raise ValueError("dataset is not valid")
        if not otree.has_base(self.network, 'Network'):
            raise ValueError("network is not valid")
        if not otree.has_base(self.system, 'System'):
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

        if not otree.has_base(self.dataset, 'Dataset'):
            raise ValueError("dataset is not valid")
        if not otree.has_base(self.network, 'Network'):
            raise ValueError("network is not valid")
        if not otree.has_base(self.system, 'System'):
            raise ValueError("system is not valid")

        retval = True

        # initialize dataset to system including normalization
        retval &= bool(self.dataset.initialize(self.system))
        # initialize system parameters by using statistics from dataset
        retval &= bool(self.system.initialize(self.dataset))
        # initialize network parameters with system parameters
        retval &= bool(self.network.initialize(self.system))

        return retval

    def optimize(self, *args, **kwds):
        """Optimize model parameters."""
        return nemoa.model.optimize(self, *args, **kwds)

    def get(self, *args, **kwds):
        """Get meta information and content."""
        return super().get(*args, **kwds)

    def _get_error(self):
        """Evaluate model error."""
        return self.evaluate('system', 'error')

    def _get_accuracy(self):
        """Evaluate model accuracy."""
        return self.evaluate('system', 'accuracy')

    def _get_precision(self):
        """Evaluate model precision."""
        return self.evaluate('system', 'precision')

    def _get_algorithms(self, *args, **kwds):
        """Get algorithms provided by model."""
        return {
            'dataset': self.dataset._get_algorithms(*args, **kwds),
            'network': self.network._get_algorithms(*args, **kwds),
            'system': self.system._get_algorithms(*args, **kwds) }

    def _get_algorithms_new(self, *args, **kwds):
        """Get algorithms provided by model."""
        return {
            'dataset': self.dataset._get_algorithms(*args, **kwds),
            'network': self.network._get_algorithms(*args, **kwds),
            'system': self.system._get_algorithms_new(*args, **kwds) }

    def _get_algorithm(self, *args, **kwds):
        """Get algorithm."""

        # search algorithm
        found = [self.dataset._get_algorithm(*args, **kwds),
            self.network._get_algorithm(*args, **kwds),
            self.system._get_algorithm(*args, **kwds)]

        # filter results
        found = [x for x in found if x is not None]

        if len(found) == 0: return None
        if len(found) > 1: raise ValueError(
            "algorithm with name '%s' is not unique: "
            "use keyword argument 'category'." % args[0])

        return found[0]

    def _get_dataset(self, type = 'dict'):
        """ """

        if type == 'dataset': return self.dataset.copy()
        if type == 'dict': return self.dataset.get('copy')

        raise ValueError(f"type '{str(type)}' is not valid")

    def _get_network(self, type = 'dict'):
        """ """

        if type == 'network': return self.network.copy()
        if type == 'dict': return self.network.get('copy')

        raise ValueError(f"type '{str(type)}' is not valid")

    def _get_system(self, type: str = 'dict'):
        """ """

        if type == 'system': return self.system.copy()
        if type == 'dict': return self.system.get('copy')

        raise ValueError(f"type '{str(type)}' is not valid")

    def _get_sample(self, *args, **kwds):
        """ """

        # fetch data from dataset using parameters:
        # 'preprocessing', 'statistics'
        if 'preprocessing' in list(kwds.keys()):
            preprocessing = kwds['preprocessing']
            del kwds['preprocessing']
        else: preprocessing = {}
        if not isinstance(preprocessing, dict):
            preprocessing = {}
        if preprocessing:
            dataset_backup = self.dataset.get('copy')
            self.dataset.preprocess(preprocessing)
        if 'statistics' in list(kwds.keys()):
            statistics = kwds['statistics']
            del kwds['statistics']
        else: statistics = 0
        cols = self.system.get('layers', visible = True)
        data = self.dataset.get('data',
            size = statistics, cols = tuple(cols))
        if preprocessing:
            self.dataset.set('copy', dataset_backup)

        return data

    def set(self, key = None, *args, **kwds):
        """Set meta information and parameters of model."""

        # set writeable attributes
        if self._attr.get(key, 0b00) & 0b10:
            return getattr(self, '_set_' + key)(*args, **kwds)

        # set model parameters
        if key == 'network': return self.network.set(*args, **kwds)
        if key == 'dataset': return self.dataset.set(*args, **kwds)
        if key == 'system': return self.system.set(*args, **kwds)

        # import configuration
        if key == 'copy': return self._set_copy(*args, **kwds)
        if key == 'config': return self._set_config(*args, **kwds)

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
        # initialize or update configuration dictionary
        if not hasattr(self, '_config') or not self._config:
            self._config = self._default.copy()
        if config:
            self._config = {**self._config, **config}
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

        if otree.has_base(dataset, 'Dataset'):
            self.dataset = dataset
            return True

        if not isinstance(dataset, dict): return False

        if otree.has_base(self.dataset, 'Dataset'):
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

        if otree.has_base(network, 'Network'):
            self.network = network
            return True

        if not isinstance(network, dict): return False

        if otree.has_base(self.network, 'Network'):
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

        if otree.has_base(system, 'System'):
            self.system = system
            return True

        if not isinstance(system, dict): return False

        if otree.has_base(self.system, 'System'):
            return self.system.set('copy', **system)

        self.system = nemoa.system.new(**system)

        return True

    def evaluate(self, key = None, *args, **kwds):
        """Evaluate model."""

        if not key: key = 'system'

        # evaluate dataset
        if key == 'dataset':
            return self.dataset.evaluate(*args, **kwds)
        if key == 'network':
            return self.network.evaluate(*args, **kwds)
        if key == 'system':

            # get data for system evaluation
            if 'data' in list(kwds.keys()):
                # get data from keyword argument
                data = kwds.pop('data')
            else:
                data = self._get_sample(*args, **kwds)
                kwds.pop('preprocessing', None)
                kwds.pop('statistics', None)

            return self.system.evaluate(data, *args, **kwds)

        raise Warning(
            "could not evaluate model: "
            "evaluation key '%s' is not supported." % key)

    def save(self, *args, **kwds):
        """Export model to file."""
        return nemoa.model.save(self, *args, **kwds)

    def show(self, *args, **kwds):
        """Show model as image."""
        return nemoa.model.show(self, *args, **kwds)

    def copy(self, *args, **kwds):
        """Create copy of model."""
        return nemoa.model.copy(self, *args, **kwds)
