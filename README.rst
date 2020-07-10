=======
rngtest
=======

Randomness testing for humans

|travis| |codecov| |docs| |license| |version| |supported-versions| |black|

*rngtest* aims to implement the tests recommended by `NIST SP800-22
<https://csrc.nist.gov/publications/detail/sp/800-22/rev-1a/final>`_
to check random number generators for randomness.  A user-friendly command-line
interface provided allows you to ``load``, ``run`` and ``report`` on your data
in a step-by-step fashion.

``rngtest.randtests`` acts as the `public API
<https://rngtest.readthedocs.io/en/latest/reference/randtests/index.html>`_
for `notebook users <https://jupyter.org/index.html>`_ and developers to use
the randomness tests directly. The tests are implemented as general solutions,
and so accept basically any binary sequence you throw at them!

Note that *rngtest* is a temporary project name and `subject to change
<https://github.com/Honno/rngtest/issues/6>`_ :o

Setup
=====

Install Python 3.7+
-------------------

Cross-platform installation instructions for Python  are available at
`realpython.com/installing-python/ <https://realpython.com/installing-python/>`_.

Note ``rngtest`` only works on **Python 3.7 or above**. Make sure you have
Python 3.7 (or higher) by checking the version of your installation like so:

.. code-block:: console

    $ python --version
    Python 3.7.X

Install rngtest
---------------

You can install ``rngtest`` via the ``pip`` command like so:

.. code-block:: console

    $ pip install rngtest

`pip <https://realpython.com/what-is-pip/>`_ is the standard package manager for
Python, which should of installed automatically when installing Python 3.7+.

Quick start
===========

Try running the randomness tests on an example binary sequence.

.. code-block:: console

    $ rngtest example-run

Output should comprise of the example sequence, test-specific summaries, and a
final overall summary table.

Foo
===

(``0`` & ``1``, ``True`` & ``False``, ``"bob"`` & ``"alice"``)

Documentation
=============

https://rngtest.readthedocs.io/


Development
===========

Install from source
-------------------

Alternatively you can clone the source code via `Git
<https://www.freecodecamp.org/news/what-is-git-and-how-to-use-it-c341b049ae61/>`_
blah


Testing
-------

To run the all tests run::

    tox


.. |docs| image:: https://readthedocs.org/projects/rngtest/badge/?style=flat
    :target: https://readthedocs.org/projects/rngtest
    :alt: Documentation Status

.. |travis| image:: https://api.travis-ci.com/Honno/rngtest.svg?branch=master
    :alt: Travis-CI build status
    :target: https://travis-ci.com/Honno/rngtest

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/Honno/rngtest?branch=master&svg=true
    :alt: AppVeyor build status
    :target: https://ci.appveyor.com/project/Honno/rngtest

.. |requires| image:: https://requires.io/github/Honno/rngtest/requirements.svg?branch=master
    :alt: Requirements status
    :target: https://requires.io/github/Honno/rngtest/requirements/?branch=master

.. |codecov| image:: https://img.shields.io/codecov/c/gh/Honno/rngtest
    :alt: Coverage status
    :target: https://codecov.io/github/Honno/rngtest

.. |version| image:: https://img.shields.io/pypi/v/rngtest.svg
    :alt: PyPI package latest release
    :target: https://pypi.org/project/rngtest

.. |wheel| image:: https://img.shields.io/pypi/wheel/rngtest.svg
    :alt: PyPI wheel
    :target: https://pypi.org/project/rngtest

.. |supported-versions| image:: https://img.shields.io/badge/python-3.7%2B-informational
    :alt: Supported versions
    :target: https://pypi.org/project/rngtest

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/rngtest.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/rngtest

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :alt: Code style
    :target: https://github.com/psf/black

.. |license| image:: https://img.shields.io/badge/license-GPLv3-blueviolet
    :alt: License
    :target: https://choosealicense.com/licenses/gpl-3.0/
