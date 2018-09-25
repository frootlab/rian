Install
=======

Nemoa requires Python 3.6 or later. If you do not already have a Python
environment configured on your computer, please see the instructions for
installing the full `scientific Python stack <https://scipy.org/install.html>`_.

.. note::
   If you are on Windows and want to install optional packages (e.g., `scipy`),
   then you will need to install a Python distribution such as
   `Anaconda <https://www.anaconda.com/download/>`_,
   `Enthought Canopy <https://www.enthought.com/product/canopy>`_,
   `Python(x,y) <http://python-xy.github.io/>`_,
   `WinPython <https://winpython.github.io/>`_, or
   `Pyzo <http://www.pyzo.org/>`_.
   If you use one of these Python distribution, please refer to their online
   documentation.

Below we assume you have the default Python environment already configured on
your computer and you intend to install ``nemoa`` inside of it.  If you want
to create and work with Python virtual environments, please follow instructions
on `venv <https://docs.python.org/3/library/venv.html>`_ and `virtual
environments <http://docs.python-guide.org/en/latest/dev/virtualenvs/>`_.

Install the development version
-------------------------------

If you have `Git <https://git-scm.com/>`_ installed on your system, it is also
possible to install the development version of ``nemoa``::

$ git clone https://github.com/fishroot/nemoa.git
$ cd nemoa
$ pip install -e .

The ``pip install -e .`` command allows you to follow the development branch as
it changes by creating links in the right places and installing the command
line scripts to the appropriate locations.

Then, if you want to update ``nemoa`` at any time, in the same directory do::

    $ git pull

Required packages
-----------------

.. note::
   Some required packages (e.g., `numpy`, `networkx`) may require compiling
   C or C++ code.  If you have difficulty installing these packages
   with `pip`, please review the instructions for installing
   the full `scientific Python stack <https://scipy.org/install.html>`_.

The following packages are reuired for nemoa.

- `NumPy <http://www.numpy.org/>`_ (>= 1.15.0)
- `Matplotlib <http://matplotlib.org/>`_ (>= 2.2.2)

Testing
-------

Nemoa uses the Python builtin package ``unittest`` for testing .

Test an installed package
^^^^^^^^^^^^^^^^^^^^^^^^^

If you have a file-based installation you can test the installed package with::

    nemoa -t

or::

    python -c "import nemoa; nemoa.test()"
