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
.. |docs| image:: https://readthedocs.org/projects/rngtest/badge/?style=flat
    :target: https://readthedocs.org/projects/rngtest
    :alt: Documentation Status

.. |travis| image:: https://api.travis-ci.com/Honno/rngtest.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/Honno/rngtest

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/Honno/rngtest?branch=master&svg=true
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/Honno/rngtest

.. |requires| image:: https://requires.io/github/Honno/rngtest/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/Honno/rngtest/requirements/?branch=master

.. |codecov| image:: https://codecov.io/gh/Honno/rngtest/branch/master/graphs/badge.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/Honno/rngtest

.. |version| image:: https://img.shields.io/pypi/v/rngtest.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/rngtest

.. |wheel| image:: https://img.shields.io/pypi/wheel/rngtest.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/rngtest

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/rngtest.svg
    :alt: Supported versions
    :target: https://pypi.org/project/rngtest

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/rngtest.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/rngtest



.. end-badges

An example package. Generated with cookiecutter-pylibrary.

Installation
============

::

    pip install rngtest

You can also install the in-development version with::

    pip install https://github.com/Honno/rngtest/archive/master.zip


Documentation
=============


https://rngtest.readthedocs.io/


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
