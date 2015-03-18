# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.model.optimizer.base

def optimize(model, schedule = None, *args, **kwargs):
    """Optimize model."""

    # test type of model and subclasses
    if not nemoa.common.type.ismodel(model):
        return nemoa.log('error', """could not optimize model:
            model is not valid.""") or None
    if not nemoa.common.type.isdataset(model.dataset):
        return nemoa.log('error', """could not optimize model:
            dataset is not valid.""") or None
    if not nemoa.common.type.isnetwork(model.network):
        return nemoa.log('error', """could not optimize model:
            network is not valid.""") or None
    if not nemoa.common.type.issystem(model.system):
        return nemoa.log('error', """could not optimize model:
            system is not valid.""") or None

    # get optimization schedule
    # 2do: move optimization 'schedule handling' to optimizer
    if not isinstance(schedule, dict):
        if schedule == None: key = 'default'
        elif isinstance(schedule, basestring): key = schedule
        else:
            return nemoa.log('error', """could not optimize model:
                optimization schedule is not valid.""") or None
        if key in model.system._config['schedules']:
            import copy
            schedule = copy.deepcopy(
                model.system._config['schedules'][key])
        else:
            schedule = {}

    # check if optimization schedule supports current system
    if not model.system.type in schedule:
        return nemoa.log('error', """could not optimize model:
            optimization schedule '%s' does not support system '%s'.
            """ % (schedule['name'], model.system.type))

    # update current optimization schedule from given schedule
    ddef = model.system._default['optimize']
    dcur = model.system._config['optimize']
    darg = schedule[model.system.type]
    config = nemoa.common.dict.merge(dcur, ddef)
    config = nemoa.common.dict.merge(darg, config)
    model.system._config['optimize'] = config
    schedule[model.system.type] = config

    # check dataset
    if (not 'check_dataset' in model.system._default['init']
        or model.system._default['init']['check_dataset'] == True) \
        and not model.system._check_dataset(self.dataset):
        return None

    # get optimization algorithm
    algorithm = config.get('meta_algorithm', config['algorithm'])
    optimizer = model.system._get_algorithm(algorithm.lower(),
        category = ('system', 'optimization'))
    if optimizer:
        nemoa.log('note', "optimize '%s' (%s) using algorithm %s."
            % (model.name, model.type, optimizer['name']))
    else:
        return nemoa.log('error', """could not optimize '%s' (%s):
            unsupported optimization algorithm '%s'."""
            % (model.name, model.type, algorithm)) or None

    tracker = nemoa.model.optimizer.base.Optimizer(model)
    optimizer['reference'](model.dataset, schedule, tracker)
    model.network.initialize(model.system)

    return True
