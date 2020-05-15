from math import erfc
from math import log
from math import sqrt

import pandas as pd
from numpy.fft import fft

from rngtest.stattests.common import TestResult
from rngtest.stattests.common import binary_stattest
from rngtest.stattests.common import elected

__all__ = ["discrete_fourier_transform"]


@elected
@binary_stattest
def discrete_fourier_transform(series, candidate=None):
    n = len(series)

    peaks = candidate
    trough = next(value for value in series.unique() if value != candidate)

    oscillations = series.map({peaks: 1, trough: -1})
    fourier_as_ndarray = fft(oscillations)
    fourier = pd.Series(fourier_as_ndarray)

    fourier_first_half = fourier[: n // 2]
    peaks = fourier_first_half.abs()

    threshold = sqrt(log(1 / 0.05) * n)
    expected_below_threshold = 0.95 * n / 2
    actual_below_threshold = sum(peaks < threshold)  # TODO not accurate

    difference = actual_below_threshold - expected_below_threshold
    normalised_diff = difference / sqrt((n * 0.95 * 0.05) / 4)

    p = erfc(abs(normalised_diff) / sqrt(2))

    return TestResult(statistic=normalised_diff, p=p)
