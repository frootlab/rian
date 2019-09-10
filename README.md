<div align="center">
  <img src="https://www.frootlab.org/images/fig/rian.svg" width=350px>
</div>

Rian
=====

[![Building Status](https://travis-ci.org/frootlab/rian.svg?branch=master)](https://travis-ci.org/frootlab/rian)
[![Documentation Status](https://readthedocs.org/projects/rian/badge/?version=latest)](https://rian.readthedocs.io/en/latest/?badge=latest)
[![PIP Version](https://badge.fury.io/py/rian.svg)](https://badge.fury.io/py/rian)

*Rian* is a machine learning- and data analysis framework, that implements *cloud-assisted meta programming* (CAMP).

The key goal of Rian is to provide a long-term data analysis framework, which
seemingly integrates into existing enterprise data environments and thereby
supports collaborative data science. To achieve this goal Rian orchestrates
established frameworks like [TensorFlow®](https://www.tensorflow.org/) and
dynamically extends their capabilities by community driven algorithms (e.g. for
[probabilistic graphical
modeling](https://en.wikipedia.org/wiki/Graphical_model), [machine
learning](https://en.wikipedia.org/wiki/Machine_learning) and [structured
data-analysis](https://en.wikipedia.org/wiki/Structured_data_analysis_(statistics))).

Thereby Rian allows the client-side usage of abstract algorithms,
that are specified with respect to their category, the used data type and an
evaluation metric that determines their fitness. During runtime
these abstract specifications are resolved server-sided from a code catalog, by
a *currently best fitting* (CBF) algorithm.

For given category and application, the CBF algorithms are determined by their
used metric. Examples for such metrices would be the prediction accuracies
within a fixed set of gold standard samples of the respective domain of
application (e.g. latin handwriting, spoken words, TCGA gene expression data,
etc.).

Rian is open source, based on the [Python](https://www.python.org/) programming
language and actively developed as part of the
[Vivid Code](https://www.frootlab.org/vivid) framework at
[Frootlab](https://www.frootlab.org).

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

Documentation
-------------

The documentation of the latest distributed version is available as an [online
manual](http://docs.frootlab.org/rian) and for download, given in the
formats [PDF](https://readthedocs.org/projects/rian/downloads/pdf/latest/),
[EPUB](https://readthedocs.org/projects/rian/downloads/epub/latest/) and
[HTML](https://readthedocs.org/projects/rian/downloads/htmlzip/latest/).

Contributions
-------------

Contributors are very welcome! Feel free to report bugs, ideas and feature
requests to the [issue tracker](https://github.com/frootlab/rian/issues),
provided by GitHub. Currently, as our team still is growing, we do not provide
any Contribution Guide Lines. So, if you are interested to help or to join the
team, we would be glad, to [hear about you](mailto:application@frootlab.org).

License
-------

Rian is open source software and available free for any use under the
[GPLv3 license](https://www.gnu.org/licenses/gpl.html):

    © 2019 Frootlab Developers:
      Patrick Michl <patrick.michl@frootlab.org>
    © 2013-2019 Patrick Michl
