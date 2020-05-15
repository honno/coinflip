from base64 import b64encode
from dataclasses import dataclass
from functools import wraps
from io import BytesIO
from math import ceil
from typing import Iterable
from typing import Union

import pandas as pd
from matplotlib.axes import Subplot

__all__ = ["TestResult", "stattest", "binary_stattest", "chunks"]


@dataclass
class TestResult:
    statistic: Union[int, float]
    p: float

    def p3f(self):
        return round(self.p, 3)

    def __str__(self):
        raise NotImplementedError()

    def _report(self) -> Iterable[Union[str, Subplot]]:
        raise NotImplementedError()

    @classmethod
    def _markup(cls, item):
        if isinstance(item, str):
            return f"<p>{item}</p>"
        elif isinstance(item, Subplot):
            image_bin = BytesIO()
            item.figure.savefig(image_bin, format="png")

            image_bin.seek(0)
            image_base64_bstr = b64encode(image_bin.read())
            image_base64_str = image_base64_bstr.decode("utf-8")

            return f"<img src='data:image/png;base64,{image_base64_str}' />"

    def report(self):
        elements = (TestResult._markup(item) for item in self._report())
        report = "\n".join(elements)

        return report


def stattest(func):
    @wraps(func)
    def wrapper(series: pd.Series, *args, **kwargs):
        if series.nunique() == 1:
            raise ValueError()

        result = func(series, *args, **kwargs)

        return result

    return wrapper


def binary_stattest(func):
    @wraps(func)
    def wrapper(series: pd.Series, *args, **kwargs):
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


def chunks(series: pd.Series, block_size=None, nblocks=None):
    if block_size and nblocks:
        raise ValueError()
    elif not block_size and not nblocks:
        raise ValueError()

    if block_size is None:
        block_size = ceil(len(series) / nblocks)

    elements_remaining = len(series) % block_size
    boundary = len(series) - elements_remaining

    for i in range(0, boundary, block_size):
        yield series[i : i + block_size]
