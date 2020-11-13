========
coinflip
========

Randomness testing for humans

|docs| |license| |version| |supported-versions| |hypothesis| |black|

*coinflip* aims to implement the tests recommended by `NIST SP800-22
<https://csrc.nist.gov/publications/detail/sp/800-22/rev-1a/final>`_
to check random number generators for randomness.  A user-friendly command-line
interface provided allows you to ``run`` the tests on your data, and
subsequently ``report`` on the results by generating informational HTML
documents.

``coinflip.randtests`` acts as the `public API
<https://coinflip.readthedocs.io/en/latest/reference/randtests/index.html>`_
for `notebook users <https://jupyter.org/index.html>`_ and developers to use
the randomness tests directly. The tests are implemented as general solutions,
meaning they accept basically any sequence with two distinct elements!

.. image:: https://raw.githubusercontent.com/Honno/coinflip/report/.video_files/thumb/thumb_thumb.png
   :target: http://www.youtube.com/watch?v=0xrWG3Ki9Z8

Setup
=====

You can get the latest release of coinflip from PyPI.

.. code-block:: console

    $ pip install coinflip

Alternatively you can get the (unstable) development version straight from
GitHub.

.. code-block:: console

    $ pip install git+https://github.com/Honno/coinflip

If that means nothing to you, no fret! Please continue reading the instructions
below.

Install Python 3.7+
-------------------

Cross-platform installation instructions for Python  are available at
`realpython.com/installing-python/ <https://realpython.com/installing-python/>`_.

Note ``coinflip`` only works on **Python 3.7 or above**. Make sure you have
Python 3.7 (or higher) by checking the version of your installation:

.. code-block:: console

    $ python --version
    Python 3.7.X

Clone repository
----------------

You can clone the source code via `Git
<https://www.freecodecamp.org/news/what-is-git-and-how-to-use-it-c341b049ae61/>`_:

.. code-block:: console

    $ git clone https://github.com/Honno/coinflip


Install coinflip
----------------

Enter the directory *coinflip* is downloaded to:

.. code-block:: console

   $ cd coinflip

You can install *coinflip* via the ``pip`` module:

.. code-block:: console

    $ pip install -e .

`pip <https://realpython.com/what-is-pip/>`_ is the standard package manager for
Python, which should of installed automatically when installing Python 3.7+.

Trial run
---------

Try running the randomness tests on an automatically generated binary sequence:

.. code-block:: console

    $ coinflip example-run

If the command ``coinflip`` is "not found", you may need to add your local
binaries folder to your shell's path. For example, in bash you would do the
following:

.. code-block:: console

    $ echo "export PATH=~/.local/bin:$PATH" >> ~/.bash_profile
    $ source ~/.bash_profile

In the worst case, you can execute commands via ``python -m``:

.. code-block:: console

    $ python -m coinflip example-run


Quick start
===========

Randomness tests can be ran over your RNG output via the ``run`` command.

.. code-block:: console

    $ coinflip run DATA OUT
    ...

``DATA`` is the path to newline-delimited text file that contains a binary
sequence. An example file to use is available on `my gist
<https://gist.github.com/Honno/dd6f3527e588428fa17a999042e3c6e8>`_.
Alternatively, raw binary files can be read as bitstreams via the ``--binary``
flag

``OUT`` is the path where you want the results to be saved. The results will be
saved as a `pickle <https://docs.python.org/3/library/pickle.html>`_-serialised
file, which can be viewed again via the ``read`` command. Additionally you can
generate informational HTML reports from the results via the ``report`` command,
but note that the reports are currently very lacking.

Output should comprise of the sequence parsed from ``DATA``, test-specific result
summaries, and a final overall summary table.

.. |docs| image:: https://readthedocs.org/projects/coinflip/badge/?style=flat
    :target: https://readthedocs.org/projects/coinflip
    :alt: Documentation Status

.. |hypothesis| image:: https://img.shields.io/badge/hypothesis-tested-brightgreen.svg
   :alt: Tested with Hypothesis
   :target: https://hypothesis.readthedocs.io

.. |version| image:: https://img.shields.io/pypi/v/coinflip.svg
    :alt: PyPI package latest release
    :target: https://pypi.org/project/coinflip

.. |supported-versions| image:: https://img.shields.io/badge/python-3.7%2B-informational
    :alt: Supported versions
    :target: https://pypi.org/project/coinflip

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/coinflip.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/coinflip

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :alt: Code style
    :target: https://github.com/psf/black

.. |license| image:: https://img.shields.io/badge/license-BSD-blueviolet
    :alt: License
    :target: https://github.com/Honno/coinflip/blob/master/LICENSE.md
