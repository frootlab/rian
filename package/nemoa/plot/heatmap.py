# -*- coding: utf-8 -*-
import nemoa
import numpy as np

from nemoa.plot.base import plot

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

class heatmap(plot):
    
    def getSettings(self):
        return {
            'output': 'file',
            'fileformat': 'pdf',
            'dpi': 600,
            'show_figure_caption': True,
            'interpolation': 'nearest'
        }

class sampleRelation(heatmap):
    
    def getDefaults(self):
        return {
            'samples': '*',
            'relation': 'distance_euclidean_hexpect'
        }

    def create(self, model, file = None):

        # calculate sample relation matrix
        data = model.getSampleRelationMatrix(
            samples  = self.settings['samples'],
            relation = self.settings['relation'] )

        # create figure object
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.grid(True)
        cax = ax.imshow(data,
            cmap = matplotlib.cm.hot_r,
            interpolation = self.settings['interpolation'],
            extent = (0, data.shape[0], 0, data.shape[1]))

        # get labels and set plot ticks and labels
        labels = model.dataset.getRowLabels()

        plt.yticks(
            len(labels) - np.arange(len(labels)) - 0.5,
            tuple(labels),
            fontsize = 9)
            
        plt.xticks(
            np.arange(len(labels)) + 0.5,
            tuple(labels),
            fontsize = 9,
            rotation = 70)
        
        # add colorbar
        cbar = fig.colorbar(cax)
        for tick in cbar.ax.get_yticklabels():
            tick.set_fontsize(9)

        # draw figure title / caption
        if self.settings['show_figure_caption']:
            
            title = "%s: %s" % (model.dataset.cfg['name'],
                self.settings['relation'])
            
            # draw title
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

class unitRelation(heatmap):

    def getDefaults(self):
        return {
            'units': 'visible',
            'x': None,
            'y': None,
            'relation': 'correlation()',
            'preprocessing': None,
            'statistics': 10000
        }

    def create(self, model, file = None):

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
            preprocessing = self.settings['preprocessing'],
            relation = self.settings['relation'],
            statistics = self.settings['statistics'])

        # create figure object
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.grid(True)
        cax = ax.imshow(data,
            cmap = matplotlib.cm.hot_r,
            interpolation = self.settings['interpolation'],
            extent = (0, len(self.settings['x']), 0, len(self.settings['y'])))

        # create labels for x-axis
        xLabels = model.network.getNodeLabels(self.settings['x'])
        plt.xticks(
            np.arange(len(xLabels)) + 0.5,
            tuple(xLabels),
            fontsize = 8,
            rotation = 65)

        # create labels for y-axis
        yLabels = model.network.getNodeLabels(self.settings['y'])
        plt.yticks(
            len(yLabels) - np.arange(len(yLabels)) - 0.5,
            tuple(yLabels),
            fontsize = 8)

        # create colorbar
        cbar = fig.colorbar(cax)
        for tick in cbar.ax.get_yticklabels():
            tick.set_fontsize(9)

        # draw figure title / caption
        if self.settings['show_figure_caption']:
            title = "%s: %s" % (model.dataset.cfg['name'], nemoa.common.strSplitParams(self.settings['relation'])[0])

            # draw title
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
