============================
Testing the Randomness Tests
============================

NIST examples
=============

The  `SP800-22 <https://github.com/Honno/coinflip/blob/master/SP800-22.pdf>`_
authors included worked examples for their recommend randomness tests, which
have been curated in ``test_examples.py``.

``test_examples.py`` contains a parametrized method to run the NIST examples on
our own `randomness tests
<https://coinflip.readthedocs.io/en/latest/reference/randtests/index.html>`_,
and assert whether our results match theirs.

Comparing implementations
=========================

Other implementations of randomness tests are kept in the ``implementations/``
folder, along with modules that adapt said implementations to be accessed the
same way as our `API
<https://coinflip.readthedocs.io/en/latest/reference/randtests/index.html>`_.

The adaptor methods raise an ``ImplementationError`` when a known error is
raised from the original method. They are also specified of any missing and
fixed keyword arguments through the ``Implementation`` named tuple, as defined
in ``impls/core.py``.

A map of the randomn test names to the adaptor's corresponding
``Implementation`` provides a ``testmap``, which is then used in
``test_comparisons.py`` to run the adapted implementations in conjunction with
our own.

We to `generate paramters
<https://hypothesis.readthedocs.io/en/latest/quickstart.html#writing-tests>`_
to randomness tests, pass them to the implementations and our own, and see if
the results are in the same ballpark.

We can also test the same NIST examples on the implementations through
``impls/test_impls.py``, which also helps contextualise our
own randomness tests.
