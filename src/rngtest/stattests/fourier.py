from math import erfc
from math import log
from math import sqrt

import pandas as pd
from numpy.fft import fft as _fft

from rngtest.stattests.common import TestResult
from rngtest.stattests.common import binary_stattest
from rngtest.stattests.common import elected

__all__ = ["discrete_fourier_transform"]


class TruncatedInputSingleValueError(ValueError):
    pass


@elected
@binary_stattest
def discrete_fourier_transform(series, candidate):
    n = len(series)

    if n % 2 != 0:
        series = series[:-1]
        if series.nunique() != 2:
            raise TruncatedInputSingleValueError()

    peaks = candidate
    trough = next(value for value in series.unique() if value != candidate)

    oscillations = series.map({peaks: 1, trough: -1})
    fourier = fft(oscillations)

    halffourier = fourier[: n // 2]
    peaks = halffourier.abs()

    threshold = sqrt(log(1 / 0.05) * n)
    expectedbelow = 0.95 * n / 2
    actualbelow = sum(peaks < threshold)  # TODO not accurate

    diff = actualbelow - expectedbelow
    normdiff = diff / sqrt((n * 0.95 * 0.05) / 4)

    p = erfc(abs(normdiff) / sqrt(2))

    return TestResult(statistic=normdiff, p=p)


def fft(array) -> pd.Series:
    fourier_ndarray = _fft(array)
    fourier_series = pd.Series(fourier_ndarray)

    return fourier_series
