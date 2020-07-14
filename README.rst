=======
rngtest
=======

Randomness testing for humans

|travis| |codecov| |docs| |license| |version| |supported-versions| |hypothesis| |black|

*rngtest* aims to implement the tests recommended by `NIST SP800-22
<https://csrc.nist.gov/publications/detail/sp/800-22/rev-1a/final>`_
to check random number generators for randomness.  A user-friendly command-line
interface provided allows you to ``load``, ``run`` and ``report`` on your data
in a step-by-step fashion.

``rngtest.randtests`` acts as the `public API
<https://rngtest.readthedocs.io/en/latest/reference/randtests/index.html>`_
for `notebook users <https://jupyter.org/index.html>`_ and developers to use
the randomness tests directly. The tests are implemented as general solutions,
meaning they accept basically any binary sequence you throw at them!

Note that *rngtest* is a temporary project name that is `subject to change
<https://github.com/Honno/rngtest/issues/6>`_ :o

Setup
=====

*rngtest* is currently in rapid development, so we recommend building from
source.

.. code-block:: console

    $ pip install git+https://github.com/Honno/rngtest

If that means nothing to you, no fret! Please continue reading the instructions
below.

Install Python 3.7+
-------------------

Cross-platform installation instructions for Python  are available at
`realpython.com/installing-python/ <https://realpython.com/installing-python/>`_.

Note ``rngtest`` only works on **Python 3.7 or above**. Make sure you have
Python 3.7 (or higher) by checking the version of your installation:

.. code-block:: console

    $ python --version
    Python 3.7.X

Clone repository
----------------

You can clone the source code via `Git
<https://www.freecodecamp.org/news/what-is-git-and-how-to-use-it-c341b049ae61/>`_:

.. code-block:: console

    $ git clone https://github.com/Honno/rngtest


Install rngtest
---------------

Enter the directory *rngtest* is downloaded to:

.. code-block:: console

   $ cd rngtest

You can install *rngtest* via the ``pip`` module:

.. code-block:: console

    $ pip install -e .

`pip <https://realpython.com/what-is-pip/>`_ is the standard package manager for
Python, which should of installed automatically when installing Python 3.7+.

Trial run
---------

Try running the randomness tests on a generated binary sequence:

.. code-block:: console

    $ rngtest example-run

If the command ``rngtest`` is "not found", you may need to add your local
binaries folder to your shell's path. For example, in bash you would do the
following:

.. code-block:: console

    $ echo "export PATH=~/.local/bin:$PATH" >> ~/.bash_profile
    $ source ~/.bash_profile

In the worst case, you can execute commands via ``python -m``:

.. code-block:: console

    $ python -m rngtest example-run


Quick start
===========

Output of random number generators can be parsed and serialised into a
test-ready format via the ``load`` command:

.. code-block:: console

    $ rngtest load DATA
    Store name to be encoded as store_<timestamp>
    Data stored successfully!
    ...

``DATA`` is the path to newline-delimited text file that contains a binary
sequence. An example file to use is available on `my gist
<https://gist.github.com/Honno/dd6f3527e588428fa17a999042e3c6e8>`_.

Randomness tests can then be ran over the store’s data via the ``run`` command.
You should be prompted by a "No STORE argument provided" message, where
``rngtest`` will assume you want to run the tests over the data you just
loaded—type ``y`` and hit enter.

.. code-block:: console

    $ rngtest run
    No STORE argument provided
      The most recent STORE to be initialised is 'store_<timestamp>'
      Pass it as the STORE argument? [y/N]: y
    ...

Output should comprise of the example sequence, test-specific summaries, and a
final overall summary table.

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

.. |hypothesis| image:: https://img.shields.io/badge/hypothesis-tested-brightgreen.svg
   :alt: Tested with Hypothesis
   :target: https://hypothesis.readthedocs.io

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
