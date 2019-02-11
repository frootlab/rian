Install
=======

Nemoa requires Python 3.7 or later. If you do not already have a Python
environment configured on your computer, please see the instructions for
installing the full `scientific Python stack <https://scipy.org/install.html>`_.

.. note::
   If you are using the Windows platform and want to install optional packages
   (e.g., `scipy`), then it may be useful to install a Python distribution such
   as:
   `Anaconda <https://www.anaconda.com/download/>`_,
   `Enthought Canopy <https://www.enthought.com/product/canopy>`_,
   `Python(x,y) <http://python-xy.github.io/>`_,
   `WinPython <https://winpython.github.io/>`_, or
   `Pyzo <http://www.pyzo.org/>`_.
   If you already use one of these Python distributions, please refer to their
   online documentation.

Below it is assumed, that you have the default Python environment configured on
your computer and you intend to install nemoa inside of it.  If you want
to create and work with Python virtual environments, please follow instructions
on `venv <https://docs.python.org/3/library/venv.html>`_ and `virtual
environments <http://docs.python-guide.org/en/latest/dev/virtualenvs/>`_.

Install the latest distributed package
--------------------------------------

You can install the latest distributed package of nemoa by using `pip`::

    $ pip install nemoa

Install the development branch
------------------------------

The installation requires that you have `Git <https://git-scm.com/>`_ installed
on your system. Under this prerequisite the first step is to clone the github
repository of `nemoa`::

    $ git clone https://github.com/frootlab/nemoa.git

Thereupon the development branch can locally be installed by using `pip`::

    $ cd nemoa
    $ pip install -e .

The ``pip install`` command allows you to follow the development branch as
it changes by creating links in the right places and installing the command
line scripts to the appropriate locations.

Update the nemoa development branch
-----------------------------------

Once you have cloned the `nemoa` GitHub repository onto a local directory, you
can update it anytime by running a ``git pull`` in this directory::

    $ git pull

Required packages
-----------------

.. note::
   Some required packages (e.g., `numpy`) may require compiling C or C++ code.
   If you have difficulty installing these packages with `pip`, it is
   highly recommended to review the instructions for installing the full
   `scientific Python stack <https://scipy.org/install.html>`_.

By using the ``pip install`` the required packages should by installed
automatically. These packages include::

- `numpy <https://www.numpy.org/>`_ (>= 1.15.0)
- `NetworkX <https://networkx.github.io/>`_ (>= 2.1)
- `Matplotlib <https://matplotlib.org/>`_ (>= 2.2.2)
- `AppDirs <https://github.com/ActiveState/appdirs>`_ (>= 1.1.0)

Testing your installation
-------------------------

Nemoa uses the Python builtin package unittest for testing. Since the tests are
not included in the distributed package you are required to install the nemoa
development branch. Thereupon you have to switch to repository directory and
run::

    $ python3 tests
