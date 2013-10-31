# -*- coding: utf-8 -*-
import nemoa

#
# plot object (template)
#

class plot:

    cfg = None
    settings = None
    defaults = None

    #
    # PLOT CONFIGURATION
    #

    def __init__(self, config = None):
        if not config:
            return

        self.setConfig(config)

    def setConfig(self, config):
        """
        initialize plot configuration, using configuration dictionary
        """

        self.cfg = {}
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

    def getName(self):
        """
        Return name of plot
        """
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
        pass
        
