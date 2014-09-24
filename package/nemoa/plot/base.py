# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import matplotlib.pyplot

class plot:

    cfg = None
    settings = None
    defaults = None

    def __init__(self, config = None):
        self._setConfig(config)

    def _setConfig(self, config):
        """Initialize plot configuration with dictionary."""

        self.cfg = {}
        if config == None: return None

        self.cfg['name']  = config['name']
        self.cfg['id']    = config['id']
        self.cfg['input'] = 'model'

        # append / overwrite settings with default settings
        self.settings = self._default()
        for key, value in self._settings().items():
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
        'showTitle': True,
        'title': None,
        'backgroundColor': 'none',
    }

    def create(self, model, file = None):

        # common matplotlib settings
        matplotlib.rc('font', family = 'serif')

        # close previous figures
        matplotlib.pyplot.close("all")

        # update configuration, depending on object type
        if self.settings['path'][0] == 'dataset':
            if self.settings['showTitle']: self.settings['title'] = \
                model.dataset.name().title()
        elif list(self.settings['path'])[0] == 'network':
            if self.settings['showTitle']: self.settings['title'] = \
                model.dataset.name().title()
        elif list(self.settings['path'])[0] == 'system':

            # assert units
            mapping = model.system.mapping()
            iUnits  = model.units(group = mapping[0])[0]
            oUnits  = model.units(group = mapping[-1])[0]
            if not isinstance(self.settings['units'], tuple) \
                or not isinstance(self.settings['units'][0], list) \
                or not isinstance(self.settings['units'][1], list):
                self.settings['units'] = (iUnits, oUnits)

            # get information about relation
            relation = model.about('system', 'relations',
                nemoa.common.strSplitParams(self.settings['relation'])[0])
            if self.settings['showTitle']: self.settings['title'] = \
                relation['name'].title()

        # create plot
        if self._create(model):

            # (optional) draw title
            if self.settings['showTitle']:
                if 'title' in self.settings \
                    and isinstance(self.settings['title'], str):
                    title = self.settings['title']
                else: title = self._getTitle(model)
                matplotlib.pyplot.title(title, fontsize = 11.)

            # output
            if file: matplotlib.pyplot.savefig(file,
                dpi = self.settings['dpi'])
            else: matplotlib.pyplot.show()

        # clear figures and release memory
        matplotlib.pyplot.clf()

        return True

    def _getTitle(self, model):
        return model.name()
