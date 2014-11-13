# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import networkx
import os

def types():
    """Get supported layer network types for network building."""

    return {
        'model': 'generic network model',
        'autoencoder': 'autoencoder'
    }

def build(type = None, *args, **kwargs):
    """Build model from parameters and dataset."""

    if type == 'model': return Model(**kwargs).build()
    if type == 'autoencoder': return AutoEncoder(**kwargs).build()

    return False

class AutoEncoder:
    """Build deep AutoEncoder from dataset and network parameters."""

    settings = {
        'dataset': None,
        'network': None,
        'system': 'dbn',
        'initialize': True,
        'optimize': False }

    def __init__(self, **kwargs):
        nemoa.common.dict_merge(kwargs, self.settings)

    def build(self):

        # create model dictionary including dataset, network and system
        model_dict = {}

        if nemoa.type.is_dataset(self.settings['dataset']):
            model_dict['dataset'] = self.settings['dataset']
            dataset_name = self.settings['dataset'].name
        else:
            model_dict['dataset'] \
                = nemoa.dataset.load(self.settings['dataset'])
            if not model_dict['dataset']: return {}
            dataset_name = model_dict['dataset']['config']['name']

        if nemoa.type.is_network(self.settings['network']):
            model_dict['network'] = self.settings['network']
            network_name = self.settings['network'].name
        else:
            model_dict['network'] \
                = nemoa.network.load(self.settings['network'])
            if not model_dict['network']: return {}
            network_name = model_dict['network']['config']['name']

        if nemoa.type.is_system(self.settings['system']):
            model_dict['system'] = self.settings['system']
            system_name = self.settings['system'].name
        else:
            model_dict['system'] \
                = nemoa.system.load(self.settings['system'])
            if not model_dict['system']: return {}
            system_name = model_dict['system']['config']['name']

        model_dict['config'] = {
            'name': '-'.join([dataset_name, network_name, system_name]),
            'type': 'base.Model'}

        # create instance of model
        # configure, iniztalize and optimize model
        model = nemoa.model.new(**model_dict)
        model.configure()
        if self.settings['initialize']: model.initialize()
        if self.settings['optimize']: model.optimize()

        return model.get('copy')

class Model:
    """Build standard model from parameters."""

    settings = {
        'dataset': None,
        'network': None,
        'system': None,
        'initialize': True,
        'optimize': False }

    def __init__(self, **kwargs):
        nemoa.common.dict_merge(kwargs, self.settings)

    def build(self):

        # create model dictionary including dataset, network and system
        model_dict = {}

        if nemoa.type.is_dataset(self.settings['dataset']):
            model_dict['dataset'] = self.settings['dataset']
            dataset_name = self.settings['dataset'].name
        else:
            model_dict['dataset'] \
                = nemoa.dataset.load(self.settings['dataset'])
            if not model_dict['dataset']: return {}
            dataset_name = model_dict['dataset']['config']['name']

        if nemoa.type.is_network(self.settings['network']):
            model_dict['network'] = self.settings['network']
            network_name = self.settings['network'].name
        else:
            model_dict['network'] \
                = nemoa.network.load(self.settings['network'])
            if not model_dict['network']: return {}
            network_name = model_dict['network']['config']['name']

        if nemoa.type.is_system(self.settings['system']):
            model_dict['system'] = self.settings['system']
            system_name = self.settings['system'].name
        else:
            model_dict['system'] \
                = nemoa.system.load(self.settings['system'])
            if not model_dict['system']: return {}
            system_name = model_dict['system']['config']['name']

        model_dict['config'] = {
            'name': '-'.join([dataset_name, network_name, system_name]),
            'type': 'base.Model'}

        # create instance of model
        # configure, iniztalize and optimize model
        model = nemoa.model.new(**model_dict)
        model.configure()
        if self.settings['initialize']: model.initialize()
        if self.settings['optimize']: model.optimize()

        return model.get('copy')
