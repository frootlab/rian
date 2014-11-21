# -*- coding: utf-8 -*-
"""Restricted Boltzmann Machine class networks.

Various classes of restricted boltzmann machines aimed for data modeling
and per layer pretraining of multilayer feedforward artificial neural
networks
"""

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.system.classes.ann
import numpy

class RBM(nemoa.system.classes.ann.ANN):
    """Restricted Boltzmann Machine (RBM).

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
        'params': {
            'samples': '*',
            'subnet': '*',
            'visible': 'auto',
            'hidden': 'auto',
            'visible_class': 'sigmoid',
            'hidden_class': 'sigmoid' },
        'init': {
            'check_dataset': False,
            'ignore_units': [],
            'w_sigma': 0.5 },
        'optimize': {
            'ignore_units': [],
            'minibatch_size': 100,
            'minibatch_update_interval': 10,
            'updates': 100000,
            'algorithm': 'cd',
            'con_module': 'klpt',
            'den_module': 'corr',
            'acc_module': 'vmra',
            'gen_module': 'rasa',
            'update_cd_sampling_steps': 1,
            'update_cd_sampling_iterations': 1,
            'update_rate': 0.1,
            'update_factor_weights': 1.,
            'update_factor_hbias': 0.1,
            'update_factor_vbias': 0.1,
            'gen_rasa_enable': True,
            'gen_rasa_init_temperature': 1.,
            'gen_rasa_annealing_factor': 1.,
            'gen_rasa_annealing_cycles': 1,
            'con_klpt_enable': True,
            'con_klpt_rate': 0.,
            'con_klpt_expect': 0.5,
            'den_corr_enable': True,
            'den_corr_type': 'mask',
            'den_corr_factor': 0.5,
            'adjacency_enable': False,
            'tracker_obj_function': 'error',
            'tracker_eval_time_interval': 10. ,
            'tracker_estimate_time': True,
            'tracker_estimate_time_wait': 20. }}

    def mapping(self):
        v = self._params['units'][0]['layer']
        h = self._params['units'][1]['layer']
        return (v, h, v)

    def _check_dataset(self, dataset):
        """Check if dataset contains binary values."""
        if not nemoa.type.isdataset(dataset):
            return nemoa.log('error', """could not test dataset:
                invalid dataset instance given.""")
        if not dataset._calc_test_binary():
            return nemoa.log('error', """dataset '%s' is not valid:
                RBMs expect binary data.""" % (dataset.name))
        return True

    def _optimize(self, dataset, schedule, tracker):
        """Optimize system parameters."""

        cfg = self._config['optimize']

        nemoa.log('note', "optimize '%s' (%s)" % \
            (self._get_name(), self._get_type()))

        nemoa.log('note', """using optimization algorithm '%s'"""
            % (cfg['algorithm']))

        # set enable flags for restriction extensions
        cfg['con_klpt_enable'] =  False
        if cfg['con_module']:
            found = False
            if cfg['con_module'] == 'klpt':
                cfg['con_klpt_enable'] =  True
                about = """Kullback-Leibler penalty (expectation
                    value %.2f)""" % (cfg['con_klpt_expect'])
                found = True
            if found:
                nemoa.log('note', 'using restriction: %s' % (about))

        # set enable flags for denoising extensions
        cfg['den_corr_enable'] = False
        if cfg['den_module']:
            found = False
            if cfg['den_module'].lower() == 'corr':
                cfg['den_corr_enable'] = True
                about = """data corruption (noise model '%s',
                    factor %.2f)""" % (cfg['den_corr_type'],
                    cfg['den_corr_factor'])
                found = True
            if found:
                nemoa.log('note', 'using denoising: %s' % (about))

        # set enable flags for acceleration extensions
        cfg['acc_vmra_enable'] = False
        if cfg['acc_module']:
            found = False
            if cfg['acc_module'].lower() == 'vmra':
                cfg['acc_vmra_enable'] = True
                about = """variance maximizing rate adaption (tail
                    length %i)""" % (cfg['acc_vmra_length'])
                found = True
            if found:
                nemoa.log('note', 'using acceleration: %s' % (about))

        # set enable flags for globalization extensions
        cfg['gen_rasa_enable'] =  False
        if cfg['gen_module']:
            found = False
            if cfg['gen_module'].lower() == 'rasa':
                cfg['gen_rasa_enable'] =  True
                about = """rate adaptive annealing (temperature %.1f,
                    annealing %.1f)""" % (
                    cfg['gen_rasa_init_temperature'],
                    cfg['gen_rasa_annealing_factor'])
                found = True
            if found:
                nemoa.log('note', 'using generalization: %s' % (about))

        # start optimization
        if cfg['algorithm'].lower() == 'cd':
            return self._optimize_cd(dataset, schedule, tracker)

        return nemoa.log('error', """could not optimize model:
            unknown optimization algorithm '%s'""" % (algorithm))

    def _optimize_cd(self, dataset, schedule, tracker):
        """Optimize system parameters with Contrastive Divergency."""

        data_update_interval = \
            self._config['optimize']['minibatch_update_interval']

        # init rasa
        tracker.write('sa',
            init_rate = self._config['optimize']['update_rate'])

        while tracker.update():

            # get data (stratified samples)
            if not tracker.get('epoch') % data_update_interval:
                data = self._optimize_get_data(dataset)

            # update system parameters
            self._optimize_cd_update(data, tracker)

        return True

    def _optimize_vmra_update_rate(self, tracker):
        store = tracker.read('vmra')
        var = numpy.var(self._params['links'][(0, 1)]['W'])
        if not 'wVar' in store: wVar = numpy.array([var])
        else: wVar = numpy.append([var], store['wVar'])

        cfg = self._config['optimize']
        length = cfg['acc_vmra_length']
        if wVar.shape[0] > length:

            wVar = wVar[:length]
            A = numpy.array([numpy.arange(0, length),
                numpy.ones(length)])
            grad = - numpy.linalg.lstsq(A.T, wVar)[0][0]
            delw = cfg['acc_vmra_factor'] * grad

            cfg['update_rate'] = min(max(delw,
                cfg['acc_vmra_min_rate']), cfg['acc_vmra_max_rate'])

        tracker.write('vmra', wVar = wVar)
        return True

    def _optimize_cd_sampling(self, data):
        """Contrastive divergency sampling.

        Args:
            data:
            (k steps, m iterations)

        Returns:
            tuple (vData, hData, vModel, hModel)
            containing numpy arrays:
                vData: input data of visible units
                hData: expected values of hidden units for vData
                vModel: sampled values of visible units after k sampling
                    steps calculated as mean values over m iterations.
                hModel: expected values of hidden units for vModel

        """

        cfg = self._config['optimize']

        k = cfg['update_cd_sampling_steps']
        m = cfg['update_cd_sampling_iterations']

        hData = self._calc_units_expect(data, ('visible', 'hidden'))
        if k == 1 and m == 1:
            vModel = self._calc_units_samples(hData,
                ('hidden', 'visible'), expect_last = True)
            hModel = self._calc_units_expect(vModel,
                ('visible', 'hidden'))
            return data, hData, vModel, hModel

        vModel = numpy.zeros(shape = data.shape)
        hModel = numpy.zeros(shape = hData.shape)
        for i in xrange(m):
            for j in xrange(k):

                # calculate hSample from hExpect
                # in first sampling step init hSample with h_data
                if j == 0: hSample = self._calc_units_samples(
                    hData, ('hidden', ))
                else: hSample = self._calc_units_samples(hExpect, (
                    'hidden', ))

                # calculate vExpect from hSample
                vExpect = self._calc_units_expect(
                    hSample, ('hidden', 'visible'))

                # calculate hExpect from vSample
                # in last sampling step use vExpect
                # instead of vSample to reduce noise
                if j + 1 == k: hExpect = self._calc_units_expect(
                    vExpect, ('visible', 'hidden'))
                else: hExpect = self._calc_units_samples(vExpect,
                    ('visible', 'hidden'), expect_last = True)

            vModel += vExpect / m
            hModel += hExpect / m

        return data, hData, vModel, hModel

    def _optimize_cd_update(self, data, tracker):
        """Update system parameters."""

        config = self._config['optimize']
        updatev = not 'visible' in config['ignore_units']
        updateh = not 'hidden' in config['ignore_units']
        updatel = not 'links' in config['ignore_units']

        # (optional) variance maximizing rate adaption
        if config['acc_vmra_enable']:
            if tracker.get('epoch') % \
                config['acc_vmra_update_interval'] == 0 \
                and tracker.get('epoch') > config['acc_vmra_init_wait']:
                self._optimize_vmra_update_rate(tracker)

        # get updates of system parameters
        sampling = self._optimize_cd_sampling(data)
        if updatev: deltav = self._get_delta_visible(sampling, tracker)
        if updateh: deltah = self._get_delta_hidden(sampling, tracker)
        if updatel: deltal = self._get_delta_links(sampling, tracker)

        # update system parameters
        if updatev: self._units['visible'].update(deltav)
        if updateh: self._units['hidden'].update(deltah)
        if updatel: self._optimize_update_links(**deltal)

        return True

    def _get_delta_visible(self, sampling, tracker):

        config = self._config['optimize']

        deltas = []
        if config['algorithm'] == 'cd':
            deltas.append(
                self._get_delta_visible_cd(*sampling))
        if config['con_klpt_enable']:
            deltas.append(
                self._get_delta_visible_klpt(*sampling))
        if config['gen_rasa_enable']:
            deltas.append(
                self._get_delta_visible_rasa(tracker))
        delta = nemoa.common.dict_sum(*deltas)

        return delta

    def _get_delta_visible_cd(self, vData, hData, vModel, hModel,
        **kwargs):
        """Constrastive divergency gradients of visible units.

        Returns:
            Dictionary with numpy arrays containing visible unit
            parameter gradients, calculated by contrastive divergency.
        """

        cfg = self._config['optimize']

        r = cfg['update_rate'] * cfg['update_factor_vbias']
        v = len(self._units['visible'].params['id'])
        d = numpy.mean(vData - vModel, axis = 0).reshape((1, v))

        return { 'bias': r * d }

    def _get_delta_visible_klpt(self, v_data, h_data, v_model,
        h_model):

        return {}

    def _get_delta_visible_rasa(self, tracker):

        # calculate temperature (t) and rate adaptive coefficient (r)
        t = self._optimize_rasa_temperature(tracker)
        if t == 0.: return {}
        config = self._config['optimize']
        r = tracker.read('sa')['init_rate'] ** 2 \
            / config['update_rate'] \
            * config['update_factor_vbias']

        shape = (1, len(self._units['visible'].params['id']))
        vb = numpy.random.normal(0., 1., shape)

        return { 'bias': r * t * vb }

    def _get_delta_hidden(self, sampling, tracker):

        config = self._config['optimize']

        deltas = []
        if config['algorithm'] == 'cd':
            deltas.append(
                self._get_delta_hidden_cd(*sampling))
        if config['con_klpt_enable']:
            deltas.append(
                self._get_delta_hidden_klpt(*sampling))
        if config['gen_rasa_enable']:
            deltas.append(
                self._get_delta_hidden_rasa(tracker))
        delta = nemoa.common.dict_sum(*deltas)

        return delta

    def _get_delta_hidden_cd(self, vData, hData, vModel, hModel,
        **kwargs):
        """Constrastive divergency gradients of hidden units.

        Returns:
            Dictionary with numpy arrays containing hidden unit
            parameter gradients, calculated by contrastive divergency.

        """

        config = self._config['optimize']

        r = config['update_rate'] * config['update_factor_hbias']
        h = len(self._units['hidden'].params['id'])
        d = numpy.mean(hData - hModel, axis = 0).reshape((1, h))

        return { 'bias': r * d }

    def _get_delta_hidden_klpt(self, vdata, hdata, vexpect,
        hexpect):
        """Kullback-Leibler penalty gradients of hidden units.

        Returns:
            Dictionary with numpy arrays containing hidden unit
            parameter gradients, calculated by Kullback-Leibler penalty,
            which uses l1-norm cross entropy.

        """

        config = self._config['optimize']

        # get expectation value target
        p = config['con_klpt_expect']

        # get current expectation value
        # Todo: test if hexpect is better
        q = numpy.mean(hdata, axis = 0)

        # get update rate
        r = max(config['update_rate'], config['con_klpt_rate'])

        return { 'bias': r * (p - q) }

    def _get_delta_hidden_rasa(self, tracker):

        # calculate temperature (t) and rate adaptive coefficient (r)
        t = self._optimize_rasa_temperature(tracker)
        if t == 0.: return {}
        config = self._config['optimize']
        r = tracker.read('sa')['init_rate'] ** 2 \
            / config['update_rate'] \
            * config['update_factor_hbias']

        shape = (1, len(self._units['hidden'].params['id']))
        hb = numpy.random.normal(0., 1., shape)

        return { 'bias': r * t * hb }

    def _get_delta_links(self, sampling, tracker):

        config = self._config['optimize']

        deltas = []
        if config['algorithm'] == 'cd':
            deltas.append(
                self._get_delta_links_cd(*sampling))
        if config['con_klpt_enable']:
            deltas.append(
                self._get_delta_links_klpt(*sampling))
        if config['gen_rasa_enable']:
            deltas.append(
                self._get_delta_links_rasa(deltas, tracker))
        delta = nemoa.common.dict_sum(*deltas)

        return delta

    def _get_delta_links_cd(self, vData, hData, vModel, hModel,
        **kwargs):
        """Constrastive divergency gradients of links.

        Returns:
            Dictionary with numpy arrays containing link parameter
            gradients, calculated by contrastive divergency.

        """

        config = self._config['optimize']

        r = config['update_rate'] * config['update_factor_weights']
        D = numpy.dot(vData.T, hData) / float(vData.size)
        M = numpy.dot(vModel.T, hModel) / float(vData.size)

        return { 'W': r * (D - M) }

    def _get_delta_links_klpt(self, v_data, h_data, v_model,
        h_model):

        return {}

    def _get_delta_links_rasa(self, deltas, tracker):

        # calculate temperature (t) and rate adaptive coefficient (r)
        t = self._optimize_rasa_temperature(tracker)
        if t == 0.: return {}
        config = self._config['optimize']
        r = tracker.read('sa')['init_rate'] ** 2 \
            / config['update_rate'] \
            * config['update_factor_weights']

        shape = self._params['links'][(0, 1)]['W'].shape
        W = numpy.random.normal(0., 1., shape)

        return { 'W': r * t * W }

    def _optimize_rasa_temperature(self, tracker):
        """Calculate temperature for simulated annealing."""

        config = self._config['optimize']
        init = float(config['gen_rasa_init_temperature'])
        annealing = float(config['gen_rasa_annealing_factor'])
        cycles = float(config['gen_rasa_annealing_cycles'])
        updates = int(float(config['updates']) / cycles)
        epoch = float(tracker.get('epoch') % updates)
        heat = init * (1. - epoch / float(updates)) ** annealing

        if heat < config['gen_rasa_min_temperature']: return 0.

        return heat

    def _calc_system_energy(self, data, *args, **kwargs):
        """Pseudo energy function.

        Calculates the logarithm of the sum of exponential negative
        sample energies (plus one).

        """

        # mapping tuples for visible and hidden units
        map_visible = ('visible', )
        map_hidden = ('visible', 'hidden')

        # calculate energies of visible units
        energy_visible = self._calc_units_energy(
            data[0], mapping = map_visible).sum(axis = 1)

        # calculate hidden unit energies of all samples
        energy_hidden = self._calc_units_energy(
            data[0], mapping = map_hidden).sum(axis = 1)

        # calculate link energies of all samples
        energy_links = self._calc_links_energy(
            data[0], mapping = map_hidden).sum(axis = (1, 2))

        # calculate energies of all samples
        energy_vector = energy_visible + energy_hidden + energy_links

        # calculate (pseudo) energy of system
        energy = -numpy.log(1. + numpy.exp(-energy_vector).sum())

        return energy

    def _optimize_update_links(self, **updates):
        """Set updates for links."""
        if 'W' in updates:
            self._params['links'][(0, 1)]['W'] += updates['W']
        if 'A' in updates:
            self._params['links'][(0, 1)]['A'] = updates['A']
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
        'params': {
            'samples': '*',
            'subnet': '*',
            'visible': 'auto',
            'hidden': 'auto',
            'visible_class': 'gauss',
            'hidden_class': 'sigmoid' },
        'init': {
            'check_dataset': False,
            'ignore_units': [],
            'w_sigma': 0.5 },
        'optimize': {
            'ignore_units': [],
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
            'den_module': 'corr',
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
            'den_corr_type': 'gauss',
            'den_corr_factor': 0.75,
            'tracker_estimate_time': False,
            'tracker_estimate_time_wait': 15.,
            'tracker_obj_tracking_enable': True,
            'tracker_obj_init_wait': 0.01,
            'tracker_obj_function': 'accuracy',
            'tracker_obj_keep_optimum': True,
            'tracker_obj_update_interval': 100,
            'tracker_eval_enable': True,
            'tracker_eval_function': 'accuracy',
            'tracker_eval_time_interval': 10. }}

    def _check_dataset(self, dataset):
        """Check if dataset contains gauss normalized values."""
        if not nemoa.type.isdataset(dataset):
            return nemoa.log('error', """could not test dataset:
                invalid dataset instance given.""")
        if not dataset.calc('test_gauss'):
            return nemoa.log('error', """dataset '%s' is not valid:
                GRBMs expect standard normal distributed data."""
                % (dataset.name))
        return True

    def _get_delta_visible_cd(self, vData, hData, vModel, hModel,
        **kwargs):
        """Return cd gradient based updates for visible units.

        Constrastive divergency gradient of visible unit parameters
        using an modified energy function for faster convergence.
        See reference for modified Energy function.
        """

        cfg = self._config['optimize']

        v = len(self._units['visible'].params['id'])
        W = self._params['links'][(0, 1)]['W']
        var = numpy.exp(self._units['visible'].params['lvar'])
        b = self._units['visible'].params['bias']
        r1 = cfg['update_rate'] * cfg['update_factor_vbias']
        r2 = cfg['update_rate'] * cfg['update_factor_vlvar']
        d = numpy.mean(0.5 * (vData - b) ** 2 \
            - vData * numpy.dot(hData, W.T), axis = 0).reshape((1, v))
        m = numpy.mean(0.5 * (vModel - b) ** 2 \
            - vModel * numpy.dot(hModel, W.T), axis = 0).reshape((1, v))
        diff = numpy.mean(vData - vModel, axis = 0).reshape((1, v))

        return {
            'bias': r1 * diff / var,
            'lvar': r2 * (d - m) / var }

    def _get_delta_links_cd(self, vData, hData, vModel, hModel,
        **kwargs):
        """Return cd gradient based updates for links.

        Constrastive divergency gradient of link parameters
        using an modified energy function for faster convergence.
        See reference for modified Energy function.

        """

        cfg = self._config['optimize']
        var = numpy.exp(self._units['visible'].params['lvar']).T
        r = cfg['update_rate'] * cfg['update_factor_weights']
        D = numpy.dot(vData.T, hData) / float(vData.size)
        M = numpy.dot(vModel.T, hModel) / float(vData.size)

        return { 'W': r * (D - M) / var }
