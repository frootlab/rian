# -*- coding: utf-8 -*-
"""Restricted Boltzmann Machine class networks.

Various classes of restricted boltzmann machines aimed for data modeling
and per layer pretraining of multilayer feedforward artificial neural
networks
"""

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.system.ann
import numpy

class rbm(nemoa.system.ann.ann):
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
            'visibleClass': 'sigmoid',
            'hiddenClass': 'sigmoid' },
        'init': {
            'checkDataset': False,
            'ignoreUnits': [],
            'wSigma': 0.5 },
        'optimize': {
            'checkDataset': False,
            'ignoreUnits': [],
            'minibatch_size': 100,
            'minibatch_update_interval': 10,
            'updates': 100000,
            'algorithm': 'vrcd',
            'update_cd_sampling_steps': 1,
            'update_cd_sampling_iterations': 1,
            'update_rate': 0.1,
            'update_factor_weights': 1.,
            'update_factor_hbias': 0.1,
            'update_factor_vbias': 0.1,
            'mod_sa_enable': True,
            'mod_sa_init_temperature': 1.,
            'mod_sa_annealing_factor': 1.,
            'mod_sa_annealing_cycles': 1,
            'mod_kl_enable': True,
            'mod_kl_rate': 0.,
            'mod_kl_expect': 0.5,
            'mod_corruption_enable': True,
            'mod_corruption_type': 'mask',
            'mod_corruption_factor': 0.5,
            'useAdjacency': False,
            'tracker_obj_function': 'error',
            'tracker_eval_time_interval': 10. ,
            'tracker_estimate_time': True,
            'tracker_estimate_timeWait': 20. }}

    def mapping(self):
        v = self._params['units'][0]['name']
        h = self._params['units'][1]['name']
        return (v, h, v)

    def _get_test_data(self, dataset):
        """Return tuple with default test data."""
        data = dataset.data()
        return (data, data)

    def _check_dataset(self, dataset):
        """Check if dataset contains binary values."""
        if not nemoa.type.is_dataset(dataset): return nemoa.log('error',
            'could not test dataset: invalid dataset instance given!')
        if not dataset._is_binary(): return nemoa.log('error',
            "dataset '%s' is not valid: RBMs expect binary data."
            % (dataset.name()))
        return True

    def _set_update_rates(self, **config):
        """Initialize updates for system parameters."""
        if not 'optimize' in self._config: self._config['optimize'] = {}
        return (self._setVisibleUnitUpdateRates(**config)
            and self._setHiddenUnitUpdateRates(**config)
            and self._setLinkUpdateRates(**config))

    def _set_params(self, params):
        """Set system parameters from dictionary."""
        return (self._set_visible_unit_params(params)
            and self._set_hidden_unit_params(params)
            and self._set_link_params(params))

    def _optimize_params(self, dataset, schedule, tracker):
        """Optimize system parameters."""

        cfg = self._config['optimize']

        if cfg['mod_corruption_enable']: nemoa.log(
            'note', """using data corruption for denoising with
            noise model '%s (%.2f)'""" % (
            cfg['mod_corruption_type'], cfg['mod_corruption_factor']))
        if cfg['mod_kl_enable']: nemoa.log('note',
            """using Kullback-Leibler penalty for sparse coding
            with expectation value %.2f""" % (cfg['mod_kl_expect']))
        if cfg['mod_vmra_enable']: nemoa.log('note',
            """using variance maximizing rate adaption
            with length %i""" % (cfg['mod_vmra_length']))
        if cfg['mod_sa_enable']: nemoa.log('note',
            """using simulated annealing  with initial temperature %.2f
            and annealing factor %.2f""" % (cfg['mod_sa_init_temperature'],
            cfg['mod_sa_annealing_factor']))

        if cfg['algorithm'].lower() == 'cd': return \
            self._optimize_cd(dataset, schedule, tracker)
        return nemoa.log('error', """could not optimize model:
            unknown optimization algorithm '%s'""" % (algorithm))

    def _optimize_cd(self, dataset, schedule, tracker):
        """Optimize system parameters with Contrastive Divergency."""

        cfg  = self._config['optimize']

        while tracker.update():

            # get data (sample from minibatches)
            if tracker.get('epoch') % cfg['minibatch_update_interval'] == 0:
                data = self._optimize_get_data(dataset)

            self._optimize_cd_update(data, tracker) # Update system parameters

        return True

    def _optimize_vmra_update_rate(self, tracker):
        store = tracker.read('vmra')
        var = numpy.var(self._params['links'][(0, 1)]['W'])
        if not 'wVar' in store: wVar = numpy.array([var])
        else: wVar = numpy.append([var], store['wVar'])

        cfg = self._config['optimize']
        length = cfg['mod_vmra_length']
        if wVar.shape[0] > length:

            wVar = wVar[:length]
            A = numpy.array([numpy.arange(0, length),
                numpy.ones(length)])
            grad = - numpy.linalg.lstsq(A.T, wVar)[0][0]
            delw = cfg['mod_vmra_factor'] * grad

            cfg['update_rate'] = min(max(delw,
                cfg['mod_vmra_min_rate']), cfg['mod_vmra_max_rate'])

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

        hData = self._eval_units_expect(data, ('visible', 'hidden'))
        if k == 1 and m == 1:
            vModel = self._eval_units_samples(hData, ('hidden', 'visible'),
                expectLast = True)
            hModel = self._eval_units_expect(vModel, ('visible', 'hidden'))
            return data, hData, vModel, hModel

        vModel = numpy.zeros(shape = data.shape)
        hModel = numpy.zeros(shape = hData.shape)
        for i in xrange(m):
            for j in xrange(k):

                # calculate hSample from hExpect
                # in first sampling step init hSample with h_data
                if j == 0: hSample = self._eval_units_samples(
                    hData, ('hidden', ))
                else: hSample = self._eval_units_samples(hExpect, (
                    'hidden', ))

                # calculate vExpect from hSample
                vExpect = self._eval_units_expect(hSample, ('hidden',
                    'visible'))

                # calculate hExpect from vSample
                # in last sampling step use vExpect
                # instead of vSample to reduce noise
                if j + 1 == k: hExpect = self._eval_units_expect(vExpect,
                    ('visible', 'hidden'))
                else: hExpect = self._eval_units_samples(vExpect,
                    ('visible', 'hidden'), expectLast = True)

            vModel += vExpect / m
            hModel += hExpect / m

        return data, hData, vModel, hModel

    def _optimize_cd_update(self, data, tracker):
        """Update system parameters."""

        config = self._config['optimize']
        ignore = config['ignoreUnits']

        # (optional) Variance maximizing rate adaption
        if config['mod_vmra_enable']:
            if tracker.get('epoch') % config['mod_vmra_update_interval'] == 0 \
                and tracker.get('epoch') > config['mod_vmra_init_wait']:
                self._optimize_vmra_update_rate(tracker)

        # get system estimations (model)
        dTuple = self._optimize_cd_sampling(data)

        # Calculate contrastive divergency updates
        # (without affecting the calculations)
        if not 'visible' in ignore: deltaV = self._optimize_cd_delta_visible(*dTuple)
        if not 'hidden' in ignore: deltaH = self._optimize_cd_delta_hidden(*dTuple)
        if not 'links' in ignore: deltaL = self._optimize_cd_delta_links(*dTuple)

        # Contrastive Divergency update
        if not 'visible' in ignore: self._units['visible'].update(deltaV)
        if not 'hidden' in ignore: self._units['hidden'].update(deltaH)
        if not 'links' in ignore: self._optimize_update_links(**deltaL)

        # (optional) Kullback-Leibler penalty update for sparsity
        if config['mod_kl_enable']:
            if not 'hidden' in ignore: self._units['hidden'].update(
                self._optimize_kl_delta_hidden(*dTuple))

        # (optional) Simulated Annealing update to avoid underfitting
        if config['mod_sa_enable']:
            if not 'visible' in ignore: self._units['visible'].update(
                self._optimize_sa_delta_visible(tracker))
            if not 'hidden' in ignore: self._units['hidden'].update(
                self._optimize_sa_delta_hidden(tracker))
            if not 'links' in ignore: self._optimize_update_links(
                **self._optimize_sa_delta_links(tracker))

        return True

    def _optimize_cd_delta_visible(self, vData, hData, vModel, hModel, **kwargs):
        """Constrastive divergency gradients of visible units.

        Returns:
            Dictionary with numpy arrays containing visible unit
            parameter gradients, calculated by contrastive divergency.
        """

        cfg = self._config['optimize']

        r = cfg['update_rate'] * cfg['update_factor_vbias'] # update rate
        v = len(self._units['visible'].params['label'])
        diff = numpy.mean(vData - vModel, axis = 0).reshape((1, v))

        return { 'bias': r * diff }

    def _optimize_cd_delta_hidden(self, vData, hData, vModel, hModel, **kwargs):
        """Constrastive divergency gradients of hidden units.

        Returns:
            Dictionary with numpy arrays containing hidden unit
            parameter gradients, calculated by contrastive divergency.
        """

        cfg = self._config['optimize']

        h = len(self._units['hidden'].params['label'])
        r = cfg['update_rate'] * cfg['update_factor_hbias'] # update rate
        diff = numpy.mean(hData - hModel, axis = 0).reshape((1, h))

        return { 'bias': r * diff }

    def _optimize_cd_delta_links(self, vData, hData, vModel, hModel, **kwargs):
        """Constrastive divergency gradients of links.

        Returns:
            Dictionary with numpy arrays containing link parameter
            gradients, calculated by contrastive divergency.
        """

        cfg = self._config['optimize']

        D = numpy.dot(vData.T, hData) / float(vData.size)
        M = numpy.dot(vModel.T, hModel) / float(vData.size)
        r = cfg['update_rate'] * cfg['update_factor_weights'] # update rate

        return { 'W': r * (D - M) }

    def _optimize_kl_delta_hidden(self, vData, hData, vModel, hModel):
        """Kullback-Leibler penalty gradients of hidden units.

        Returns:
            Dictionary with numpy arrays containing hidden unit
            parameter gradients, calculated by Kullback-Leibler penalty,
            which uses l1-norm cross entropy.
        """

        cfg = self._config['optimize']

        p = cfg['mod_kl_expect'] # target expectation value
        q = numpy.mean(hData, axis = 0) # expectation value over samples
        r = max(cfg['update_rate'], cfg['mod_kl_rate']) # update rate

        return { 'bias': r * (p - q) }

    def _optimize_sa_delta_hidden(self, tracker):
        cfg = self._config['optimize']
        #cfg['mod_sa_init_temperature'], cfg['mod_sa_annealing_factor']

        #dBias = numpy.zeros([1, hData.shape[1]])

        #return { 'bias': dBias }
        return {}

    def _optimize_sa_delta_visible(self, tracker):
        cfg = self._config['optimize']
        #cfg['mod_sa_init_temperature'], cfg['mod_sa_annealing_factor']

        #dBias = numpy.zeros([1, vData.shape[1]])

        #return { 'bias': dBias }
        return {}

    def _optimize_sa_delta_links(self, tracker):
        cfg = self._config['optimize']
        params = tracker.read('sa')
        if params:
            initRate = params['initRate']
        else:
            initRate = cfg['update_rate']
            tracker.write('sa', initRate = initRate)

        shape = self._params['links'][(0, 1)]['W'].shape
        r = initRate ** 2 / cfg['update_rate'] * cfg['update_factor_weights']
        temperature = self._optimize_sa_temperature(tracker)
        if temperature == 0.: return {}
        sigma = r * temperature
        W = numpy.random.normal(0., sigma, shape)

        return { 'W': W }

    def _optimize_sa_temperature(self, tracker):
        """Calculate temperature for simulated annealing."""
        config = self._config['optimize']

        init      = float(config['mod_sa_init_temperature'])
        annealing = float(config['mod_sa_annealing_factor'])
        cycles    = float(config['mod_sa_annealing_cycles'])
        updates   = int(float(config['updates']) / cycles)
        epoch     = float(tracker.get('epoch') % updates)
        heat      = init * (1. - epoch / float(updates)) ** annealing

        if heat < config['mod_sa_min_temperature']: return 0.
        return heat

    #def _get_units_from_config(self):
        #"""Return tuple with unit information created from config."""

        #if isinstance(self._config['params']['visible'], int):
            #vLabel = ['v:v%i' % (num) for num \
                #in xrange(1, self._config['params']['visible'] + 1)]
        #elif isinstance(self._config['params']['visible'], list):
            #for node in self._config['params']['visible']:
                #if not isinstance(node, str):
                    #return None
            #vLabel = self._config['params']['visible']
        #else: vLabel = []
        #if isinstance(self._config['params']['hidden'], int):
            #hLabel = ['h:h%i' % (num) for num \
                #in xrange(1, self._config['params']['hidden'] + 1)]
        #elif isinstance(self._config['params']['hidden'], list):
            #for node in self._config['params']['hidden']:
                #if not isinstance(node, str):
                    #return None
            #hLabel = self._config['params']['hidden']
        #else: hLabel = []

        #return [{
            #'id': 0, 'name': 'visible',
            #'visible': True, 'label': vLabel,
        #}, {
            #'id': 1, 'name': 'hidden',
            #'visible': False, 'label': hLabel
        #}]

    #def _get_units_from_dataset(self, dataset):
        #"""Return tuple with lists of unit labels ([visible], [hidden]) using dataset for visible."""
        #return (dataset._get_col_labels(), self._units['hidden'].params['label'])

    ## TODO: generalize to ann
    #def _unlink_unit(self, unit):
        #"""Delete unit links in adjacency matrix."""
        #if unit in self._units['visible'].params['label']:
            #i = self._units['visible'].params['label'].index(unit)
            #self._params['links'][(0, 1)]['A'][i,:] = False
            #return True
        #if unit in self._units['hidden'].params['label']:
            #i = self._units['hidden'].params['label'].index(unit)
            #self._params['links'][(0, 1)]['A'][:,i] = False
            #return True
        #return False

    def _set_visible_unit_params(self, params):
        """Set parameters of visible units using dictionary."""
        return self._units['visible']._overwrite(params['units'][0])

    def _set_hidden_unit_params(self, params):
        """Set parameters of hidden units using dictionary."""
        return self._units['hidden']._overwrite(params['units'][1])

    def _get_links_from_config(self):
        """Return links from adjacency matrix."""
        links = []
        for i, v in enumerate(self._units['visible'].params['label']):
            for j, h in enumerate(self._units['hidden'].params['label']):
                if not 'A' in self._params \
                    or self._params['links'][(0, 1)]['A'][i, j]:
                    links.append((v, h))
        return links

    def _eval_system_energy(self, data, *args, **kwargs):
        """Pseudo energy function.

        Calculates the logarithm of the sum of exponential negative
        sample energies (plus one).

        """

        # mapping tuples for visible and hidden units
        map_visible = ('visible', )
        map_hidden = ('visible', 'hidden')

        # calculate energies of visible units
        energy_visible = self._eval_units_energy(
            data[0], mapping = map_visible).sum(axis = 1)

        # calculate hidden unit energies of all samples
        energy_hidden = self._eval_units_energy(
            data[0], mapping = map_hidden).sum(axis = 1)

        # calculate link energies of all samples
        energy_links = self._eval_links_energy(
            data[0], mapping = map_hidden).sum(axis = (1, 2))

        # calculate energies of all samples
        energy_vector = energy_visible + energy_hidden + energy_links

        # calculate (pseudo) energy of system
        energy = -numpy.log(1. + numpy.exp(-energy_vector).sum())

        return energy

    def _set_link_params(self, params):
        """Set link parameters and update link matrices using dictionary."""
        for i, v in enumerate(self._units['visible'].params['label']):
            if not v in params['units'][0]['label']:
                continue
            k = params['units'][0]['label'].index(v)
            for j, h in enumerate(self._units['hidden'].params['label']):
                if not h in params['units'][1]['label']:
                    continue
                l = params['units'][1]['label'].index(h)
                self._params['links'][(0, 1)]['A'][i, j] = params['A'][k, l]
                self._params['links'][(0, 1)]['W'][i, j] = params['W'][k, l]
        return True

    #def _remove_links(self, links = []):
        #"""Remove links from adjacency matrix using list of links."""
        #if not self._configure_test(self._params): # check params
            #nemoa.log('error', """
                #could not remove links:
                #units have not been set yet!""")
            #return False

        ## search links and update list of current links
        #curLinks = self._get_links_from_config() # get current links
        #for link in links:
            #found = False
            #if (link[0], link[1]) in curLinks:
                #del curLinks[curLinks.index((link[0], link[1]))]
                #found = True
            #if (link[1], link[0]) in curLinks:
                #del curLinks[curLinks.index((link[1], link[0]))]
                #found = True
            #if not found:
                #nemoa.log('warning', """could not delete link (%s → %s):
                    #link could not be found!""" % (link[0], link[1]))
                #continue

        #return self._configure_set_links(curLinks)

    def _optimize_update_links(self, **updates):
        """Set updates for links."""
        if 'W' in updates:
            self._params['links'][(0, 1)]['W'] += updates['W']
        if 'A' in updates:
            self._params['links'][(0, 1)]['A'] = updates['A']
        return True

class grbm(rbm):
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
            'visible': 'sigmoid',
            'hidden': 'sigmoid',
            'visibleClass': 'gauss',
            'hiddenClass': 'sigmoid' },
        'init': {
            'checkDataset': True,
            'ignoreUnits': [],
            'wSigma': 0.5 },
        'optimize': {
            'checkDataset': True, # check if data is gauss normalized
            'ignoreUnits': [], # do not ignore units on update (needed for stacked updates)
            'updates': 100000, # number of update steps / epochs
            'algorithm': 'cd', # algorithm used for updates
            'update_cd_sampling_steps': 1, # number of gibbs steps in cdk sampling
            'update_cd_sampling_iterations': 1, # number of iterations in cdk sampling
            'update_rate': 0.001, # update rate (depends in algorithm)
            'update_factor_weights': 1., # factor for weight updates (related to update rate)
            'update_factor_hbias': 0.1, # factor for hidden unit bias updates (related to update rate)
            'update_factor_vbias': 0.1, # factor for visible unit bias updates (related to update rate)
            'update_factor_vlvar': 0.01, # factor for visible unit logarithmic variance updates (related to update rate)
            'minibatch_size': 500, # number of samples used to calculate updates
            'minibatch_update_interval': 1, # number of updates the same minibatch is used
            'mod_corruption_enable': False,
            'mod_corruption_type': 'none', # do not use corruption
            'mod_corruption_factor': 0., # no corruption of data
            'mod_sa_enable': True, # use simulated annealing
            'mod_sa_init_temperature': 1.,
            'mod_sa_annealing_factor': 1.,
            'mod_sa_annealing_cycles': 1,
            'mod_kl_enable': True, # use Kullback-Leibler penalty
            'mod_kl_rate': 0., # sparsity update
            'mod_kl_expect': 0.5, # aimed value for l2-norm penalty
            'useAdjacency': False, # do not use selective weight updates
            'tracker_obj_function': 'error', # objective function
            'tracker_eval_time_interval': 20., # time interval for calculation the inspection function
            'tracker_estimate_time': True, # initally estimate time for whole optimization process
            'tracker_estimate_timeWait': 20. # time intervall used for time estimation
        }}

    def _check_dataset(self, dataset):
        """Check if dataset contains gauss normalized values."""
        if not nemoa.type.is_dataset(dataset): return nemoa.log('error',
            'could not test dataset: invalid dataset instance given!')
        if not dataset._eval_normalization_gauss(): return nemoa.log('error',
            """dataset '%s' is not valid: GRBMs expect
            standard normal distributed data.""" % (dataset.name()))
        return True

    def _optimize_cd_delta_visible(self, vData, hData, vModel, hModel,
        **kwargs):
        """Return cd gradient based updates for visible units.

        Constrastive divergency gradient of visible unit parameters
        using an modified energy function for faster convergence.
        See reference for modified Energy function.
        """

        cfg = self._config['optimize']

        v = len(self._units['visible'].params['label'])
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

    def _optimize_cd_delta_links(self, vData, hData, vModel, hModel,
        **kwargs):
        """Return cd gradient based updates for links.

        Constrastive divergency gradient of link parameters
        using an modified energy function for faster convergence.
        See reference for modified Energy function.

        """

        cfg = self._config['optimize']
        var = numpy.exp(self._units['visible'].params['lvar']).T # variance of visible units
        r = cfg['update_rate'] * cfg['update_factor_weights'] # update rate
        D = numpy.dot(vData.T, hData) / float(vData.size)
        M = numpy.dot(vModel.T, hModel) / float(vData.size)

        return { 'W': r * (D - M) / var }

    def _get_visible_unit_params(self, label):
        """Return system parameters of one specific visible unit."""
        id = self._units['visible'].params['label'].index(label)
        return {
            'bias': self._units['visible'].params['bias'][0, id],
            'sdev': numpy.sqrt(numpy.exp(
                self._units['visible'].params['lvar'][0, id])) }

    def _set_visible_unit_params(self, params):
        """Set parameters of visible units using dictionary."""
        return self._units['visible']._overwrite(params['units'][0])
