# -*- coding: utf-8 -*-
"""Artificial Neuronal Network (ANN) Evaluation.

This module includes various implementations for quantifying structural
and statistical values of whole artificial neural networks, units, links
and relations. These methods include:

    (a) data based methods like data manipulation tests
    (b) graphical methods on weighted graphs
    (c) function based methods like partial derivations

"""

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import numpy

@nemoa.common.decorators.algorithm(
    name     = 'correlation',
    category = 'relation',
    directed = False,
    signed   = True,
    normal   = True,
    args     = 'all',
    retfmt   = 'scalar',
    plot     = 'heatmap',
    formater = lambda val: '%.3f' % (val)
)
def correlation(model, data, mapping = None, **kwargs):
    """Data correlation between source and target units.

    Undirected data based relation describing the 'linearity'
    between variables (units).

    Args:
        data: 2-tuple with numpy arrays: input data and output data
        mapping: tuple of strings containing the mapping
            from input layer (first argument of tuple)
            to output layer (last argument of tuple)

    Returns:
        Numpy array of shape (source, target) containing pairwise
        correlation between source and target units.

    """

    # 2do: allow correlation between hidden units

    # calculate symmetric correlation matrix
    corr = numpy.corrcoef(numpy.hstack(data).T)

    # create asymmetric output matrix
    mapping = model.system._get_mapping()
    srcunits = model.system._get_units(layer = mapping[0])
    tgtunits = model.system._get_units(layer = mapping[-1])
    units = srcunits + tgtunits
    relation = numpy.zeros(shape = (len(srcunits), len(tgtunits)))
    for i, u1 in enumerate(srcunits):
        k = units.index(u1)
        for j, u2 in enumerate(tgtunits):
            l = units.index(u2)
            relation[i, j] = corr[k, l]

    return relation

@nemoa.common.decorators.algorithm(
    name     = 'connectionweight',
    category = 'relation',
    directed = True,
    signed   = True,
    normal   = False,
    args     = 'all',
    retfmt   = 'scalar',
    plot     = 'heatmap',
    formater = lambda val: '%.3f' % (val)
)
def connectionweight(model, data, mapping = None, **kwargs):
    """Weight sum product from source to target units.

    Directed graph based relation describing the matrix product from
    source to target units (variables) given by mapping.

    Args:
        data: 2-tuple with numpy arrays: input data and output data
        mapping: tuple of strings containing the mapping
            from input layer (first argument of tuple)
            to output layer (last argument of tuple)

    Returns:
        Numpy array of shape (source, target) containing pairwise
        weight sum products from source to target units.

    """

    if not mapping: mapping = model.system._get_mapping()

    # calculate product of weight matrices
    for i in range(1, len(mapping))[::-1]:
        weights = model.system._units[mapping[i - 1]].links(
            {'layer': mapping[i]})['W']
        if i == len(mapping) - 1: wsp = weights.copy()
        else: wsp = numpy.dot(wsp.copy(), weights)

    return wsp.T

@nemoa.common.decorators.algorithm(
    name     = 'coinduction',
    category = 'relation',
    directed = True,
    signed   = False,
    normal   = False,
    args     = 'all',
    retfmt   = 'scalar',
    plot     = 'heatmap',
    formater = lambda val: '%.3f' % (val)
)
def coinduction(model, data, *args, **kwargs):
    """Coinduced deviation from source to target units."""

    # 2do: Open Problem:
    #       Normalization of CoInduction
    # Ideas:
    #       - Combine CoInduction with common distribution
    #         of induced values
    #       - Take a closer look to extreme Values

    # 2do: Proove:
    # CoInduction <=> Common distribution in 'deep' latent variables

    # algorithmic default parameters
    gauge = 0.1 # setting gauge lower than induction default
                # to increase sensitivity

    mapping = model.system._get_mapping()
    srcunits = model.system._get_units(layer = mapping[0])
    tgtunits = model.system._get_units(layer = mapping[-1])

    # prepare cooperation matrix
    coop = numpy.zeros((len(srcunits), len(srcunits)))

    # create keawords for induction measurement

    if not 'gauge' in kwargs: kwargs['gauge'] = gauge

    # calculate induction without manipulation
    ind = induction(data, *args, **kwargs)
    norm = numpy.sqrt((ind ** 2).sum(axis = 1))

    # calculate induction with manipulation
    for sid, sunit in enumerate(srcunits):

        # manipulate source unit values and calculate induction
        datamp = [numpy.copy(data[0]), data[1]]
        datamp[0][:, sid] = 10.0
        indmp = induction(datamp, *args, **kwargs)

        print(('manipulation of', sunit))
        vals = [-2., -1., -0.5, 0., 0.5, 1., 2.]
        maniparr = numpy.zeros(shape = (len(vals), data[0].shape[1]))
        for vid, val in enumerate(vals):
            datamod = [numpy.copy(data[0]), data[1]]
            datamod[0][:, sid] = val #+ datamod[0][:, sid].mean()
            indmod = induction(datamod, *args, **kwargs)
            maniparr[vid, :] = numpy.sqrt(((indmod - ind) ** 2).sum(axis = 1))
        manipvar = maniparr.var(axis = 0)
        #manipvar /= numpy.amax(manipvar)
        manipnorm = numpy.amax(manipvar)
        # 2do
        print((manipvar * 1000.))
        print((manipvar / manipnorm))

        coop[:,sid] = \
            numpy.sqrt(((indmp - ind) ** 2).sum(axis = 1))

    return coop

@nemoa.common.decorators.algorithm(
    name     = 'induction',
    category = 'relation',
    directed = True,
    signed   = False,
    normal   = False,
    args     = 'all',
    retfmt   = 'scalar',
    plot     = 'heatmap',
    formater = lambda val: '%.3f' % (val)
)
def induction(model, data, mapping = None, points = 10,
    amplify = 1., gauge = 0.25, contrast = 20.0, **kwargs):
    """Induced deviation from source to target units.

    Directed data manipulation based relation describing the induced
    deviation of reconstructed values of a given output unit, when
    manipulating the values of a given input unit.

    For each sample and for each source the induced deviation on
    target units is calculated by respectively fixing one sample,
    modifying the value for one source unit (n uniformly taken
    points from it's own distribution) and measuring the deviation
    of the expected valueas of each target unit. Then calculate the
    mean of deviations over a given percentage of the strongest
    induced deviations.

    Args:
        data: 2-tuple with numpy arrays: input data and output data
        mapping: tuple of strings containing the mapping
            from source layer (first argument of tuple)
            to target layer (last argument of tuple)
        points: number of points to extrapolate induction
        amplify: amplification of the modified source values
        gauge: cutoff for strongest induced deviations
        contrast:

    Returns:
        Numpy array of shape (source, target) containing pairwise
        induced deviation from source to target units.

    """

    if not mapping: mapping = model.system._get_mapping()
    iunits = model.system._get_units(layer = mapping[0])
    ounits = model.system._get_units(layer = mapping[-1])
    R = numpy.zeros((len(iunits), len(ounits)))

    # get indices of representatives
    rids = [int((i + 0.5) * int(float(data[0].shape[0])
        / points)) for i in range(points)]

    for iid, iunit in enumerate(iunits):
        icurve = amplify * numpy.take(
            numpy.sort(data[0][:, iid]), rids)

        # create output matrix for each output
        C = {ounit: numpy.zeros((data[0].shape[0], points)) \
            for ounit in ounits}
        for pid in range(points):
            idata  = data[0].copy()
            idata[:, iid] = icurve[pid]
            oexpect = unitexpect(model, idata, mapping = mapping)
            for tid, ounit in enumerate(ounits):
                C[ounit][:, pid] = oexpect[:, tid]

        # calculate mean of standard deviations of outputs
        for oid, ounit in enumerate(ounits):

            # calculate norm by mean over part of data
            bound = int((1. - gauge) * data[0].shape[0])
            subset = numpy.sort(C[ounit].std(axis = 1))[bound:]
            norm = subset.mean() / data[1][:, oid].std()

            # calculate influence
            R[iid, oid] = norm

    # amplify contrast of induction
    A = R.copy()
    for iid, iunit in enumerate(iunits):
        for oid, ounit in enumerate(ounits):
            if ':' in ounit: inlabel = ounit.split(':')[1]
            else: inlabel = ounit
            if ':' in iunit: outlabel = iunit.split(':')[1]
            else: outlabel = iunit
            if inlabel == outlabel: A[iid, oid] = 0.0
    bound = numpy.amax(A)

    intensify = nemoa.system.commons.math.intensify
    return intensify(R, factor = contrast, bound = bound)

@nemoa.common.decorators.algorithm(
    name     = 'energy',
    category = 'model',
    args     = 'all',
    formater = lambda val: '%.3f' % (val),
    optimum  = 'min'
)
def modelenergy(model, data, *args, **kwargs):
    """Sum of local link and unit energies."""

    mapping = list(model._get_mapping())
    energy = 0.

    # sum local unit energies
    for i in range(1, len(mapping) + 1):
        energy += unitenergy(model, data[0],
            mapping = tuple(mapping[:i])).sum(axis = 1)

    # sum local link energies
    for i in range(1, len(mapping)):
        energy += linksenergy(model, data[0],
            mapping = tuple(mapping[:i + 1])).sum(axis = (1, 2))

    # calculate (pseudo) energy of system
    return numpy.log(1. + numpy.exp(-energy).sum())

@nemoa.common.decorators.algorithm(
    name     = 'energy',
    category = 'units',
    args     = 'input',
    retfmt   = 'scalar',
    formater = lambda val: '%.3f' % (val),
    plot     = 'diagram'
)
def unitenergy(model, data, mapping = None):
    """Unit energies of target units.

    Args:
        data: numpy array containing source data corresponding to
            the source unit layer (first argument of the mapping)
        mapping: n-tuple of strings containing the mapping
            from source unit layer (first argument of tuple)
            to target unit layer (last argument of tuple)

    Returns:
        Numpy array of shape (data, targets).

    """

    # set mapping from input layer to output layer (if not set)
    if mapping == None: mapping = model.system._get_mapping()
    data = unitexpect(model, data, mapping)
    return model.system._units[mapping[-1]].energy(data)

@nemoa.common.decorators.algorithm(
    name     = 'links_energy',
    category = ('system', 'links', 'evaluation'),
    args     = 'input',
    retfmt   = 'scalar',
    formater = lambda val: '%.3f' % (val),
    plot     = 'diagram'
)
def linksenergy(model, data, mapping = None, **kwargs):
    """Return link energies of a layer.

    Args:
        mapping: tuple of strings containing the mapping
            from source unit layer (first argument of tuple)
            to target unit layer (last argument of tuple)

    """

    if len(mapping) == 1:
        # TODO
        return nemoa.log('error', """sorry: bad implementation of
            links_energy""")
    elif len(mapping) == 2:
        sdata = data
        tdata = unitvalues(model, sdata, mapping)
    else:
        sdata = unitexpect(model, data, mapping[0:-1])
        tdata = unitvalues(model, sdata, mapping[-2:])

    fullmapping = model.system._get_mapping()
    sid = fullmapping.index(mapping[-2])
    tid = fullmapping.index(mapping[-1])
    src = self._units[mapping[-2]].params
    tgt = self._units[mapping[-1]].params

    if (sid, tid) in model.system._params['links']:
        links = model.system._params['links'][(sid, tid)]
        return nemoa.system.commons.links.Links.energy(
            sdata, tdata, src, tgt, links)
    elif (tid, sid) in model.system._params['links']:
        links = model.system._params['links'][(tid, sid)]
        return nemoa.system.commons.links.Links.energy(
            tdata, sdata, tgt, src, links)
