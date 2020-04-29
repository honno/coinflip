from dataclasses import dataclass
from typing import Any

from click import echo


@dataclass
class ValueRepeats:
    value: Any
    repeats: int = 1


def runs(series):
    coded_series = []

    first_value = series.iloc[0]
    coded_series.append(ValueRepeats(first_value, repeats=0))

    for _, value in series.iteritems():
        tail = coded_series[-1]

        if value == tail.value:
            tail.repeats += 1
        else:
            coded_series.append(ValueRepeats(value))

    echo(coded_series[:5])

    # TODO summary statsticss
