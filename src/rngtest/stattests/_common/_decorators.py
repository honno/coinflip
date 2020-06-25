from functools import wraps
from warnings import warn

import pandas as pd

__all__ = ["stattest", "infer_candidate", "elected"]


class NonBinarySequenceError(ValueError):
    pass


def stattest(min_input=2):
    def decorator(func):
        @wraps(func)
        def wrapper(sequence, *args, **kwargs):
            if not isinstance(sequence, pd.Series):
                series = pd.Series(sequence)
            else:
                series = sequence

            if series.nunique() != 2:
                raise NonBinarySequenceError()

            if len(series) < min_input:
                warn(f"Sequence below recommended input of {min_input}", UserWarning)

            result = func(series, *args, **kwargs)

            return result

        return wrapper

    return decorator


def infer_candidate(values):
    try:
        candidate = max(values)
    except TypeError:
        candidate = values[0]

    return candidate


def elected(func):
    @wraps(func)
    def wrapper(series: pd.Series, *args, candidate=None, **kwargs):
        if candidate is None:
            values = series.unique()
            candidate = infer_candidate(values)
        else:
            if candidate not in series.unique():
                raise ValueError()

        result = func(series, *args, candidate=candidate, **kwargs)

        return result

    return wrapper
