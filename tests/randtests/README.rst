============================
Testing the Randomness Tests
============================

NIST examples
=============

The  `SP800-22 <https://github.com/Honno/rngtest/blob/master/SP800-22.pdf>`_
authors included worked examples for their recommend randomness tests, which
have been curated in ``examples.py`` as  heterogeneous dictionary tree. They are
conveniently exposed through the ``examples_iter`` method.

Methods named ``test_randtest_on_example`` are passed the examples automatically
when running these tests via ``pytest`` due to ``conftest.py`` `configuration
<https://docs.pytest.org/en/stable/example/parametrize.html>`_. The optional
flag ``--example <regex>`` filters the test names via a `regular expression
<https://regexone.com/>`_.

``test_examples.py`` contains such a method to pass the parameters of the NIST
examples to our own `randomness tests
<https://rngtest.readthedocs.io/en/latest/reference/randtests/index.html>`_,
and assert whether our results match theirs.


Comparing implementations
=========================

Other implementations of randomness tests are kept in the ``implementations/``
folder, along with modules that adapt said implementations to be accessed the
same way as our `API
<https://rngtest.readthedocs.io/en/latest/reference/randtests/index.html>`_.

The adaptor methods raise an ``ImplementationError`` when a known error is
raised from the original method. They are also specified of any missing and
fixed keyword arguments through the ``Implementation`` named tuple, as defined
in ``implementations/_implementation.py``.

A map of the randomn test names to the adaptor's corresponding
``Implementation`` provides a ``testmap``, which is then used in
``test_comparisons.py`` to run the adapted implementations in conjunction with
our own.

We to `generate paramters
<https://hypothesis.readthedocs.io/en/latest/quickstart.html#writing-tests>`_
to randomness tests, pass them to the implementations and our own, and see if
the results are in the same ballpark.
