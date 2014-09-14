#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nemoa

import nemoa.plot as plot

class mpAnalyse:

    cfg = {}
    path = None

    def __init__(self, config = None, path = None, plots = None):

        # copy configuration
        if config == None:
            return

        self.cfg   = config
        self.path  = path
        self.plots = plots

    def analyse(self, obj_model):

        # check object class
        if not obj_model.__class__.__name__ == 'mpModel':
            nemoa.log('error', "could not run analysis: 'model' has to be mpModel instance!")
            return False

        nemoa.log('analyse model:')

        # create plots
        default = {
            'fileformat': 'pdf',
            'dpi': 600,
            'output': 'file'
        }

        if 'plots' in self.cfg:
            for plotid in self.cfg['plots']:
                if not plotid in self.plots:
                    continue

                type   = self.plots[plotid]['type']
                params = self.plots[plotid]['params']

                for key in default:
                    if not key in params:
                        params[key] = default[key]

                file = self.path + obj_model.cfg['name'] + '/' + plotid + '.' + params['fileformat']
                nemoa.log(" * plot '" + plotid + "'")
                plot.mpPlot(obj_model, plot = type, file = file, **params)

        return True
