from functools import wraps

import pandas as pd

from coinflip.randtests._exceptions import NonBinarySequenceError
from coinflip.randtests._exceptions import TestInputError
from coinflip.randtests._result import TestResult

__all__ = ["randtest", "infer_candidate", "elected"]


class MinimumInputError(TestInputError):
    """Error if sequence length is below minimum allowed"""

    def __init__(self, n, min_input):
        self.n = n
        self.min_input = min_input

    def __str__(self):
        return f"Sequence length {self.n} is below required minimum of {self.min_input}"


def randtest(min_input=2):
    """Decorator factory for parsing sequences in randomness tests

    Returns a decorator (a method which returns a wrapper method). The wrapper
    checks if passed ``sequence`` is a pandas ``Series``, attempting to convert it
    if not.

    The length of the ``sequence`` is then checked to see if it meets the
    passed minimum input requirement, raising an error if not.

    Parameters
    ----------
    min_input : ``int``, default ``2``
        Absolute minimum length of sequence the test can handle

    Returns
    -------
    decorator : ``Callable[[Callable], Callable]``
        Decorator method for parsing sequences in randomness tests

    Raises
    ------
    MinimumInputError
        If ``sequence`` length exceeds ``min_input``

    See Also
    --------
    pandas.Series: Initialises with ``sequence`` if not already a ``Series``
    """

    def decorator(func):
        @wraps(func)
        def wrapper(sequence, *args, **kwargs) -> TestResult:
            if isinstance(sequence, pd.Series):
                series = sequence
            else:
                series = pd.Series(sequence)

            if series.nunique() != 2:
                raise NonBinarySequenceError()

            n = len(series)
            if n < min_input:
                raise MinimumInputError(n, min_input)

            result = func(series, *args, **kwargs)

            return result

        return wrapper

    return decorator


def infer_candidate(unique_values):
    """Infers the candidate from a list of unique values

    An equality check between the values is attempted, where the "largest"
    value is chosen. If the values can not be compared, then the first element
    of ``unique_values`` is chosen.

    Parameters
    ----------
    unique_values : List
        List of a unique values

    Returns
    -------
    candidate
        Inferred candidate of ``unique_values``

    See Also
    --------
    max : Built-in method used to pick the "largest" value
    """
    try:
        candidate = max(unique_values)
    except TypeError:
        candidate = unique_values[0]

    return candidate


# TODO take candidate and unique value args
class CandidateNotInSequenceError(TestInputError):
    """Error for when candidate value is not present in sequence"""

    def __str__(self):
        return "Candidate value not present in sequence"


def elected(func):
    """Decorator for parsing candidate arguments in randomness tests

    If no ``candidate`` value is passed, a candidate is inferred from the
    unique values of the passed ``series``.

    If a ``candidate`` value is passed, it is checked to see the value is present
    in the passed ``series``.

    Parameters
    ----------
    func : ``Callable``
        Randomness test with candidate kwarg to parse

    Returns
    -------
    wrapper : ``Callable``
        Decorated ``func``

    Raises
    ------
    CandidateNotInSequenceError
        If passed ``candidate`` value is not present in ``series``

    See Also
    --------
    infer_candidate: Method that infers the value of ``candidate``
    """

    @wraps(func)
    def wrapper(series, *args, candidate=None, **kwargs) -> TestResult:
        values = series.unique()
        if candidate is None:
            candidate = infer_candidate(values)
        else:
            if candidate not in values:
                raise CandidateNotInSequenceError()

        result = func(series, *args, candidate=candidate, **kwargs)

        return result

    return wrapper
