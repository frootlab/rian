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
        fig = matplotlib.pyplot.figure()
        ax = fig.add_subplot(111)
        ax.grid(True)
        cax = ax.imshow(data,
            cmap = matplotlib.cm.hot_r,
            interpolation = self.settings['interpolation'],
            extent = (0, data.shape[0], 0, data.shape[1]))

        # get labels and set plot ticks and labels
        labels = model.dataset.getRowLabels()

        matplotlib.pyplot.yticks(
            len(labels) - numpy.arange(len(labels)) - 0.5,
            tuple(labels),
            fontsize = 9)
            
        matplotlib.pyplot.xticks(
            numpy.arange(len(labels)) + 0.5,
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

class unitRelation(heatmap):

    def getDefaults(self):
        return {
            'x': None,
            'y': None,
            'relation': 'correlation()',
            'preprocessing': None,
            'statistics': 10000
        }

    def create(self, model, file = None):

        # use layer names for x and y
        # special case: units in ['visible', 'hidden']
        params = self.settings['params']
        for key in ['x', 'y']:
            if isinstance(params[key], list):
                # 2DO: check units
                continue
            if not isinstance(params[key], str) \
                or not params[key] in model.groups():
                nemoa.log('error', """
                    could not create plot:
                    unsupported value for parameter '%s': %s!
                    """ % (key, params[key]))
                return False
            params[key] = model.units(group = params[key])

        # calculate relation matrix
        data = model.getUnitRelations(
            units = (params['x'], params['y']),
            preprocessing = self.settings['preprocessing'],
            relation = self.settings['relation'],
            statistics = self.settings['statistics'])

        # create figure object
        fig = matplotlib.pyplot.figure()
        ax = fig.add_subplot(111)
        ax.grid(True)
        cax = ax.imshow(data,
            cmap = matplotlib.cm.hot_r,
            interpolation = settings['interpolation'],
            extent = (0, len(params['x']), 0, len(params['y'])))

        # create labels for x-axis
        xLabels = model.network.getNodeLabels(params['x'])
        matplotlib.pyplot.xticks(
            numpy.arange(len(xLabels)) + 0.5,
            tuple(xLabels),
            fontsize = 8,
            rotation = 65)

        # create labels for y-axis
        yLabels = model.network.getNodeLabels(params['y'])
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
