========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |appveyor| |requires|
        | |codecov|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|
.. |docs| image:: https://readthedocs.org/projects/prng/badge/?style=flat
    :target: https://readthedocs.org/projects/prng
    :alt: Documentation Status

.. |travis| image:: https://api.travis-ci.com/Honno/prng.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/Honno/prng

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/Honno/prng?branch=master&svg=true
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/Honno/prng

.. |requires| image:: https://requires.io/github/Honno/prng/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/Honno/prng/requirements/?branch=master

.. |codecov| image:: https://codecov.io/gh/Honno/prng/branch/master/graphs/badge.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/Honno/prng

.. |version| image:: https://img.shields.io/pypi/v/prng.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/prng

.. |wheel| image:: https://img.shields.io/pypi/wheel/prng.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/prng

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/prng.svg
    :alt: Supported versions
    :target: https://pypi.org/project/prng

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/prng.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/prng


.. end-badges

An example package. Generated with cookiecutter-pylibrary.

Installation
============

::

    pip install prng

You can also install the in-development version with::

    pip install https://github.com/Honno/prng/archive/master.zip


Documentation
=============


https://prng.readthedocs.io/


Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
