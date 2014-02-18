#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nemoa, matplotlib.pyplot

class plot:

    cfg = None
    settings = None
    defaults = None

    def __init__(self, config = None):
        self.setConfig(config)

    def setConfig(self, config):
        """Initialize plot configuration with dictionary."""

        self.cfg = {}
        if config == None:
            return None

        self.cfg['name'] = config['name']
        self.cfg['id'] = config['id']
        self.cfg['input'] = 'model'

        # append / overwrite settings with default settings
        self.settings = self.getSettings()
        for key, value in self.getDefaults().items():
            self.settings[key] = value

        # set configured settings
        for key, value in config['params'].items():
            self.settings[key] = value
        
        return True

    def name(self):
        """Return name of plot. """
        return self.cfg['name']

    def getSettings(self):
        return {
            'fileformat': 'pdf',
            'dpi': 600,
            'output': 'file',
            'show_figure_caption': True }

    def getDefaults(self):
        return {}

    def create(self, model, file = None):
        
        # common matplotlib settings
        matplotlib.rc('font', family = 'serif')

        self._create(model, file)

        # clear figures and release memory
        matplotlib.pyplot.close("all")

        return True
        
