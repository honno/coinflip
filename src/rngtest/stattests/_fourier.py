from math import erfc
from math import log
from math import sqrt

import pandas as pd
from numpy.fft import fft as _fft

from rngtest.stattests._common import TestResult
from rngtest.stattests._common import elected
from rngtest.stattests._common import stattest

__all__ = ["discrete_fourier_transform"]


class TruncatedInputSingleValueError(ValueError):
    pass


@stattest
@elected
def discrete_fourier_transform(series, candidate):
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
    candidate : Value present in given series
        The value which is considered the peak in oscillations

    Returns
    -------
    TestResult
        Dataclass that contains the test's statistic and p-value

    Raises
    ------
    TruncatedInputSingleValueError
        When odd-lengthed sequence is truncated there is only one unique value
        present

    """
    n = len(series)

    if n % 2 != 0:
        series = series[:-1]
        if series.nunique() != 2:
            raise TruncatedInputSingleValueError()

    peaks = candidate
    trough = next(value for value in series.unique() if value != candidate)

    oscillations = series.map({peaks: 1, trough: -1})
    fourier = fft(oscillations)

    half_fourier = fourier[: n // 2]
    peaks = half_fourier.abs()

    threshold = sqrt(log(1 / 0.05) * n)
    nbelow_expected = 0.95 * n / 2
    nbelow_actual = sum(peaks < threshold)

    diff = nbelow_actual - nbelow_expected
    normdiff = diff / sqrt((n * 0.95 * 0.05) / 4)

    p = erfc(abs(normdiff) / sqrt(2))

    return TestResult(statistic=normdiff, p=p)


def fft(array) -> pd.Series:
    fourier_ndarray = _fft(array)
    fourier_series = pd.Series(fourier_ndarray)

    return fourier_series
