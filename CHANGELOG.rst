=========
Changelog
=========

0.1.5 (2020-12-08)
------------------

* ``coinflip.collections.defaultlist`` improvements:
    * `index()` and `remove()` uses the `__iter__()` method.
    * Setter for the `default_factory` property.
    * Returns a `defaultlist` on slice get operations.


0.1.4 (2020-11-28)
------------------

* Slicing support for accessor methods in ``coinflip.collections.defaultlist``.
* Fixed bug causing inaccurate results for the *Non-overlapping Template Matching* test.
* ``Bins`` and ``FloorDict`` containers in ``coinflip.collections`` are now always ordered.

0.1.3 (2020-11-19)
------------------

* Fixed wrong intervals being rounded to in ``coinflip.collections.bins``.


0.1.2 (2020-11-18)
------------------

* ``coinflip.collections.bins`` now uses ``OrderedDict`` under the hood.


0.1.1 (2020-11-16)
------------------

* Reference implementation available in ``coinflip.randtests_refimpl`` (requires the `refimpl` extra).
* Docstrings for all the randomness tests in ``coinflip.randtests``.


0.1.0 (2020-11-09)
------------------

* First beta release on PyPI.
