#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nemoa.plot.base, matplotlib, matplotlib.pyplot

class histogram(nemoa.plot.base.plot):

    def _default(self):
        return {
            'output': 'file',
            'fileformat': 'pdf',
            'dpi': 600,
            'show_figure_caption': True,
            'bins': 120,
            'facecolor': 'lightgrey',
            'edgecolor': 'black',
            'histtype': 'bar',
            'linewidth': 0.5
        }

    def _create(self, model, file = None):

        # get data
        data = self.getData(model)

        # create figure object
        fig = matplotlib.pyplot.figure()
        ax = fig.add_subplot(111)
        ax.grid(True)
        cax = ax.hist(data,
            normed    = True,
            bins      = self.settings['bins'],
            facecolor = self.settings['facecolor'],
            histtype  = self.settings['histtype'],
            linewidth = self.settings['linewidth'],
            edgecolor = self.settings['edgecolor'])

        return True

    def getData(self, model):
        return model.dataset.getData(self.settings['statistics']).flatten()
    def _getTitle(self, model):
        return "Data distribution of '" + model.dataset.name() + "'"

class data(histogram):

    def getDefaults(self):
        return {'statistics': 10000}
    def getData(self, model):
        return model.dataset.getData(self.settings['statistics']).flatten()

#class sampleRelation(histogram):

    #def getDefaults(self):
        #return {'samples': '*', 'relation': 'correlation'}
    #def getData(self, model):
        #return model.getSampleRelationMatrix(
            #samples = settings['samples'],
            #relation = settings['relation']).flatten()
    #def getTitle(self, model):
        #return "Distribution of sample " + self.settings['relation']

class relation(histogram):

    def getDefaults(self):
        return {
            'units': 'visible', 'x': None, 'y': None,
            'relation': 'knockout',
            'statistics': 100000 }

    def getData(self, model):

        # convert 'visible' and 'hidden' to list of nodes
        visible, hidden = model.system.getUnits()
        for key in ['units', 'x', 'y']:
            if type(self.settings[key]) == type(list()):
                continue
            if not type(self.settings[key]) == type(str()):
                self.settings[key] = []
                continue
            if self.settings[key].lower().strip() == 'visible':
                self.settings[key] = visible
            elif settings[key].lower().strip() == 'hidden':
                self.settings[key] = hidden

        # set independent units (y) and dependent units (x)
        if self.settings['units']:
            self.settings['x'] = self.settings['units']
            self.settings['y'] = self.settings['units']
        elif not self.settings['x'] and self.settings['y']:
            self.settings['x'] = visible
        elif self.settings['x'] and not self.settings['y']:
            self.settings['y'] = visible

        # calculate relation matrix
        data = model.getUnitRelationMatrix(
            units = self.settings['units'], x = self.settings['x'], y = self.settings['y'],
            relation = self.settings['relation'],
            statistics = self.settings['statistics']).flatten()

        return data
    
    def _getTitle(self, model):
        return "Distribution of unit " + self.settings['relation']
    
