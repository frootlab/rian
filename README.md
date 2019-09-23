<div align="center">
  <figure>
    <img src="https://www.frootlab.org/images/fig/rian.svg" width=350px
      alt="Machine Learning using Vivid Node">
  </figure>
</div>

Vivid Node
==========

[![Building Status](https://travis-ci.org/frootlab/rian.svg?branch=master)](https://travis-ci.org/frootlab/rian)
[![Documentation Status](https://readthedocs.org/projects/rian/badge/?version=latest)](https://rian.readthedocs.io/en/latest/?badge=latest)
[![PIP Version](https://badge.fury.io/py/rian.svg)](https://badge.fury.io/py/rian)

*Vivid Node* (alias *Rian*) is a free [Python](https://www.python.org/) library
for next generation machine learning- and data analysis applications, that
implement *cloud-assisted meta programming*. Rian is part of the
[Vivid Code](http://www.frootlab.org/vivid) framework and actively developed at
the [Frootlab](http://www.frootlab.org) Organization.

The key goal of Rian is to automate and support collaborative data science. To
achieve this goal Rian orchestrates established frameworks like
[TensorFlow®](https://www.tensorflow.org) or [Keras®](https://keras.io) and
dynamically extends their capabilities by cloud based community algorithms.
Thereby Rian allows the usage of abstract defined algorithms, that are specified
with respect to their category, the used data type and an evaluation metric.
During runtime these abstract specifications are resolved cloud-sided by
*currently best fitting* algorithm, that match the specification. This allows
the separation of engineering and data science, as well as simple collaborations
between organizations without the requirement to share data.

<div align="center">
  <figure>
    <img src="https://www.frootlab.org/images/fig/vivid-collaboration.svg"
      width=400px alt="Collaborative data science using the Vivid Code framework">
    <br>
    <figcaption>
      Collaborative data science using the Vivid Code framework
    </figcaption>
  </figure>
</div>

For a given algorithm category and data type, the currently best fitting
algorithms are determined by the used metric. Examples for such metrices would
be the prediction accuracies within a fixed set of gold standard samples of the
respective domain of application (e.g. latin handwriting, spoken words, TCGA
gene expression data, etc.).

Current Development Status
--------------------------

Rian currently is in *Pre-Alpha* development stage, which immediately follows
the *Planning* stage. This means, that at least some essential requirements of
Rian are not yet implemented.

Installation
------------

Comprehensive information and installation support is provided within the
[online manual](http://docs.frootlab.org/rian). If you already have a
Python environment configured on your computer, you can install the latest
distributed version by using pip:

    $ pip install rian

Or alternatively:

    $ pip install vivid-node

Documentation
-------------

The documentation of the latest distributed version is available as an [online
manual](http://docs.frootlab.org/rian) and for download, given in the
formats [PDF](https://readthedocs.org/projects/rian/downloads/pdf/latest/),
[EPUB](https://readthedocs.org/projects/rian/downloads/epub/latest/) and
[HTML](https://readthedocs.org/projects/rian/downloads/htmlzip/latest/).

Contribution
------------

Contributors are very welcome! Feel free to report bugs, ideas and feature
requests to the [issue tracker](https://github.com/frootlab/rian/issues),
provided by GitHub. Currently, as our team still is growing, we do not provide
any Contribution Guide Lines. So, if you are interested to help or to join the
team, we would be glad, to [hear about you](mailto:application@frootlab.org).

License
-------

Rian is open source software and available free for any use under the
[GPLv3 license](https://www.gnu.org/licenses/gpl.html):

    © 2019 The Frootlab Organization
    © 2013-2019 Patrick Michl
