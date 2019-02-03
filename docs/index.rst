Nemoa
=====

Nemoa is an open source data analysis framework for enterprise and scientific
application and based on the `Python`_ programming language.

Introduction
------------

In many domains of enterprise and scientific data analysis the lack of strong
structural beliefs encourages the use of machine intelligence to gather
information or even to draw decisions. Although such approaches surpass the
structural flexibility of classical statistical methods, they are generally paid
by a high mathematical uncertainty. This makes it indispensable to choose and
adapt the statistical model as closely as possible to the underlying problem.

.. image:: images/model.png
   :width: 300
   :align: center
   :alt: Nemoa Deep Belief Model

The key goal of nemoa is to provide a long-term data analysis framework, which
seemingly integrates into existing data systems and thereby offers state of the
art machine intelligence. To achieve this goal nemoa orchestrates established
frameworks like `TensorFlow`_ and `SQLAlchemy`_ and dynamically extends their
capabilities by community driven algorithms for probabilistic graphical
modeling [PGM]_, machine learning [ML]_ and structured data-analysis [SDA]_.

Components
----------

Nemoa provides:

    * A transparent `EDW`_ architecture for the seamless integration of existing
        SQL databases, flat data from laboratory measurement devices and data
        generators.
    * A versatile and fast date modeling and data analysis framework.

.. References:
.. _Python: https://www.python.org/
.. _EDW: https://en.wikipedia.org/wiki/Data_warehouse
.. _SQLAlchemy: https://www.sqlalchemy.org/
.. _TensorFlow: https://www.tensorflow.org/

.. toctree::
   :maxdepth: 3
   :caption: Contents:

   Installation <install>
   Reference <source/modules>
   Glossary <glossary>
   License <license>
   Bibliography <bibliography>

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
