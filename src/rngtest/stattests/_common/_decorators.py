from functools import wraps

import pandas as pd

__all__ = ["stattest", "elected"]


def stattest(func):
    @wraps(func)
    def wrapper(sequence, *args, **kwargs):
        if not isinstance(sequence, pd.Series):
            series = pd.Series(sequence)
        else:
            series = sequence

        if series.nunique() != 2:
            raise ValueError()

        result = func(series, *args, **kwargs)

        return result

    return wrapper


def elected(func):
    @wraps(func)
    def wrapper(series: pd.Series, *args, candidate=None, **kwargs):
        if candidate is None:
            if 1 in series.unique():
                candidate = 1
            else:
                candidate = series.unique()[0]
        else:
            if candidate not in series.unique():
                raise ValueError()

        result = func(series, *args, candidate=candidate, **kwargs)

        return result

    return wrapper
