.. raw:: html

   <div align="center">
     <a href="https://github.com/frootlab/nemoa">
       <img src="https://bit.ly/2VHbyJI">
     </a>
     <br>
   </div>

----------

Nemoa
=====

.. image:: https://travis-ci.org/frootlab/nemoa.svg?branch=master
    :target: https://travis-ci.org/frootlab/nemoa
    :alt: Building Status

.. image:: https://readthedocs.org/projects/nemoa/badge/?version=latest
    :target: https://nemoa.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://badge.fury.io/py/nemoa.svg
    :target: https://badge.fury.io/py/nemoa
    :alt: PIP Version

*Nemoa* is a machine learning- and data analysis framework, that implements the
**Cloud-Assisted Meta Programming** (CAMP) paradigm.

The key goal of Nemoa is to provide a long-term data analysis framework, which
seemingly integrates into existing enterprise data environments and thereby
supports collaborative data science. To achieve this goal Nemoa orchestrates
established Python frameworks like `TensorFlow®`_ and `SQLAlchemy`_ and
dynamically extends their capabilities by community driven algorithms (e.g. for
`probabilistic graphical modeling`_, `machine learning`_ and `structured
data-analysis`_).

Thereby Nemoa allows client-side implementations to use abstract **currently
best fitting** (CBF) algorithms. During runtime the concrete implementation of
CBF algorithms are chosen server-sided by category and metric. An example for
such a metric would be the average prediction accuracy within a fixed set of
gold standard samples of the respective domain of application (e.g. latin
handwriting samples, spoken word samples, TCGA gene expression data, etc.).

Nemoa is `open source`_, based on the `Python`_ programming language and
actively developed as part of `Project Infimum`_ at `Frootlab`_.

Current Development Status
--------------------------

Nemoa currently is in *Pre-Alpha* development stage, which immediately follows
the *Planning* stage. This means, that at least some essential requirements of
Nemoa are not yet implemented.

Installation
------------

Comprehensive information and installation support is provided within the
`online manual`_. If you already have a Python environment configured on your
computer, you can install the latest distributed version by using pip::

    $ pip install nemoa

Documentation
-------------

The latest Nemoa documentation is available as an `online manual`_ and for
download in the formats `PDF`_, `Epub`_ and `HTML`_.

Contribute
----------

Contributors are very welcome! Feel free to report bugs and feature requests to
the `issue tracker`_ provided by GitHub. Currently, as the Frootlab Developers
team still is growing, we do not provide any Contribution Guide Lines to
collaboration partners. However, if you are interested to join the team, we
would be glad, to receive an informal `application`_.

License
-------

Nemoa is `open source`_ and available free for any use under the `GPLv3
license`_::

   © 2019 Frootlab Developers
     Patrick Michl <patrick.michl@gmail.com>
   © 2013-2019 Patrick Michl

.. _Python: https://www.python.org/
.. _TensorFlow®: https://www.tensorflow.org/
.. _SQLAlchemy: https://www.sqlalchemy.org/
.. _PyPI: https://pypi.org/project/pandb/
.. _GPLv3 license: https://www.gnu.org/licenses/gpl.html
.. _Installation Manual: https://nemoa.readthedocs.io/en/latest/install.html
.. _online manual: https://nemoa.readthedocs.io/en/latest/
.. _PDF: https://readthedocs.org/projects/nemoa/downloads/pdf/latest/
.. _Epub: https://readthedocs.org/projects/nemoa/downloads/epub/latest/
.. _HTML: https://readthedocs.org/projects/nemoa/downloads/htmlzip/latest/
.. _issue tracker: https://github.com/frootlab/nemoa/issues
.. _Frootlab: https://github.com/frootlab
.. _probabilistic graphical modeling:
    https://en.wikipedia.org/wiki/Graphical_model
.. _machine learning: https://en.wikipedia.org/wiki/Machine_learning
.. _structured data-analysis:
    https://en.wikipedia.org/wiki/Structured_data_analysis_(statistics)
.. _GPLv3 license: https://www.gnu.org/licenses/gpl.html
.. _issue tracker: https://github.com/frootlab/nemoa/issues
.. _google group: http://groups.google.com/group/nemoa
.. _Project Infimum: https://github.com/orgs/frootlab/projects
.. _open source: https://github.com/frootlab/pandora
.. _application: patrick.michl@gmail.com
