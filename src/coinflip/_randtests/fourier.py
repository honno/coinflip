from dataclasses import dataclass
from math import erfc
from math import log
from math import sqrt

import pandas as pd
from numpy.fft import fft

from coinflip._randtests.common.exceptions import NonBinarySequenceError
from coinflip._randtests.common.result import TestResult
from coinflip._randtests.common.result import make_testvars_list
from coinflip._randtests.common.testutils import check_recommendations
from coinflip._randtests.common.testutils import randtest

__all__ = ["spectral"]


class NonBinaryTruncatedSequenceError(NonBinarySequenceError):
    """Error if truncated sequence does not contain only 2 distinct values"""

    def __str__(self):
        return (
            "When truncated into an even-length, sequence contains only 1 distinct value\n"
            "i.e. the sequence was originally binary, but now isn't"
        )


@randtest()
def spectral(series, heads, tails):
    n = len(series)

    check_recommendations({"n ≥ 1000": n >= 1000})

    if n % 2 != 0:
        series = series[:-1]
        if series.nunique() != 2:
            raise NonBinaryTruncatedSequenceError()

    threshold = sqrt(log(1 / 0.05) * n)
    nbelow_expected = 0.95 * n / 2

    oscillations = series.map({heads: 1, tails: -1})
    fourier = pd.Series(fft(oscillations))  # fft returns a ndarray

    half_fourier = fourier[: n // 2]
    peaks = half_fourier.abs()

    nbelow = sum(peaks < threshold)

    diff = nbelow - nbelow_expected
    normdiff = diff / sqrt((n * 0.95 * 0.05) / 4)

    p = erfc(abs(normdiff) / sqrt(2))

    return SpectralTestResult(heads, tails, normdiff, p, nbelow_expected, nbelow, diff,)


@dataclass
class SpectralTestResult(TestResult):
    nbelow_expected: float
    nbelow: int
    diff: float

    def __post_init__(self):
        pass

    def _render(self):
        yield self._pretty_result("normalised diff")

        yield make_testvars_list(
            "npeaks above threshold",
            ("actual", self.nbelow),
            ("expected", self.nbelow_expected),
            ("diff", self.diff),
        )
