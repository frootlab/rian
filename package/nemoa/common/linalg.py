#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy, numpy.linalg

def pcaRedimData(data, dims = 2):
    mean = numpy.mean(data, axis = 0)
    # mean center the data
    data -= mean
    # calculate the covariance matrix
    cov = numpy.cov(data.T)
    # calculate eigenvectors & eigenvalues of the covariance matrix
    eigVals, eigVecs = numpy.linalg.eig(cov)
    # sorted them by eigenvalue in decreasing order
    idx = numpy.argsort(eigVals)[::-1]
    eigVecs = eigVecs[:, idx]
    eigVals = eigVals[idx]
    # select the first n eigenvectors (n is desired dimension
    # of rescaled data array, or dims)
    eigVecs = eigVecs[:, :dims]
    # carry out the transformation on the data using eigenvectors
    return numpy.dot(eigVecs.T, data.T).T
    # reconstruct original data array
    #data_original_regen = numpy.dot(eigVecs, dim1).T + mean
    #return data_rescaled, data_original_regen
