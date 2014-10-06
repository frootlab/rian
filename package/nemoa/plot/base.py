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
        self._set_config(config)

    def _set_config(self, config):
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
        'show_title': True,
        'title': None,
        'bg_color': 'none',
    }

    def create(self, model, file = None):

        # common matplotlib settings
        matplotlib.rc('font', family = 'serif')

        # close previous figures
        matplotlib.pyplot.close('all')

        # update configuration, depending on object type
        if list(self.settings['path'])[0] == 'dataset':
            if self.settings['show_title']:
                self.settings['title'] = model.dataset.get('name').title()
        elif list(self.settings['path'])[0] == 'network':
            if self.settings['show_title']:
                self.settings['title'] = model.dataset.get('name').title()
        elif list(self.settings['path'])[0] == 'system':

            # assert units
            mapping = model.system.mapping()
            in_units = model.system.get('units', layer = mapping[0])
            out_units = model.system.get('units', layer = mapping[-1])
            if not isinstance(self.settings['units'], tuple) \
                or not isinstance(self.settings['units'][0], list) \
                or not isinstance(self.settings['units'][1], list):
                self.settings['units'] = (in_units, out_units)

            # get information about relation
            if self.settings['show_title']:
                rel_id = nemoa.common.str_split_params(
                    self.settings['relation'])[0]
                rel_dict = model.about('system', 'relations', rel_id)
                rel_name = rel_dict['name']
                self.settings['title'] = rel_name.title()

        # create plot
        if self._create(model):

            # (optional) draw title
            if self.settings['show_title']:
                if 'title' in self.settings \
                    and isinstance(self.settings['title'], str):
                    title = self.settings['title']
                else: title = self._get_title(model)
                matplotlib.pyplot.title(title, fontsize = 11.)

            # output
            if file:
                matplotlib.pyplot.savefig(
                    file, dpi = self.settings['dpi'])
            else: matplotlib.pyplot.show()

        # clear figures and release memory
        matplotlib.pyplot.clf()

        return True

    def _get_title(self, model):
        return model.get('name')
