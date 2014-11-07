import numpy as np
import sys, fileinput, os
import csv

def hill(x): return 1.0 / (1.0 + np.exp(-x))

def main(workspace, **kwargs):

    # data definition
    iNodes  = 4
    oNodes  = 2
    samples = 1000
    path    = '/home/rebecca/nemoa.workspaces/tutorial/data/'
    name    = 'tutorial4b'
    label   = 'nm'
    sdev    = 1.0

    # create binomial data
    bernoulli = np.random.randint(2, size = (samples, iNodes + oNodes)) - 0.5
    gauss = np.random.normal(0, sdev, size = (samples, iNodes + oNodes))

    data = bernoulli + gauss

    # for easy indexing
    i = [None] + range(iNodes)
    o = [None] + [iNodes + k for k in range(oNodes)]

    # manipulate data
    #data[:, i[2]] = data[:, i[1]]
    #data[:, i[3]] = data[:, i[4]]
    h1 = hill(0.5 * data[:, i[1]] - 0.5 * data[:, i[2]]) + 0.5 * data[:, o[1]]
    h2 = hill(0.5 * data[:, i[3]] - 0.5 * data[:, i[4]]) + 0.5 * data[:, o[2]]
    
    data[:, o[1]] = hill(0.5 * h1 + 0.5 * h2)
    data[:, o[2]] = hill(0.5 * h1 - 0.5 * h2)

    # add gaussian noise
    # data = data + gauss

    # normalize data (gauss)
    for i in range(data.shape[1]):
        (data[:, i] - np.mean(data[:, i])) / np.std(data[:, i])

    # create column labels
    colLabels = ['label'] \
        + ['i%i' % (n + 1) for n in range(iNodes)] \
        + ['o%i' % (n + 1) for n in range(oNodes)]

    # write file
    file = '%s%s.tab' % (path, name)
    with open(file, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter = '\t')
        writer.writerow(colLabels)
        for i in range(data.shape[0]):
            dataRow = ['%s-%i' % (label, i + 1)] + data[i,:].tolist()
            writer.writerow(dataRow)

    ## create column labels
    #colLabels = ['s%i' % (n + 1) for n in range(iNodes)] \
        #+ ['e%i' % (n + 1) for n in range(oNodes)]

    ## also write no label file (for other applications)
    #file = './%s-nolabel.tab' % (name)
    #with open(file, 'wb') as csvfile:
        #writer = csv.writer(csvfile, delimiter = '\t')
        #writer.writerow(colLabels)
        #for i in range(data.shape[0]):
            #writer.writerow(data[i,:].tolist())
