<div align="center">
  <a href="https://github.com/frootlab/nemoa">
    <img src="https://bit.ly/2VRCy9t">
  </a>
  <br>
</div>

Nemoa
=====

[![Building Status](https://travis-ci.org/frootlab/nemoa.svg?branch=master)](https://travis-ci.org/frootlab/nemoa)
[![Documentation Status](https://readthedocs.org/projects/nemoa/badge/?version=latest)](https://nemoa.readthedocs.io/en/latest/?badge=latest)
[![PIP Version](https://badge.fury.io/py/nemoa.svg)](https://badge.fury.io/py/nemoa)

*Nemoa* is a machine learning- and data analysis framework, that implements the
**Cloud-Assisted Meta Programming** (CAMP) paradigm.

The key goal of Nemoa is to provide a long-term data analysis framework, which
seemingly integrates into existing enterprise data environments and thereby
supports collaborative data science. To achieve this goal Nemoa orchestrates
established Python frameworks like [TensorFlow®](https://www.tensorflow.org/)
and [SQLAlchemy](https://www.sqlalchemy.org/) and dynamically extends their
capabilities by community driven algorithms (e.g. for [probabilistic graphical
modeling](https://en.wikipedia.org/wiki/Graphical_model), [machine
learning](https://en.wikipedia.org/wiki/Machine_learning) and [structured
data-analysis](https://en.wikipedia.org/wiki/Structured_data_analysis_(statistics))).

Thereby Nemoa allows client-side implementations to use abstract **currently
best fitting** (CBF) algorithms. During runtime the concrete implementation of
CBF algorithms are chosen server-sided by category and metric. An example for
such a metric would be the average prediction accuracy within a fixed set of
gold standard samples of the respective domain of application (e.g. latin
handwriting samples, spoken word samples, TCGA gene expression data, etc.).

Nemoa is [open source](https://github.com/frootlab/pandora), based on the
[Python](https://www.python.org/) programming language and actively developed as
part of the [Liquid ML](https://github.com/orgs/frootlab/projects) framework
at [Frootlab](https://github.com/frootlab).

Current Development Status
--------------------------

Nemoa currently is in *Pre-Alpha* development stage, which immediately follows
the *Planning* stage. This means, that at least some essential requirements of
Nemoa are not yet implemented.

Installation
------------

Comprehensive information and installation support is provided within the
[online manual](http://docs.frootlab.org/nemoa). If you already have a
Python environment configured on your computer, you can install the latest
distributed version by using pip:

    $ pip install nemoa

Documentation
-------------

The documentation of the latest distributed version is available as an [online
manual](http://docs.frootlab.org/nemoa) and for download, given in the
formats [PDF](https://readthedocs.org/projects/nemoa/downloads/pdf/latest/),
[EPUB](https://readthedocs.org/projects/nemoa/downloads/epub/latest/) and
[HTML](https://readthedocs.org/projects/nemoa/downloads/htmlzip/latest/).

Contribute
----------

Contributors are very welcome! Feel free to report bugs and feature requests to
the [issue tracker](https://github.com/frootlab/nemoa/issues) provided by
GitHub. Currently, as the Frootlab Developers team still is growing, we do not
provide any Contribution Guide Lines to collaboration partners. However, if you
are interested to join the team, we would be glad, to receive an informal
[application](mailto:application@frootlab.org).

License
-------

Nemoa is [open source](https://github.com/frootlab/pandora) and available free
for any use under the [GPLv3 license](https://www.gnu.org/licenses/gpl.html):

    © 2019 Frootlab Developers:
      Patrick Michl <patrick.michl@frootlab.org>
    © 2013-2019 Patrick Michl
