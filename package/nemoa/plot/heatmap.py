#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nemoa.plot.base, numpy, matplotlib

class heatmap(nemoa.plot.base.plot):

    def getSettings(self):
        return {
            'output': 'file',
            'fileformat': 'pdf',
            'dpi': 600,
            'show_figure_caption': True,
            'interpolation': 'nearest'
        }

#class sampleRelation(heatmap):

    #def getDefaults(self):
        #return {
            #'samples': '*',
            #'relation': 'distance_euclidean_hexpect'
        #}

    #def create(self, model, file = None):

        ## calculate sample relation matrix
        #data = model.getSampleRelationMatrix(
            #samples  = self.settings['samples'],
            #relation = self.settings['relation'] )

        ## create figure object
        #fig = matplotlib.pyplot.figure()
        #ax = fig.add_subplot(111)
        #ax.grid(True)
        #cax = ax.imshow(data,
            #cmap = matplotlib.cm.hot_r,
            #interpolation = self.settings['interpolation'],
            #extent = (0, data.shape[0], 0, data.shape[1]))

        ## get labels and set plot ticks and labels
        #labels = model.dataset.getRowLabels()

        #matplotlib.pyplot.yticks(
            #len(labels) - numpy.arange(len(labels)) - 0.5,
            #tuple(labels),
            #fontsize = 9)
            
        #matplotlib.pyplot.xticks(
            #numpy.arange(len(labels)) + 0.5,
            #tuple(labels),
            #fontsize = 9,
            #rotation = 70)
        
        ## add colorbar
        #cbar = fig.colorbar(cax)
        #for tick in cbar.ax.get_yticklabels():
            #tick.set_fontsize(9)

        ## draw figure title / caption
        #if self.settings['show_figure_caption']:
            
            #title = "%s: %s" % (model.dataset.cfg['name'],
                #self.settings['relation'])
            
            ## draw title
            #matplotlib.pyplot.title(title, fontsize = 11)
        
        ## output
        #if file:
            #matplotlib.pyplot.savefig(file, dpi = self.settings['dpi'])
        #else:
            #matplotlib.pyplot.show()
        
        ## clear current figure object and release memory
        #matplotlib.pyplot.clf()
        #matplotlib.pyplot.close(fig)

        #return True

class unitRelation(heatmap):

    def getDefaults(self):
        return {
            'units': (None, None),
            'relation': 'correlation()',
            'modify': 'knockout',
            'eval': 'error',
            'preprocessing': None,
            'statistics': 10000
        }

    def create(self, model, file = None):
        params = self.settings['params'] if 'params' in self.settings \
            else {}

        # update self.units
        if not isinstance(self.settings['units'], tuple) \
            or not isinstance(self.settings['units'][0], list):
            mapping = model.system.getMapping()
            self.settings['units'] = (model.units(group = mapping[0])[0],
                model.units(group = mapping[-1])[0])

        # calculate relation matrix
        R = model.getUnitRelation(
            units = self.settings['units'],
            preprocessing = self.settings['preprocessing'],
            relation = self.settings['relation'],
            eval = self.settings['eval'],
            modify = self.settings['modify'],
            statistics = self.settings['statistics'])

        # create figure object
        fig = matplotlib.pyplot.figure()
        ax = fig.add_subplot(111)
        ax.grid(True)
        cax = ax.imshow(R,
            cmap = matplotlib.cm.hot_r,
            interpolation = self.settings['interpolation'],
            extent = (0, R.shape[1], 0, R.shape[0]))

        # create labels for x-axis
        xLabelIDs = self.settings['units'][1]
        xLabels = model.network.getNodeLabels(xLabelIDs)
        matplotlib.pyplot.xticks(
            numpy.arange(len(xLabels)) + 0.5,
            tuple(xLabels),
            fontsize = 8,
            rotation = 65)

        # create labels for y-axis
        yLabelIDs = self.settings['units'][0]
        yLabels = model.network.getNodeLabels(yLabelIDs)
        matplotlib.pyplot.yticks(
            len(yLabels) - numpy.arange(len(yLabels)) - 0.5,
            tuple(yLabels),
            fontsize = 8)

        # create colorbar
        cbar = fig.colorbar(cax)
        for tick in cbar.ax.get_yticklabels():
            tick.set_fontsize(9)

        # draw figure title / caption
        if self.settings['show_figure_caption']:
            title = "%s: %s" % (model.dataset.cfg['name'],
                nemoa.common.strSplitParams(self.settings['relation'])[0])

            # draw title
            matplotlib.pyplot.title(title, fontsize = 11)

        # output
        if file:
            matplotlib.pyplot.savefig(file, dpi = self.settings['dpi'])
        else:
            matplotlib.pyplot.show()

        # clear current figure object and release memory
        matplotlib.pyplot.clf()
        matplotlib.pyplot.close(fig)

        return True
