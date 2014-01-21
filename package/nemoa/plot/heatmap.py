#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nemoa, nemoa.plot.base, numpy, matplotlib

class heatmap(nemoa.plot.base.plot):

    def getSettings(self):
        return {
            'output': 'file',
            'fileformat': 'pdf',
            'dpi': 600,
            'show_figure_caption': True,
            'interpolation': 'nearest'
        }

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
        
        # test relation matrix
        if not isinstance(R, numpy.ndarray): return nemoa.log('error',
            'could not plot heatmap: relation matrix is not valid!')

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
        yLabelIDs = self.settings['units'][0]
        yLabels = model.network.getNodeLabels(yLabelIDs)
        fontsize = 400.0 / float(max(len(xLabels), len(yLabels)))

        # plot labels
        matplotlib.pyplot.xticks(
            numpy.arange(len(xLabels)) + 0.5,
            tuple(xLabels), fontsize = fontsize, rotation = 65)
        matplotlib.pyplot.yticks(
            len(yLabels) - numpy.arange(len(yLabels)) - 0.5,
            tuple(yLabels), fontsize = fontsize)

        # create colorbar
        cbar = fig.colorbar(cax)
        for tick in cbar.ax.get_yticklabels(): tick.set_fontsize(9)

        # plot title
        if self.settings['show_figure_caption']: matplotlib.pyplot.title(
            nemoa.common.strSplitParams(
            self.settings['relation'])[0].title(), fontsize = 11)

        # output
        if file: matplotlib.pyplot.savefig(file, dpi = self.settings['dpi'])
        else: matplotlib.pyplot.show()

        # clear current figure object and release memory
        matplotlib.pyplot.clf()
        matplotlib.pyplot.close(fig)

        return True
