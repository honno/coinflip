"""Statistical tests for randomness

This sub-package comprises of implementations of statistical tests laid out in a
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
explanations. Part of the purpose for ``coinflip`` is to "describe" the NIST tests
more wholly than in the paper itself, whilst also reducing the noise of some
non-idiomatic programming conventions used in ``sts``.

.. [1] National Institute of Standards and Technology <Andrew Rukhin, Juan Soto,
   James Nechvatal, Miles Smid, Elaine Barker, Stefan Leigh, Mark Levenson, Mark
   Vangel, David Banks, Alan Heckert, James Dray, San Vo,
   Lawrence E Bassham II>, "A Statistical Test Suite for Random and Pseudorandom
   Number Generators for Cryptographic Applications", *Special Publication
   800-22 Revision 1a*, April 2010.
"""
from typing import Optional
from typing import Tuple

from coinflip import _randtests
from coinflip._randtests.common import exceptions

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
    "exceptions",
]


def monobit(sequence):
    """Proportion of values is compared to expected 1:1 ratio

    The difference between the occurrences of the two values in the sequence is
    found, and referenced to a hypothetically truly random sequence.

    Parameters
    ----------
    sequence : array-like with two distinct values
        Sequence containing 2 distinct elements

    Returns
    -------
    result : ``MonobitTestResult``
        Dataclass that contains the test's statistic and p-value as well as
        other relevant information gathered.
    """
    return _randtests.monobit(sequence)


def frequency_within_block(sequence, blocksize: Optional[int] = None):
    """Proportion of values per block is compared to expected 1:1 ratio

    The sequence is split into blocks, and the difference between the occurrences
    of the two values in the sequence is found. This is referenced to a
    hypothetically truly random sequence.

    Parameters
    ----------
    sequence : array-like with two distinct values
        Sequence containing 2 distinct elements
    blocksize : ``int``
        Size of the blocks that partition the given sequence

    Returns
    -------
    result : ``FrequencyWithinBlockTestResult``
        Dataclass that contains the test's statistic and p-value as well as
        other relevant information gathered.
    """
    return _randtests.frequency_within_block(sequence, blocksize=blocksize)


def runs(sequence):
    """Number of runs is compared to expected result

    The number of runs (uninterrupted sequence of the same value) is found, and
    referenced to a hypothetically truly random sequence.

    Parameters
    ----------
    sequence : array-like with two distinct values
        Sequence containing 2 distinct elements

    Returns
    -------
    result : ``RunsTestResult``
        Dataclass that contains the test's statistic and p-value as well as
        other relevant information gathered.
    """
    return _randtests.runs(sequence)


def longest_runs(sequence):
    """Longest runs per block is compared to expected result

    The sequence is split into blocks, where the longest number of runs
    (uninterrupted sequence of the same value) in each block is found. This is
    referenced to a hypothetically truly random sequence.

    Parameters
    ----------
    sequence : array-like with two distinct values
        Sequence containing 2 distinct elements

    Returns
    -------
    result : ``LongestRunsTestResult``
        Dataclass that contains the test's statistic and p-value as well as
        other relevant information gathered.
    """
    return _randtests.longest_runs(sequence)


def binary_matrix_rank(sequence, matrix_dimen: Optional[Tuple[int, int]] = None):
    """Independence of neighbouring sequences is compared to expected result

    The sequence is split into matrices, where the rank of each matrix is found
    to determine independence. The counts of different rank bins is referenced
    to a hypothetically truly random sequence.

    Parameters
    ----------
    sequence : array-like with two distinct values
        Sequence containing 2 distinct elements
    matrix_dimen : ``Tuple[int, int]``
        Number of rows and columns in each matrix

    Returns
    -------
    result : ``BinaryMatrixRankTestResult``
        Dataclass that contains the test's statistic and p-value as well as
        other relevant information gathered.
    """
    return _randtests.binary_matrix_rank(sequence, matrix_dimen=matrix_dimen)


def spectral(sequence):
    """Potency of periodic features in sequence is compared to expected result

    The sequence is treated as a signal, which is applied a Fourier transform so
    as to find constituent periodic features. The strength of these features is
    referenced to the expected periodic features present in a hypothetically
    truly random sequence.

    Parameters
    ----------
    sequence : array-like with two distinct values
        Sequence containing 2 distinct elements

    Returns
    -------
    result : ``SpectralTestResult``
        Dataclass that contains the test's statistic and p-value as well as
        other relevant information gathered.

    Raises
    ------
    NonBinaryTruncatedSequenceError
        When odd-lengthed sequence is truncated there is only one distinct value
        present

    """
    return _randtests.spectral(sequence)


def non_overlapping_template_matching(
    sequence, template_size: Optional[int] = None, blocksize: Optional[int] = None
):
    """Matches to template per block is compared to expected result

    The sequence is split into blocks, where the number of non-overlapping
    pattern matches to the template in each block is found. This is referenced
    to the expected mean and variance in matches of a hypothetically truly
    random sequence.

    Parameters
    ----------
    sequence : array-like with two distinct values
        Sequence containing 2 distinct elements
    template_size : ``int``
        Size of all the templates to be generated
    blocksize : ``int``
        Size of the blocks that partition the given sequence

    Returns
    -------
    results : ``NonOverlappingTemplateMatchingMultiTestResult``
        Dataclass that contains the statistics and p-values of all sub-tests, as
        well as other relevant information gathered.
    """
    return _randtests.non_overlapping_template_matching(
        sequence,
        template_size=template_size,
        blocksize=blocksize,
    )


def overlapping_template_matching(
    sequence, template_size: Optional[int] = None, blocksize: Optional[int] = None
):
    """Overlapping matches to template per block is compared to expected result

    The sequence is split into blocks, where the number of overlapping patterns
    matches to the template in each block is found. This is referenced to the
    expected mean and variance in matches of a hypothetically truly random sequence.

    Parameters
    ----------
    sequence : array-like with two distinct values
        Sequence containing 2 distinct elements
    template_size : ``int``
        Size of the template to be generated
    blocksize : ``int``
        Size of the blocks that partition the given sequence

    Returns
    -------
    result : ``OverlappingTemplateMatchingTestResult``
        Dataclass that contains the test's statistic and p-value as well as
        other relevant information gathered.
    """
    return _randtests.overlapping_template_matching(
        sequence,
        template_size=template_size,
        blocksize=blocksize,
    )


def maurers_universal(
    sequence, blocksize: Optional[int] = None, init_nblocks: Optional[int] = None
):
    """Distance between patterns is compared to expected result

    The distinct patterns in an initial sequence are identified, and the
    distances between subsequent occurences of these patterns in a remaining
    sequence are accumulated. The normalised value for the accumulated distances
    is referenced to a hypothetically truly random sequence.

    Parameters
    ----------
    sequence : array-like with two distinct values
        Sequence containing 2 distinct elements
    blocksize : ``int``
        Size of the patterns
    init_nblocks : ``int``
        Number of initial blocks to identify patterns

    Returns
    -------
    result : ``UniversalTestResult``
        Dataclass that contains the test's statistic and p-value as well as
        other relevant information gathered.
    """
    return _randtests.maurers_universal(
        sequence,
        blocksize=blocksize,
        init_nblocks=init_nblocks,
    )


def linear_complexity(sequence, blocksize: Optional[int] = None):
    """LSFRs of blocks is compared to expected length

    The seqience is split into blocks, where the shortest linear feedback shift
    register is found for each block. The difference of each LSFR's length to the
    expected mean length is binned, and is referenced to a hypothetically truly
    random sequence.

    Parameters
    ----------
    sequence : array-like with two distinct values
        Sequence containing 2 distinct elements
    blocksize : ``int``
        Size of the blocks

    Returns
    -------
    results : ``LinearComplexityTestResult``
        Dataclass that contains the test's statistic and p-value as well as
        other relevant information gathered.
    """
    return _randtests.linear_complexity(sequence, blocksize=blocksize)


def serial(sequence, blocksize: Optional[int] = None):
    """Proportion of all overlapping patterns is compared to expected uniformity

    The number of overlapping pattern matches for each distinct pattern is
    found. This is referenced to a hypothetically truly random sequence.

    Parameters
    ----------
    sequence : array-like with two distinct values
        Sequence containing 2 distinct elements
    blocksize : ``int``
        Size of the patterns

    Returns
    -------
    results : ``SerialMultiTestResult``
        Dataclass that contains the statistics and p-values of all sub-tests, as
        well as other relevant information gathered.
    """
    return _randtests.serial(sequence, blocksize=blocksize)


def approximate_entropy(sequence, blocksize: Optional[int] = None):
    """Approximate entropy of sequence is compared to expected result

    The approximate entropy of the sequence is found and referenced to a truly
    random sequence.

    Parameters
    ----------
    sequence : array-like with two distinct values
        Sequence containing 2 distinct elements
    blocksize : ``int``
        Size of the patterns

    Returns
    -------
    results : ``ApproximateEntropyTestResult``
        Dataclass that contains the test's statistic and p-value as well as
        other relevant information gathered.
    """
    return _randtests.approximate_entropy(sequence, blocksize=blocksize)


def cusum(sequence, reverse: bool = False):
    """Furthest detour in a randomn walk is compared to expected result

    The sequence is treated as a random walk, where the furthest detour from the
    axis is identified and referenced to a hypothetically truly random sequence.

    Parameters
    ----------
    sequence : array-like with two distinct values
        Sequence containing 2 distinct elements
    reverse : ``bool``
        Cumulate sums from the end of the sequence first.

    Returns
    -------
    results : ``CusumTestResult``
        Dataclass that contains the test's statistic and p-value as well as
        other relevant information gathered.
    """
    return _randtests.cusum(sequence, reverse=reverse)


def random_excursions(sequence):
    """Frequency of states per cycle in a random walk is compared to expected results

    The sequence is treated as a random walk, where the frequency of states -4
    to 4 in each cycle is found. This is referenced to a hypothetically truly
    random sequence.

    Parameters
    ----------
    sequence : array-like with two distinct values
        Sequence containing 2 distinct elements

    Returns
    -------
    results : ``RandomExcursionsMultiTestResult``
        Dataclass that contains the statistics and p-values of all sub-tests, as
        well as other relevant information gathered.
    """
    return _randtests.random_excursions(sequence)


def random_excursions_variant(sequence):
    """Proportion of states in a random walk is compared to expected results

    The sequence is treated as a random walk, where the occurrences of states -9
    to 9 is founded and referenced to a hypothetically truly random sequence.

    Parameters
    ----------
    sequence : array-like with two distinct values
        Sequence containing 2 distinct elements

    Returns
    -------
    results : ``RandomExcursionsVariantMultiTestResult``
        Dataclass that contains the statistics and p-values of all sub-tests, as
        well as other relevant information gathered.
    """
    return _randtests.random_excursions_variant(sequence)
