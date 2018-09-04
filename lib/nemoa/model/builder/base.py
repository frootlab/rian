# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa

from nemoa.common import classes

def types():
    """Get supported layer network types for network building."""

    return {
        'autoencoder': 'autoencoder',
        'model': 'generic network model' }

def build(type = None, *args, **kwargs):
    """Build model from parameters and dataset."""

    if type == 'autoencoder': return AutoEncoder(**kwargs).build()
    if type == 'model': return Model(**kwargs).build()

    return False

class AutoEncoder:
    """Build AutoEncoder from dataset and network parameters."""

    settings = None
    default = {
        'dataset': None,
        'network': None,
        'system': 'dbn' }

    def __init__(self, dataset = None, **kwargs):
        from nemoa.common.dict import merge
        self.settings = merge(kwargs, self.default)

        if classes.hasbase(dataset, 'Dataset'):
            self.settings['dataset'] = dataset
        else:
            self.settings['dataset'] = nemoa.dataset.load(dataset)

    def build(self):

        # create dataset instance
        if not classes.hasbase(self.settings['dataset'], 'Dataset'):
            return {}

        # create network instance from dataset instance
        self.settings['network'] = nemoa.network.create('autoencoder',
            dataset = self.settings['dataset'])

        return Model(**self.settings).build()

class Model:
    """Build standard model from parameters."""

    settings = None
    default = {
        'dataset': None,
        'network': None,
        'system': None,
        'initialize': True,
        'optimize': False }

    def __init__(self, **kwargs):
        from nemoa.common.dict import merge
        self.settings = merge(kwargs, self.default)

    def build(self):

        # create model dictionary including dataset, network and system
        model_dict = {}

        if classes.hasbase(self.settings['dataset'], 'Dataset'):
            model_dict['dataset'] = self.settings['dataset']
            dataset_name = self.settings['dataset'].name
        else:
            model_dict['dataset'] \
                = nemoa.dataset.load(self.settings['dataset'])
            if not model_dict['dataset']: return {}
            dataset_name = model_dict['dataset']['config']['name']

        if classes.hasbase(self.settings['network'], 'Network'):
            model_dict['network'] = self.settings['network']
            network_name = self.settings['network'].name
        else:
            model_dict['network'] \
                = nemoa.network.load(self.settings['network'])
            if not model_dict['network']: return {}
            network_name = model_dict['network']['config']['name']

        if classes.hasbase(self.settings['system'], 'System'):
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
