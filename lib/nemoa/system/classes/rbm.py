# -*- coding: utf-8 -*-
"""Restricted Boltzmann Machine class networks.

Various classes of restricted boltzmann machines aimed for data modeling
and per layer pretraining of multilayer feedforward artificial neural
networks
"""

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.system.classes.ann
import numpy

class RBM(nemoa.system.classes.ann.ANN):
    """Restricted Boltzmann Machine (RBM).

    Restricted Boltzmann Machines (1) are energy based undirected
    artificial neuronal networks with two layers with visible and
    hidden units. The visible layer contains binary distributed
    sigmoidal units to model data. The hidden layer contains binary
    distributed sigmoidal units to model data relations.

    Reference:
        (1) "A Practical Guide to Training Restricted Boltzmann
            Machines", Geoffrey E. Hinton, University of Toronto, 2010

    Attributes:
        about (str): Short description of the content of the resource.
            Hint: Read- & writeable wrapping attribute to get('about')
                and set('about', str).
        author (str): A person, an organization, or a service that is
            responsible for the creation of the content of the resource.
            Hint: Read- & writeable wrapping attribute to get('author')
                and set('author', str).
        branch (str): Name of a duplicate of the original resource.
            Hint: Read- & writeable wrapping attribute to get('branch')
                and set('branch', str).
        edges (list of str): List of all edges in the network.
            Hint: Readonly wrapping attribute to get('edges')
        email (str): Email address to a person, an organization, or a
            service that is responsible for the content of the resource.
            Hint: Read- & writeable wrapping attribute to get('email')
                and set('email', str).
        fullname (str): String concatenation of name, branch and
            version. Branch and version are only conatenated if they
            exist.
            Hint: Readonly wrapping attribute to get('fullname')
        layers (list of str): List of all layers in the network.
            Hint: Readonly wrapping attribute to get('layers')
        license (str): Namereference to a legal document giving official
            permission to do something with the resource.
            Hint: Read- & writeable wrapping attribute to get('license')
                and set('license', str).
        name (str): Name of the resource.
            Hint: Read- & writeable wrapping attribute to get('name')
                and set('name', str).
        nodes (list of str): List of all nodes in the network.
            Hint: Readonly wrapping attribute to get('nodes')
        path (str):
            Hint: Read- & writeable wrapping attribute to get('path')
                and set('path', str).
        type (str): String concatenation of module name and class name
            of the instance.
            Hint: Readonly wrapping attribute to get('type')
        version (int): Versionnumber of the resource.
            Hint: Read- & writeable wrapping attribute to get('version')
                and set('version', int).

    """

    _default = {
        'params': {
            'samples': '*',
            'subnet': '*',
            'visible': 'auto',
            'hidden': 'auto',
            'visible_class': 'sigmoid',
            'hidden_class': 'sigmoid' },
        'init': {
            'check_dataset': False,
            'ignore_units': [],
            'w_sigma': 0.5 },
        'optimize': {
            'ignore_units': [],
            'minibatch_size': 100,
            'minibatch_update_interval': 10,
            'updates': 100000,
            'algorithm': 'cd',
            'con_module': 'klpt',
            'denoising': 'noise',
            'acc_module': 'vmra',
            'gen_module': 'rasa',
            'update_cd_sampling_steps': 1,
            'update_cd_sampling_iterations': 1,
            'update_rate': 0.1,
            'update_factor_weights': 1.,
            'update_factor_hbias': 0.1,
            'update_factor_vbias': 0.1,
            'gen_rasa_enable': True,
            'gen_rasa_init_temperature': 1.,
            'gen_rasa_annealing_factor': 1.,
            'gen_rasa_annealing_cycles': 1,
            'con_klpt_enable': True,
            'con_klpt_rate': 0.,
            'con_klpt_expect': 0.5,
            'noise_enable': True,
            'noise_type': 'mask',
            'noise_factor': 0.5,
            'adjacency_enable': False,
            'tracker_obj_function': 'error',
            'tracker_eval_time_interval': 10. ,
            'tracker_estimate_time': True,
            'tracker_estimate_time_wait': 20. }}

    def _set_params_create_mapping(self):
        v = self._params['units'][0]['layer']
        h = self._params['units'][1]['layer']
        mapping = (v, h, v)
        self._set_mapping(mapping)

        return True

    def _check_dataset(self, dataset):
        """Check if dataset contains only binary values."""
        if not nemoa.common.type.isdataset(dataset):
            return nemoa.log('error', """could not test dataset:
                invalid dataset instance given.""")
        if not dataset._algorithm_test_binary():
            return nemoa.log('error', """dataset '%s' is not valid:
                RBMs expect binary data.""" % dataset.name)
        return True

class GRBM(RBM):
    """Gaussian Restricted Boltzmann Machine (GRBM).

    Gaussian Restricted Boltzmann Machines (1) are energy based
    undirected artificial neuronal networks with two layers: visible
    and hidden. The visible layer contains gauss distributed
    gaussian units to model data. The hidden layer contains binary
    distributed sigmoidal units to model relations in the data.

    Reference:
        (1) "Improved Learning of Gaussian-Bernoulli Restricted
            Boltzmann Machines", KyungHyun Cho, Alexander Ilin and
            Tapani Raiko, ICANN 2011

    Attributes:
        about (str): Short description of the content of the resource.
            Hint: Read- & writeable wrapping attribute to get('about')
                and set('about', str).
        author (str): A person, an organization, or a service that is
            responsible for the creation of the content of the resource.
            Hint: Read- & writeable wrapping attribute to get('author')
                and set('author', str).
        branch (str): Name of a duplicate of the original resource.
            Hint: Read- & writeable wrapping attribute to get('branch')
                and set('branch', str).
        edges (list of str): List of all edges in the network.
            Hint: Readonly wrapping attribute to get('edges')
        email (str): Email address to a person, an organization, or a
            service that is responsible for the content of the resource.
            Hint: Read- & writeable wrapping attribute to get('email')
                and set('email', str).
        fullname (str): String concatenation of name, branch and
            version. Branch and version are only conatenated if they
            exist.
            Hint: Readonly wrapping attribute to get('fullname')
        layers (list of str): List of all layers in the network.
            Hint: Readonly wrapping attribute to get('layers')
        license (str): Namereference to a legal document giving official
            permission to do something with the resource.
            Hint: Read- & writeable wrapping attribute to get('license')
                and set('license', str).
        name (str): Name of the resource.
            Hint: Read- & writeable wrapping attribute to get('name')
                and set('name', str).
        nodes (list of str): List of all nodes in the network.
            Hint: Readonly wrapping attribute to get('nodes')
        path (str):
            Hint: Read- & writeable wrapping attribute to get('path')
                and set('path', str).
        type (str): String concatenation of module name and class name
            of the instance.
            Hint: Readonly wrapping attribute to get('type')
        version (int): Versionnumber of the resource.
            Hint: Read- & writeable wrapping attribute to get('version')
                and set('version', int).

    """

    _default = {
        'params': {
            'samples': '*',
            'subnet': '*',
            'visible': 'auto',
            'hidden': 'auto',
            'visible_class': 'gauss',
            'hidden_class': 'sigmoid' },
        'init': {
            'check_dataset': False,
            'ignore_units': [],
            'w_sigma': 0.5 },
        'optimize': {
            'ignore_units': [],
            'algorithm': 'cd',
            'updates': 100000,
            'update_rate': 0.0005,
            'update_factor_weights': 1.,
            'update_factor_hbias': 0.1,
            'update_factor_vbias': 0.1,
            'update_factor_vlvar': 0.01,
            'update_cd_sampling_steps': 1,
            'update_cd_sampling_iterations': 1,
            'minibatch_size': 100,
            'minibatch_update_interval': 1,
            'con_module': '',
            'denoising': 'noise',
            'acc_module': 'vmra',
            'gen_module': 'rasa',
            'acc_vmra_init_rate': 0.0005,
            'acc_vmra_length': 3,
            'acc_vmra_update_interval': 10,
            'acc_vmra_init_wait': 100,
            'acc_vmra_factor': 10.,
            'acc_vmra_min_rate': 0.0005,
            'acc_vmra_max_rate': 0.02,
            'gen_rasa_init_temperature': 10.,
            'gen_rasa_min_temperature': 0.01,
            'gen_rasa_annealing_factor': 10.,
            'gen_rasa_annealing_cycles': 2,
            'con_klpt_rate': 0.0001,
            'con_klpt_expect': 0.35,
            'noise_type': 'gauss',
            'noise_factor': 0.75,
            'tracker_estimate_time': False,
            'tracker_estimate_time_wait': 15.,
            'tracker_obj_tracking_enable': True,
            'tracker_obj_init_wait': 0.01,
            'tracker_obj_function': 'accuracy',
            'tracker_obj_keep_optimum': True,
            'tracker_obj_update_interval': 100,
            'tracker_eval_enable': True,
            'tracker_eval_function': 'accuracy',
            'tracker_eval_time_interval': 10. }}

    def _check_dataset(self, dataset):
        """Check if dataset contains gauss normalized values."""
        if not nemoa.common.type.isdataset(dataset):
            return nemoa.log('error', """could not test dataset:
                invalid dataset instance given.""")
        if not dataset.evaluate('test_gauss'):
            return nemoa.log('error', """dataset '%s' is not valid:
                GRBMs expect standard normal distributed data."""
                % (dataset.name))
        return True
