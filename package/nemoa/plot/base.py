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
        if config == None: return None

        self.cfg['name'] = config['name']
        self.cfg['id'] = config['id']
        self.cfg['input'] = 'model'

        # append / overwrite settings with default settings
        self.settings = self._default()
        for key, value in self.getDefaults().items():
            self.settings[key] = value

        # set configured settings
        for key, value in config['params'].items():
            self.settings[key] = value

        return True

    def name(self):
        """Return name of plot. """
        return self.cfg['name']

    @staticmethod
    def _default(): return {
        'fileformat': 'pdf',
        'dpi': 300,
        'output': 'file',
        'show_figure_caption': True }

    def getDefaults(self):
        return {}

    def create(self, model, file = None):

        # common matplotlib settings
        matplotlib.rc('font', family = 'serif')

        # close previous figures
        matplotlib.pyplot.close("all")

        # create plot (in memory)
        self._create(model)

        # draw title
        if 'title' in self.settings \
            and isinstance(self.settings['title'], str):
            title = self.settings['title']
        else: title = self._getTitle(model)
        matplotlib.pyplot.title(title, fontsize = 11.0)

        # output
        if file: matplotlib.pyplot.savefig(file, dpi = self.settings['dpi'])
        else: matplotlib.pyplot.show()

        # clear figures and release memory
        matplotlib.pyplot.clf()

        return True

    def _getTitle(self, model):
        return model.name()
