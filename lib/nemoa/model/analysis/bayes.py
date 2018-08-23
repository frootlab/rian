# -*- coding: utf-8 -*-
"""Bayesian network analysis.

This module includes various functions for the analysis of directed graphical
models, known as Bayesian networks. These models include linear models (LM),
feedforward neural networks (ANN).

The supported analysis functions are:

    (1) Sampler: Matrix valued statistical inference functions
        Returns numpy arrays of shape (d, n), where n is the number of
        target observables and d the size of the sample.
    (2) Sample statistics: Vectorial statistical inference functions
        Returns numpy arrays of shape (1, n), where n is the number of
        target observables
    (3) Objective functions: Scalar statistical inference functions
        Returns scalar value, that can be used to determin local optima
    (4) Association measures: Matrix valued statistical association measures
        Returns numpy arrays of shape (n, n), where n is the number of
        observables

"""

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import numpy

#
# (1) Bayesian network sampler
#

from nemoa.common.decorators import sampler

@sampler(
    name    = 'ancestral',
    title   = 'Ancestral Sampler',
    classes = ['LM', 'ANN']
)
def get_sample_ancestral_values(model, *args, **kwargs):
    """Forward sampled values of target observables.

    Args:
        data: numpy array containing data of the observables within the
            first layer in mapping
        mapping: n-tuple of strings that consecutively identify the layers
            within the mapping from the source observable layer (first argument)
            to the target observable layer (last argument)
        block: list of strings containing labels of source observables, which
            are 'ignored' by replacing their values by their means and therefore
            do not contribute to the variance of the sampled target values.
        expect_last: return expectation values of the units
            for the last step instead of maximum likelihood values.

    Returns:
        Numpy array of shape (data, targets).

    """

    return model.system._get_unitvalues(*args, **kwargs)

@sampler(
    name    = 'ancestralml',
    title   = 'Ancestral Maximum Likelihood Sampler',
    classes = ['LM', 'ANN']
)
def get_sample_ancestral_ml(model, *args, **kwargs):
    """Forward sampled maximum likelihood values of target observables.

    Args:
        data: numpy array containing data of the observables within the
            first layer in mapping
        mapping: n-tuple of strings that consecutively identify the layers
            within the mapping from the source observable layer (first argument)
            to the target observable layer (last argument)
        block: list of strings containing labels of source observables, which
            are 'ignored' by replacing their values by their means and therefore
            do not contribute to the variance of the sampled target values.

    Returns:
        Numpy array of shape (data, targets).

    """

    return model.system._get_unitexpect(*args, **kwargs)

@nemoa.common.decorators.algorithm(
    name     = 'samples',
    category = 'units',
    args     = 'input',
    retfmt   = 'vector',
    formater = lambda val: '%.3f' % (val),
    plot     = 'histogram'
)
def unitsamples(model, *args, **kwargs):
    """Sampled unit values of target units.

    Args:
        data: numpy array containing source data corresponding to
            the source unit layer (first argument of the mapping)
        mapping: n-tuple of strings containing the mapping
            from source unit layer (first argument of tuple)
            to target unit layer (last argument of tuple)
        block: list of strings containing labels of source units
            that are 'blocked' by setting their values to the means
            of their values.
        expect_last: return expectation values of the units
            for the last step instead of sampled values

    Returns:
        Numpy array of shape (data, targets).

    """

    return model.system._get_unitsamples(*args, **kwargs)

@nemoa.common.decorators.algorithm(
    name     = 'residuals',
    category = 'units',
    args     = 'all',
    retfmt   = 'vector',
    formater = lambda val: '%.3f' % (val),
    plot     = 'histogram'
)
def get_residuals(model, data, mapping = None, block = None):
    """Reconstruction residuals of target units.

    Args:
        data: 2-tuple of numpy arrays containing source and target
            data corresponding to the first and the last argument
            of the mapping
        mapping: n-tuple of strings containing the mapping
            from source unit layer (first argument of tuple)
            to target unit layer (last argument of tuple)
        block: list of strings containing labels of source units
            that are 'blocked' by setting their values to the means
            of their values.

    Returns:
        Numpy array of shape (data, targets).

    """

    d_src, d_tgt = data

    # set mapping: inLayer to outLayer (if not set)
    if mapping == None: mapping = model.system._get_mapping()

    # set unit values to mean (optional)
    if isinstance(block, list):
        d_src = numpy.copy(d_src)
        for i in block: d_src[:, i] = numpy.mean(d_src[:, i])

    # calculate prediction for response variables
    m_out = get_sample_ancestral(d_src, mapping)

    # calculate residuals
    return d_tgt - m_out

#
# (2) Bayesian network sample statistics
#

@nemoa.common.decorators.inference(
    name    = 'errorvector',
    title   = 'Reconstruction Error',
    classes = ['LM', 'ANN'],
    plot    = 'bar'
)
def get_error_vector(model, data, norm = 'MSE', **kwargs):
    """Reconstruction error of regressands.

    The reconstruction error is defined by:
        error := norm(residuals)

    Args:
        data: 2-tuple of numpy arrays containing source and target
            data corresponding to the first and the last layer in
            the mapping
        mapping: n-tuple of strings containing the mapping
            from source unit layer (first argument of tuple)
            to target unit layer (last argument of tuple)
        block: list of strings containing labels of source units
            that are blocked by setting the values to their means
        norm: used norm to calculate data reconstuction error from
            residuals. see nemoa.common.ndarray.meannorm for a list
            of provided norms

    """

    from nemoa.common.ndarray import meannorm

    res = get_residuals(data, **kwargs)
    error = meannorm(res, norm = norm)

    return error

@nemoa.common.decorators.algorithm(
    name     = 'accuracyvector',
    category = 'units',
    args     = 'all',
    retfmt   = 'scalar',
    formater = lambda val: '%.3f' % (val),
    plot     = 'diagram'
)
def get_accuracy_vector(model, data, norm = 'MSE', **kwargs):
    """Unit reconstruction accuracy.

    The unit reconstruction accuracy is defined by:
        accuracy := 1 - norm(residuals) / norm(data).

    Args:
        data: 2-tuple of numpy arrays containing source and target
            data corresponding to the first and the last layer
            in the mapping
        mapping: n-tuple of strings containing the mapping
            from source unit layer (first argument of tuple)
            to target unit layer (last argument of tuple)
        block: list of strings containing labels of source units
            that are blocked by setting the values to their means
        norm: used norm to calculate accuracy
            see nemoa.common.ndarray.meannorm for a list of provided
            norms

    """

    from nemoa.common.ndarray import meannorm

    res = get_residuals(data, **kwargs)
    normres = meannorm(res, norm = norm)
    normdat = meannorm(data[1], norm = norm)

    return 1. - normres / normdat

@nemoa.common.decorators.algorithm(
    name     = 'precisionvector',
    category = 'units',
    args     = 'all',
    retfmt   = 'scalar',
    formater = lambda val: '%.3f' % (val),
    plot     = 'diagram'
)
def get_precision_vector(model, data, norm = 'SD', **kwargs):
    """Unit reconstruction precision.

    The unit reconstruction precision is defined by:
        precision := 1 - dev(residuals) / dev(data).

    Args:
        data: 2-tuple of numpy arrays containing source and target
            data corresponding to the first and the last layer
            in the mapping
        mapping: n-tuple of strings containing the mapping
            from source unit layer (first argument of tuple)
            to target unit layer (last argument of tuple)
        block: list of strings containing labels of source units
            that are blocked by setting the values to their means
        norm: used norm to calculate deviation for precision
            see nemoa.common.ndarray.devnorm for a list of provided
            norms

    """

    from nemoa.common.ndarray import devnorm

    res = get_residuals(data, **kwargs)
    devres = devnorm(res, norm = norm)
    devdat = devnorm(data[1], norm = norm)

    return 1. - devres / devdat

@nemoa.common.decorators.inference(
    name     = 'mean',
    title    = 'Reconstructed Mean Values',
    category = 'units',
    plot     = 'bar'
)
def get_mean_vector(model, data, mapping = None, block = None):
    """Predicted mean values of response variables.

    Args:
        data: numpy array containing source data corresponding to
            the source unit layer (first argument of the mapping)
        mapping: n-tuple of strings containing the mapping
            from source unit layer (first argument of tuple)
            to target unit layer (last argument of tuple)
        block: list of strings containing labels of source units
            that are 'blocked' by setting their values to the means
            of their values.

    Returns:
        Numpy array of shape (targets).

    """

    if mapping == None: mapping = model.system._get_mapping()
    if block == None:
        model_out = unit_expect(data[0], mapping)
    else:
        data_in_copy = numpy.copy(data)
        for i in block:
            data_in_copy[:,i] = numpy.mean(data_in_copy[:,i])
        model_out = unit_expect(data_in_copy, mapping)

    return model_out.mean(axis = 0)

@nemoa.common.decorators.algorithm(
    name     = 'variance',
    category = 'units',
    args     = 'input',
    retfmt   = 'scalar',
    formater = lambda val: '%.3f' % (val),
    plot     = 'diagram'
)
def get_variance_vector(model, data, mapping = None, block = None):
    """Return variance of reconstructed unit values.

    Args:
        data: numpy array containing source data corresponding to
            the first layer in the mapping
        mapping: n-tuple of strings containing the mapping
            from source unit layer (first argument of tuple)
            to target unit layer (last argument of tuple)
        block: list of strings containing labels of source units
            that are blocked by setting the values to their means
    """

    if mapping == None: mapping = model.system._get_mapping()
    if block == None:
        model_out = get_sample_ancestral(data, mapping)
    else:
        data_in_copy = numpy.copy(data)
        for i in block:
            data_in_copy[:,i] = numpy.mean(data_in_copy[:,i])
        model_out = get_sample_ancestral(data_in_copy, mapping)

    return model_out.var(axis = 0)

#
# (3) Bayesian Network objective functions
#

@nemoa.common.decorators.objective(
    name    = 'error',
    title   = 'Mean Reconstruction Error',
    classes = ['LM', 'ANN'],
    optimum = 'min'
)
def get_error_scalar(model, *args, **kwargs):
    """Return mean error of regressands."""
    return numpy.mean(get_error_vector(model, *args, **kwargs))

@nemoa.common.decorators.objective(
    name    = 'accuracy',
    title   = 'Mean Reconstruction Accuracy',
    classes = ['LM', 'ANN'],
    optimum = 'max'
)
def get_accuracy_scalar(model, *args, **kwargs):
    """Return mean accuracy of regressands."""
    return numpy.mean(get_accuracy_vector(model, *args, **kwargs))

@nemoa.common.decorators.objective(
    name    = 'precision',
    title   = 'Mean Reconstruction Pricision',
    classes = ['LM', 'ANN'],
    optimum = 'max'
)
def get_precision_scalar(model, *args, **kwargs):
    """Return mean precision of regressands."""
    return numpy.mean(get_precision_vector(model, *args, **kwargs))

#
# (4) Bayesian Network Association Measures
#

@nemoa.common.decorators.algorithm(
    name     = 'knockout',
    category = 'relation',
    directed = True,
    signed   = True,
    normal   = False,
    args     = 'all',
    retfmt   = 'scalar',
    plot     = 'heatmap',
    formater = lambda val: '%.3f' % (val)
)
def knockout(model, data, mapping = None, **kwargs):
    """Knockout effect from source to target units.

    Directed data manipulation based relation describing the
    increase of the data reconstruction error of a given output
    unit, when setting the values of a given input unit to its mean
    value.

    Knockout single source units and measure effects on target units
    respective to given data

    Args:
        data: 2-tuple with numpy arrays: input data and output data
        mapping: tuple of strings containing the mapping
            from input layer (first argument of tuple)
            to output layer (last argument of tuple)

    Returns:
        Numpy array of shape (source, target) containing pairwise
        knockout effects from source to target units.

    """

    if not mapping: mapping = model.system._get_mapping()
    in_labels = model.system._get_units(layer = mapping[0])
    out_labels = model.system._get_units(layer = mapping[-1])

    # prepare knockout matrix
    R = numpy.zeros((len(in_labels), len(out_labels)))

    # calculate unit values without knockout
    if not 'measure' in kwargs: measure = 'error'
    else: measure = kwargs['measure']
    default = model.evaluate(algorithm = measure,
        category = 'units', mapping = mapping)

    if not default: return None

    # calculate unit values with knockout
    for in_id, in_unit in enumerate(in_labels):

        # modify unit and calculate unit values
        knockout = model.evaluate(algorithm = measure,
            category = 'units', mapping = mapping, block = [in_id])

        # store difference in knockout matrix
        for out_id, out_unit in enumerate(out_labels):
            R[in_id, out_id] = \
                knockout[out_unit] - default[out_unit]

    return R
