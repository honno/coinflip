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
"""

from typing import Tuple

from coinflip import _randtests

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
    "linear_complexity",
    "serial",
    "approximate_entropy",
    "cusum",
    "random_excursions",
    "random_excursions_variant",
]


def monobit(sequence):
    """Proportion of values is compared to expected 1:1 ratio

    The difference between the frequency of the two values is found, and
    referenced to a hypothetically truly random RNG.

    Parameters
    ----------
    sequence : array-like
        Output of the RNG being tested

    Returns
    -------
    result: ``MonobitTestResult``
        Dataclass that contains the test's statistic and p-value as well as
        other relevant information gathered.
    """
    return _randtests.monobit(sequence)


def frequency_within_block(sequence, blocksize=None):
    """Proportion of values per block is compared to expected 1:1 ratio

    The difference between the frequency of the two values in each block is
    found, and referenced to a hypothetically truly random RNG.

    Parameters
    ----------
    sequence : array-like
        Output of the RNG being tested
    blocksize : ``int``
        Size of the blocks that partition the given series

    Returns
    -------
    result: ``FrequencyWithinBlockTestResult``
        Dataclass that contains the test's statistic and p-value as well as
        other relevant information gathered.
    """
    return _randtests.frequency_within_block(sequence, blocksize=blocksize)


def runs(sequence):
    """Actual number of runs is compared to expected result

    The number of runs (uninterrupted sequence of the same value) is found, and
    referenced to a hypothetically truly random RNG.

    Parameters
    ----------
    sequence : array-like
        Output of the RNG being tested

    Returns
    -------
    result: ``RunsTestResult``
        Dataclass that contains the test's statistic and p-value
    """
    return _randtests.runs(sequence)


def longest_runs(sequence):
    """Longest runs per block is compared to expected result

    The longest number of runs (uninterrupted sequence of the same value) per
    block is found, and referenced to a hypothetically truly random RNG.

    Parameters
    ----------
    sequence : array-like
        Output of the RNG being tested

    Returns
    -------
    result: ``LongestRunsTestResult``
        Dataclass that contains the test's statistic and p-value
    """
    return _randtests.longest_runs(sequence)


def binary_matrix_rank(sequence, matrix_dimen: Tuple[int, int] = None):
    """Independence of neighbouring sequences is compared to expected result

    Independence is determined by the matrix rank of a subsequence, where it is
    split into multiple rows to form a matrix. The counts of different rank bins
    is referenced to a hypothetically truly random RNG.

    Parameters
    ----------
    sequence : array-like
        Output of the RNG being tested
    candidate : Value present in given sequence
        The value which is counted in each block
    matrix_dimen : ``Tuple[int, int]``
        Number of rows and columns in each matrix

    Returns
    -------
    result: ``BinaryMatrixRankTestResult``
        Dataclass that contains the test's statistic and p-value
    """
    return _randtests.binary_matrix_rank(sequence, matrix_dimen=matrix_dimen)


def spectral(sequence):
    """Potency of periodic features in sequence is compared to expected result

    The binary values are treated as the peaks and troughs respectively of a
    signal, which is applied a Fourier transform so as to find constituent
    periodic features. The strength of these features is referenced to the
    expected potent periodic features present in a hypothetically truly random
    RNG.

    Parameters
    ----------
    sequence : array-like
        Output of the RNG being tested

    Returns
    -------
    result: ``SpectralTestResult``
        Dataclass that contains the test's statistic and p-value

    Raises
    ------
    NonBinaryTruncatedSequenceError
        When odd-lengthed sequence is truncated there is only one distinct value
        present

    """
    return _randtests.spectral(sequence)


def non_overlapping_template_matching(sequence, template_size=None, blocksize=None):
    """Matches of template per block is compared to expected result

    The sequence is split into blocks, where the number of non-overlapping
    matches to the template in each block is found. This is referenced to the
    expected mean and variance in matches of a hypothetically truly random RNG.

    Parameters
    ----------
    sequence : array-like
        Output of the RNG being tested
    template_size : ``int``
        Size of all the templates to be generated
    blocksize : ``int``
        Size of the blocks that partition the given series

    Returns
    -------
    results: ``MultiNonOverlappingTemplateMatchingTestResult``
        Dictionary that contains the multiple test results
    """
    return _randtests.non_overlapping_template_matching(
        sequence, template_size=template_size, blocksize=blocksize
    )


def overlapping_template_matching(sequence, template_size=None, blocksize=None, df=5):
    """Overlapping matches of template per block is compared to expected result

    The sequence is split into ``nblocks`` blocks, where the number of
    overlapping matches to the template in each block is found. This is
    referenced to the expected mean and variance in matches of a hypothetically
    truly random RNG.

    Parameters
    ----------
    sequence : array-like
        Output of the RNG being tested
    template_size : ``int``
        Size of the template to be generated
    blocksize : ``int``
        Size of the blocks that partition the given series

    Returns
    -------
    result: ``OverlappingTemplateMatchingTestResult``
        Dataclass that contains the test's statistic and p-value.
    """
    return _randtests.overlapping_template_matching(
        sequence, template_size=template_size, blocksize=blocksize, df=df
    )


def maurers_universal(sequence, blocksize=None, init_nblocks=None):
    """Distance between patterns is compared to expected result

    Unique permutations in an initial sequence are identified, and the
    distances of aforementioned permutations in a remaining sequence are
    accumulated. The normalised value for the accumulated distances is then
    compared to a hypothetically truly random RNG.


    Parameters
    ----------
    sequence : array-like
        Output of the RNG being tested
    blocksize : ``int``
        Size of the blocks that form a permutation
    init_nblocks : ``int``
        Number of initial blocks to identify permutations

    Returns
    -------
    result: ``UniversalTestResult``
        Dataclass that contains the test's statistic and p-value
    """
    return _randtests.maurers_universal(
        sequence, blocksize=blocksize, init_nblocks=init_nblocks
    )


def serial(sequence, blocksize=None):
    return _randtests.serial(sequence, blocksize=None)


def linear_complexity(sequence, blocksize=None):
    return _randtests.linear_complexity(sequence, blocksize=blocksize)


def approximate_entropy(sequence, blocksize=None):
    return _randtests.approximate_entropy(sequence, blocksize=blocksize)


def cusum(sequence, reverse=False):
    return _randtests.cusum(sequence, reverse=reverse)


def random_excursions(sequence):
    return _randtests.random_excursions(sequence)


def random_excursions_variant(sequence):
    return _randtests.random_excursions_variant(sequence)
