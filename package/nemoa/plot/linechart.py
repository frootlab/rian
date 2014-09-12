# -*- coding: utf-8 -*-
import nemoa
import numpy as np
from nemoa.plot.base import plot

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

class linechart(plot):

    def getSettings(self): return {
        'output': 'file',
        'fileformat': 'pdf',
        'dpi': 300,
        'showTitle': True,
        'show_figure_caption': True,
        'facecolor': 'lightgrey',
        'edgecolor': 'black',
        'linewidth': 0.5,
        'valuation': 'accuracy'
    }

    def create(self, models, file = None):

        # get data
        data = np.zeros(len(models))
        for i, model in enumerate(models):
            data[i] = self.getData(model)

        # create figure object
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.grid(True)
        cax = ax.hist(data,
            normed = True,
            bins = self.settings['bins'],
            facecolor = self.settings['facecolor'],
            histtype  = self.settings['histtype'],
            linewidth = self.settings['linewidth'],
            edgecolor = self.settings['edgecolor'])

        # draw figure title / caption
        if self.settings['show_figure_caption']:

            # draw title
            title = self.getTitle(model)
            plt.title(title, fontsize = 11)

        # output
        if file:
            plt.savefig(file, dpi = self.settings['dpi'])
        else:
            plt.show()

        # clear current figure object and release memory
        plt.clf()
        plt.close(fig)

        return True

    def getData(self, model):
        return model.dataset.getData(self.settings['statistics']).flatten()
    def getTitle(self, model):
        return "Data distribution of '" + model.dataset.cfg['name'] + "'"

class modelValuation(linechart):

    def getDefaults(self):
        return {'statistics': 10000}
    def getData(self, model):
        return model.dataset.getData(self.settings['statistics']).flatten()
    def getTitle(self, model):
        return "Data distribution of '" + model.dataset.cfg['name'] + "'"
