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
        'model': 'network model'
    }

def build(type = None, *args, **kwargs):
    """Build model from parameters and dataset."""

    if type == 'model': return Model(**kwargs).build()

    return False

class Model:
    """Build standard model from parameters."""

    settings = {
        'dataset': None,
        'network': None,
        'system': None,
        'initialize': True,
        'optimize': False }

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            if key in self.settings.keys():
                self.settings[key] = val

    def build(self):

        # create model dictionary including dataset, network and system
        model_dict = {}
        model_dict['dataset'] \
            = nemoa.dataset.load(self.settings['dataset'])
        if not model_dict['dataset']: return {}
        model_dict['network'] \
            = nemoa.network.load(self.settings['network'])
        if not model_dict['network']: return {}
        model_dict['system'] \
            = nemoa.system.load(self.settings['system'])
        if not model_dict['system']: return {}
        model_dict['config'] = {
            'name': '-'.join([
                model_dict['dataset']['config']['name'],
                model_dict['network']['config']['name'],
                model_dict['system']['config']['name']]),
            'type': 'base.Model'}

        # create instance of model
        # configure, iniztalize and optimize model
        model = nemoa.model.new(**model_dict)
        model.configure()
        if self.settings['initialize']: model.initialize()
        if self.settings['optimize']: model.optimize()

        return model.get('copy')
