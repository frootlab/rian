# -*- coding: utf-8 -*-
import metapath.common as mp
import numpy as np
from metapath.plot.base import plot

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

class linechart(plot):

    def getSettings(self):
        return {
            'output': 'file',
            'fileformat': 'pdf',
            'dpi': 600,
            'show_figure_caption': True,
            'facecolor': 'lightgrey',
            'edgecolor': 'black',
            'linewidth': 0.5,
            'valuation': 'performance()'
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

##
##class GRBM_plot:
##
##    def __init__(self):
##        
##        self.label = {
##            'energy': 'Energy = $- \sum \\frac{1}{2 \sigma_i^2}(v_i - b_i)^2 ' +\
##                '- \sum \\frac{1}{\sigma_i^2} w_{ij} v_i h_j ' +\
##                '- \sum c_j h_j$',
##            'error': 'Error = $\sum (data - p[v = data|\Theta])^2$'
##        }
##
##        self.density = 1
##        self.reset()
##
##        
##    def reset(self):
##        self.data = {
##            'epoch': np.empty(1),
##            'energy': np.empty(1),
##            'error': np.empty(1)
##        }
##
##        self.buffer = {
##            'energy': 0,
##            'error': 0
##        }
##
##        self.last_epoch = 0
##    
##    def set_density(self, updates, points):
##        self.density = max(int(updates / points), 1)
##    
##    def add(self, epoch, v_data, h_data, v_model, h_model, params):
##        
##        # calculate energy, error etc.
##        self.buffer['error'] += params.error(v_data)
##        self.buffer['energy'] += params.energy(v_data)
##        
##        if (epoch - self.last_epoch) % self.density == 0:
##            self.data['epoch'] = \
##                np.append(self.data['epoch'], epoch)
##            self.data['error'] = \
##                np.append(self.data['error'], self.buffer['error'] / self.density)
##            self.data['energy'] = \
##                np.append(self.data['energy'], self.buffer['energy'] / self.density)
##
##            # reset energy and error
##            self.buffer['error'] = 0
##            self.buffer['energy'] = 0
##
##    def save(self, path = None):
##        if path == None:
##            mp_error("no save path was given")
##
##        # create path if not available
##        if not os.path.exists(path):
##            os.makedirs(path)
##
##        for key, val in self.data.items():
##            if key == 'epoch':
##                continue
##
##            file_plot = '%s/%s.pdf' % (path, key.lower())
##
##            # get labels
##            xlabel = 'updates'
##            ylabel = key
##
##            plt.figure()
##            plt.plot(self.data['epoch'], val, 'b,')
##            plt.xlabel(xlabel)
##            plt.ylabel(ylabel)
##            plt.savefig(file_plot)
