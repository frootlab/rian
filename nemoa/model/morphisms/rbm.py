# -*- coding: utf-8 -*-
"""Restricted Boltzmann Machine Morphisms."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

import numpy
from flab.base import catalog, mapping
from nemoa.core import ui
import nemoa.model.morphisms.ann

class RBM(nemoa.model.morphisms.ann.ANN):
    """Restricted Boltzmann Machine (RBM) Optimizer.

    Restricted Boltzmann Machines (1) are energy based undirected
    artificial neuronal networks with two layers with visible and
    hidden units. The visible layer contains binary distributed
    sigmoidal units to model data. The hidden layer contains binary
    distributed sigmoidal units to model data relations.

    Reference:
        (1) "A Practical Guide to Training Restricted Boltzmann
            Machines", Geoffrey E. Hinton, University of Toronto, 2010

    """

    _default = {
        'algorithm': 'cd',
        'updates': 100000,
        'minibatch_size': 100,
        'minibatch_update_interval': 10,
        'con_module': '',
        'denoising': '',
        'acc_module': 'vmra',
        'gen_module': 'rasa',
        'update_cd_sampling_steps': 1,
        'update_cd_sampling_iterations': 1,
        'update_rate': 0.1,
        'update_factor_weights': 1.,
        'update_factor_hbias': 0.1,
        'update_factor_vbias': 0.1,
        'gen_rasa_enable': False,
        'gen_rasa_init_temperature': 0.1,
        'gen_rasa_min_temperature': 0.01,
        'gen_rasa_annealing_factor': 5.,
        'gen_rasa_annealing_cycles': 1,
        'acc_vmra_init_rate': 0.0005,
        'acc_vmra_length': 2,
        'acc_vmra_update_interval': 10,
        'acc_vmra_init_wait': 100,
        'acc_vmra_factor': 10.,
        'acc_vmra_min_rate': 0.0005,
        'acc_vmra_max_rate': 0.02,
        'con_klpt_enable': False,
        'con_klpt_rate': 0.,
        'con_klpt_expect': 0.5,
        'noise_enable': False,
        'noise_type': 'mask',
        'noise_factor': 0.5,
        'adjacency_enable': False,
        'tracker_estimate_time': False,
        'tracker_estimate_time_wait': 15.,
        'tracker_obj_tracking_enable': True,
        'tracker_obj_init_wait': 0.01,
        'tracker_obj_function': 'accuracy',
        'tracker_obj_keep_optimum': True,
        'tracker_obj_update_interval': 100,
        'tracker_eval_enable': True,
        'tracker_eval_function': 'accuracy',
        'tracker_eval_time_interval': 10.,
        'ignore_units': [] }

    @catalog.custom(
        name     = 'cd',
        longname = 'contrastive divergency',
        category = 'optimization',
        type     = 'algorithm',
        syscheck = None)
    def _cdiv(self):
        """Contrastive Divergency parameter optimization."""

        system = self.model.system
        config = self._config

        # set enable flags for restriction extensions
        config['con_klpt_enable'] = False
        if config['con_module']:
            found = False
            if config['con_module'] == 'klpt':
                config['con_klpt_enable'] = True
                about = """Kullback-Leibler penalty (expectation
                    value %.2f)""" % config['con_klpt_expect']
                found = True
            if found:
                ui.info('using restriction: %s' % about)

        # set enable flags for denoising extensions
        if config['denoising']:
            found = False
            if config['denoising'].lower() == 'noise':
                config['noise_enable'] = True
                about = """data corruption (noise model '%s',
                    factor %.2f)""" % (config['noise_type'],
                    config['noise_factor'])
                found = True
            if found:
                ui.info('using denoising: %s' % (about))

        # set enable flags for acceleration extensions
        config['acc_vmra_enable'] = False
        if config['acc_module']:
            found = False
            if config['acc_module'].lower() == 'vmra':
                config['acc_vmra_enable'] = True
                about = """variance maximizing rate adaption (tail
                    length %i)""" % config['acc_vmra_length']
                found = True
            if found:
                ui.info('using acceleration: %s' % about)

        # set enable flags for globalization extensions
        config['gen_rasa_enable'] = False
        if config['gen_module']:
            found = False
            if config['gen_module'].lower() == 'rasa':
                config['gen_rasa_enable'] = True
                about = """rate adaptive annealing (temperature %.1f,
                    annealing %.1f)""" % (
                    config['gen_rasa_init_temperature'],
                    config['gen_rasa_annealing_factor'])
                found = True
            if found:
                ui.info('using generalization: %s' % (about))

        # init rasa
        self.write('sa', init_rate=config['update_rate'])

        while self.update():
            # get training data (sample from stratified minibatches)
            data = self._get_data_training()[0]
            # update parameters
            self._cdiv_update(data)

        return True

    def _cdiv_update(self, data):
        """Update system parameters."""

        system = self.model.system
        config = self._config

        updatev = not 'visible' in config['ignore_units']
        updateh = not 'hidden' in config['ignore_units']
        updatel = not 'links' in config['ignore_units']

        # (optional) variance maximizing rate adaption
        if config['acc_vmra_enable']:
            epoch = self._get_epoch()
            if epoch % config['acc_vmra_update_interval'] == 0 \
                and epoch > config['acc_vmra_init_wait']:
                self._cdiv_update_rate_vmra()

        # get updates of system parameters
        sampling = self._cdiv_sampling(data)
        if updatev: deltav = self._cdiv_delta_visible(sampling)
        if updateh: deltah = self._cdiv_delta_hidden(sampling)
        if updatel: deltal = self._cdiv_delta_links(sampling)

        # update system parameters
        if updatev: system._units['visible'].update(deltav)
        if updateh: system._units['hidden'].update(deltah)
        if updatel: self._cdiv_update_links(**deltal)

        return True

    def _cdiv_update_rate_vmra(self):
        """ """

        system = self.model.system
        config = self._config

        store = self.read('vmra') or {}
        var = numpy.var(system._params['links'][(0, 1)]['W'])
        if 'wvar' not in store: wvar = numpy.array([var])
        else: wvar = numpy.append([var], store['wvar'])

        length = config['acc_vmra_length']
        if wvar.shape[0] > length:

            wvar = wvar[:length]
            A = numpy.array([numpy.arange(0, length),
                numpy.ones(length)])
            grad = - numpy.linalg.lstsq(A.T, wvar, rcond = None)[0][0]
            delw = config['acc_vmra_factor'] * grad

            config['update_rate'] = min(max(delw,
                config['acc_vmra_min_rate']),
                config['acc_vmra_max_rate'])

        self.write('vmra', wvar = wvar)
        return True

    def _cdiv_sampling(self, data):
        """Contrastive divergency sampling.

        Args:
            data:
            (k steps, m iterations)

        Returns:
            tuple (vData, hData, vModel, hModel)
            containing numpy arrays:
                vdata: input data of visible units
                hdata: expected values of hidden units for vData
                vmodel: sampled values of visible units after $k$
                    sampling steps calculated as mean values over $m$
                    iterations.
                hmodel: expected values of hidden units for vmodel

        """

        system = self.model.system
        config = self._config

        k = config['update_cd_sampling_steps']
        m = config['update_cd_sampling_iterations']

        hdata = system._get_unitexpect(data, ('visible', 'hidden'))
        if k == 1 and m == 1:
            vmodel = system._get_unitsamples(hdata,
                ('hidden', 'visible'), expect_last = True)
            hmodel = system._get_unitexpect(vmodel,
                ('visible', 'hidden'))
            return data, hdata, vmodel, hmodel

        vmodel = numpy.zeros(shape = data.shape)
        hmodel = numpy.zeros(shape = hdata.shape)
        for i in range(m):
            for j in range(k):

                # calculate hsample from hexpect
                # in first sampling step init hsample with h_data
                if j == 0:
                    hsample = system._get_unitsamples(
                        hdata, ('hidden', ))
                else:
                    hsample = system._get_unitsamples(
                        hexpect, ('hidden', ))

                # calculate vexpect from hsample
                vexpect = system._get_unitexpect(
                    hsample, ('hidden', 'visible'))

                # calculate hexpect from vsample
                # in last sampling step use vexpect
                # instead of vsample to reduce noise
                if j + 1 == k:
                    hexpect = system._get_unitexpect(
                        vexpect, ('visible', 'hidden'))
                else:
                    hexpect = system._get_unitsamples(vexpect,
                        ('visible', 'hidden'), expect_last = True)

            vmodel += vexpect / m
            hmodel += hexpect / m

        return data, hdata, vmodel, hmodel

    def _cdiv_delta_visible(self, sampling):
        """ """

        system = self.model.system
        config = self._config

        deltas = []
        if config['algorithm'] == 'cd':
            deltas.append(self._cdiv_delta_visible_cd(*sampling))
        if config['con_klpt_enable']:
            deltas.append(self._cdiv_delta_visible_klpt(*sampling))
        if config['gen_rasa_enable']:
            deltas.append(self._cdiv_delta_visible_rasa())

        return mapping.sumjoin(*deltas)

    def _cdiv_delta_visible_cd(self, vdata, hdata, vmodel, hmodel, **kwds):
        """Constrastive divergency gradients of visible units.

        Returns:
            Dictionary with numpy arrays containing visible unit
            parameter gradients, calculated by contrastive divergency.
        """

        system = self.model.system
        config = self._config

        r = config['update_rate'] * config['update_factor_vbias']
        v = len(system._units['visible'].params['id'])
        d = numpy.mean(vdata - vmodel, axis = 0).reshape((1, v))

        return { 'bias': r * d }

    def _cdiv_delta_visible_klpt(self, vdata, hdata, vmodel, hmodel):
        """ """

        return {}

    def _cdiv_delta_visible_rasa(self):
        """ """

        system = self.model.system
        config = self._config

        # calculate temperature (t) and rate adaptive coefficient (r)
        t = self._cdiv_rasa_temperature()
        if t == 0.: return {}
        r = self.read('sa')['init_rate'] ** 2 \
            / config['update_rate'] \
            * config['update_factor_vbias']

        shape = (1, len(system._units['visible'].params['id']))
        vb = numpy.random.normal(0., 1., shape)

        return { 'bias': r * t * vb }

    def _cdiv_delta_hidden(self, sampling):
        """ """

        system = self.model.system
        config = self._config

        deltas = []
        if config['algorithm'] == 'cd':
            deltas.append(self._cdiv_delta_hidden_cd(*sampling))
        if config['con_klpt_enable']:
            deltas.append(self._cdiv_delta_hidden_klpt(*sampling))
        if config['gen_rasa_enable']:
            deltas.append(self._cdiv_delta_hidden_rasa())

        return mapping.sumjoin(*deltas)

    def _cdiv_delta_hidden_cd(self, vdata, hdata, vmodel, hmodel, **kwds):
        """Constrastive divergency gradients of hidden units.

        Returns:
            Dictionary with numpy arrays containing hidden unit
            parameter gradients, calculated by contrastive divergency.

        """

        system = self.model.system
        config = self._config

        r = config['update_rate'] * config['update_factor_hbias']
        h = len(system._units['hidden'].params['id'])
        d = numpy.mean(hdata - hmodel, axis = 0).reshape((1, h))

        return { 'bias': r * d }

    def _cdiv_delta_hidden_klpt(self, vdata, hdata, vmodel, hmodel):
        """Kullback-Leibler penalty gradients of hidden units.

        Returns:
            Dictionary with numpy arrays containing hidden unit
            parameter gradients, calculated by Kullback-Leibler penalty,
            which uses l1-norm cross entropy.

        """

        system = self.model.system
        config = self._config

        # get expectation value target
        p = config['con_klpt_expect']

        # get current expectation value
        # 2do: test if hmodel is better
        q = numpy.mean(hdata, axis = 0)

        # get update rate
        r = max(config['update_rate'], config['con_klpt_rate'])

        return { 'bias': r * (p - q) }

    def _cdiv_delta_hidden_rasa(self):
        """ """

        system = self.model.system
        config = self._config

        # calculate temperature (t) and rate adaptive coefficient (r)
        t = self._cdiv_rasa_temperature()
        if t == 0.: return {}
        r = self.read('sa')['init_rate'] ** 2 \
            / config['update_rate'] \
            * config['update_factor_hbias']

        shape = (1, len(system._units['hidden'].params['id']))
        hb = numpy.random.normal(0., 1., shape)

        return { 'bias': r * t * hb }

    def _cdiv_delta_links(self, sampling):
        """ """

        system = self.model.system
        config = self._config

        deltas = []
        if config['algorithm'] == 'cd':
            deltas.append(self._cdiv_delta_links_cd(*sampling))
        if config['con_klpt_enable']:
            deltas.append(self._cdiv_delta_links_klpt(*sampling))
        if config['gen_rasa_enable']:
            deltas.append(self._cdiv_delta_links_rasa(deltas))

        return mapping.sumjoin(*deltas)

    def _cdiv_delta_links_cd(self, vdata, hdata, vmodel, hmodel, **kwds):
        """Constrastive divergency gradients of links.

        Returns:
            Dictionary with numpy arrays containing link parameter
            gradients, calculated by contrastive divergency.

        """

        system = self.model.system
        config = self._config

        r = config['update_rate'] * config['update_factor_weights']
        d = numpy.dot(vdata.T, hdata) / float(vdata.size)
        m = numpy.dot(vmodel.T, hmodel) / float(vdata.size)

        return { 'W': r * (d - m) }

    def _cdiv_delta_links_klpt(self, vdata, hdata, vmodel,
        hmodel, **kwds):
        """ """

        return {}

    def _cdiv_delta_links_rasa(self, deltas):
        """ """

        system = self.model.system
        config = self._config

        # calculate temperature (t) and rate adaptive coefficient (r)
        t = self._cdiv_rasa_temperature()
        if t == 0.: return {}
        r = self.read('sa')['init_rate'] ** 2 \
            / config['update_rate'] \
            * config['update_factor_weights']

        shape = system._params['links'][(0, 1)]['W'].shape
        weights = numpy.random.normal(0., 1., shape)

        return { 'W': r * t * weights }

    def _cdiv_rasa_temperature(self):
        """Calculate temperature for simulated annealing."""

        system = self.model.system
        config = self._config

        init = float(config['gen_rasa_init_temperature'])
        annealing = float(config['gen_rasa_annealing_factor'])
        cycles = float(config['gen_rasa_annealing_cycles'])
        updates = int(float(config['updates']) / cycles)
        epoch = float(self.get('epoch') % updates)
        heat = init * (1. - epoch / float(updates)) ** annealing

        if heat < config['gen_rasa_min_temperature']: return 0.

        return heat

    def _cdiv_update_links(self, **updates):
        """Set updates for links."""

        system = self.model.system
        links = system._params['links'][(0, 1)]

        if 'W' in updates: links['W'] += updates['W']
        if 'A' in updates: links['A'] = updates['A']

        return True

class GRBM(RBM):
    """Gaussian Restricted Boltzmann Machine (GRBM).

    Gaussian Restricted Boltzmann Machines (1) are energy based
    undirected artificial neuronal networks with two layers: visible
    and hidden. The visible layer contains gauss distributed
    gaussian units to model data. The hidden layer contains binary
    distributed sigmoidal units to model relations in the data.

    Reference:
        (1) "Improved Learning of Gaussian-Bernoulli Restricted
            Boltzmann Machines", KyungHyun Cho, Alexander Ilin and
            Tapani Raiko, ICANN 2011

    """

    _default = {
        'algorithm': 'cd',
        'updates': 100000,
        'update_rate': 0.0005,
        'update_factor_weights': 1.,
        'update_factor_hbias': 0.1,
        'update_factor_vbias': 0.1,
        'update_factor_vlvar': 0.01,
        'update_cd_sampling_steps': 1,
        'update_cd_sampling_iterations': 1,
        'minibatch_size': 100,
        'minibatch_update_interval': 1,
        'con_module': '',
        'denoising': 'noise',
        'acc_module': 'vmra',
        'gen_module': 'rasa',
        'acc_vmra_init_rate': 0.0005,
        'acc_vmra_length': 3,
        'acc_vmra_update_interval': 10,
        'acc_vmra_init_wait': 100,
        'acc_vmra_factor': 10.,
        'acc_vmra_min_rate': 0.0005,
        'acc_vmra_max_rate': 0.02,
        'gen_rasa_init_temperature': 10.,
        'gen_rasa_min_temperature': 0.01,
        'gen_rasa_annealing_factor': 10.,
        'gen_rasa_annealing_cycles': 2,
        'con_klpt_rate': 0.0001,
        'con_klpt_expect': 0.35,
        'noise_enable': True,
        'noise_type': 'gauss',
        'noise_factor': 0.75,
        'tracker_estimate_time': False,
        'tracker_estimate_time_wait': 15.,
        'tracker_obj_tracking_enable': True,
        'tracker_obj_init_wait': 0.01,
        'tracker_obj_function': 'accuracy',
        'tracker_obj_keep_optimum': True,
        'tracker_obj_update_interval': 100,
        'tracker_eval_enable': True,
        'tracker_eval_function': 'accuracy',
        'tracker_eval_time_interval': 10.,
        'ignore_units': [] }

    def _cdiv_delta_visible_cd(self, vdata, hdata, vmodel,
        hmodel, **kwds):
        """Return cd gradient based updates for visible units.

        Constrastive divergency gradient of visible unit parameters
        using an modified energy function for faster convergence.
        See reference for modified Energy function.

        """

        system = self.model.system
        config = self._config

        v = len(system._units['visible'].params['id'])
        w = system._params['links'][(0, 1)]['W']
        var = numpy.exp(system._units['visible'].params['lvar'])
        b = system._units['visible'].params['bias']
        d = numpy.mean(0.5 * (vdata - b) ** 2 \
            - vdata * numpy.dot(hdata, w.T), axis = 0).reshape((1, v))
        m = numpy.mean(0.5 * (vmodel - b) ** 2 \
            - vmodel * numpy.dot(hmodel, w.T), axis = 0).reshape((1, v))
        diff = numpy.mean(vdata - vmodel, axis = 0).reshape((1, v))

        r = config['update_rate']
        rb = r * config['update_factor_vbias']
        rv = r * config['update_factor_vlvar']

        return {
            'bias': rb * diff / var,
            'lvar': rv * (d - m) / var }

    def _cdiv_delta_links_cd(self, vdata, hdata, vmodel, hmodel,
        **kwds):
        """Return cd gradient based updates for links.

        Constrastive divergency gradient of link parameters
        using an modified energy function for faster convergence.
        See reference for modified Energy function.

        """

        system = self.model.system
        config = self._config

        var = numpy.exp(system._units['visible'].params['lvar']).T
        r = config['update_rate'] * config['update_factor_weights']
        d = numpy.dot(vdata.T, hdata)
        m = numpy.dot(vmodel.T, hmodel)
        s = float(vdata.size)

        return { 'W': r * (d - m) / s / var }
