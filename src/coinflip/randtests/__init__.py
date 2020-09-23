"""Statistical tests for randomness

This subpackage comprises of implementations of statistical tests laid out in a
comprehensive paper from NIST [1]_ in regards to assessing (pseudo-)random number
generators.

Notes
-----
A copy of the NIST paper can be found at the root of the ``coinflip`` repository as
`SP800-22.pdf <https://github.com/Honno/coinflip/blob/master/SP800-22.pdf>`_.

The test themselves are defined in section 2., "Random Number Generation Tests",
p. 23-62. Further detail of the tests are provided in section 3. "Technical
Descriptions of Tests", p. 63-87.

These tests were implemented in a complimentary program ``sts``, which can be
downloaded from the `NIST website
<https://csrc.nist.gov/projects/random-bit-generation/documentation-and-software>`_.

Note that the paper assumes a great amount of familiarity with certain
concepts in statistics. It also uses some constants and algorithms without any
explaination. Part of the purpose for ``coinflip`` is to "describe" the NIST tests
more wholly than in the paper itself, whilst also reducing the noise of some
non-idiomatic programming conventions used in ``sts``.

.. [1] National Institute of Standards and Technology <Andrew Rukhin, Juan Soto,
   James Nechvatal, Miles Smid, Elaine Barker, Stefan Leigh, Mark Levenson, Mark
   Vangel, David Banks, Alan Heckert, James Dray, San Vo,
   Lawrence E Bassham II>, "A Statistical Test Suite for Random and Pseudorandom
   Number Generators for Cryptographic Applications", *Special Publication
   800-22 Revision 1a*, April 2010.


.. autofunction:: coinflip.randtests.monobit(sequence)
.. autofunction:: coinflip.randtests.frequency_within_block(sequence, candidate=None, blocksize=8)
.. autofunction:: coinflip.randtests.runs(sequence, candidate=None)
.. autofunction:: coinflip.randtests.longest_runs(sequence, candidate=None)
.. autofunction:: coinflip.randtests.binary_matrix_rank(sequence, candidate=None, matrix_dimen: Tuple[int, int] = None)
.. autofunction:: coinflip.randtests.spectral(sequence, candidate=None)
.. autofunction:: coinflip.randtests.non_overlapping_template_matching(sequence, template: List = None, nblocks=None)
.. autofunction:: coinflip.randtests.overlapping_template_matching(sequence, template: List = None, nblocks=None, df=5)
.. autofunction:: coinflip.randtests.maurers_universal(sequence, blocksize=None, init_nblocks=None)
"""
from coinflip.randtests.entropy import approximate_entropy
from coinflip.randtests.fourier import spectral
from coinflip.randtests.frequency import frequency_within_block
from coinflip.randtests.frequency import monobit
from coinflip.randtests.matrix import binary_matrix_rank
from coinflip.randtests.runs import longest_runs
from coinflip.randtests.runs import runs
from coinflip.randtests.template import non_overlapping_template_matching
from coinflip.randtests.template import overlapping_template_matching
from coinflip.randtests.universal import maurers_universal

__all__ = [
    "monobit",
    "frequency_within_block",
    "runs",
    "longest_runs",
    "binary_matrix_rank",
    "spectral",
    "non_overlapping_template_matching",
    "overlapping_template_matching",
    "maurers_universal",
    "approximate_entropy",
]
