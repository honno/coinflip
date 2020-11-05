from dataclasses import dataclass
from functools import lru_cache
from functools import wraps
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Tuple
from warnings import warn

import pandas as pd
from rich.progress import Progress

from coinflip._randtests.common.exceptions import NonBinarySequenceError
from coinflip._randtests.common.exceptions import TestInputError
from coinflip._randtests.common.typing import Face

__all__ = [
    "randtest",
    "set_task_total",
    "advance_task",
    "check_recommendations",
]


@dataclass
class MinimumInputError(TestInputError):
    n: int
    min_n: int

    def __str__(self):
        return f"Sequence length {self.n} is below required minimum of {self.min_n}"


class CliContext(NamedTuple):
    progress: Progress
    task: int


def randtest(min_n=2):
    """Decorator factory for parsing sequences in randomness tests

    Returns a decorator (a method which returns a wrapper method). The wrapper
    checks if passed ``sequence`` is a pandas ``Series``, attempting to convert
    it if not.

    The length of the ``sequence`` is then checked to see if it meets the
    passed minimum input requirement, raising an error if not.

    The `heads` and `tails` of the ``sequence`` is inferred from its unique
    values.

    Parameters
    ----------
    min_n : ``int``, default ``2``
        Minimum length of sequence the test can handle

    Returns
    -------
    decorator : ``Callable[[Callable], Callable]``
        Decorator method for parsing sequences in randomness tests

    Raises
    ------
    MinimumInputError
        If ``sequence`` length exceeds ``min_n``

    See Also
    --------
    pandas.Series: Initialises with ``sequence`` if not already a ``Series``

    Notes
    -----
    `heads` and `tails` corresponds to the ``1`` and ``0`` values of a binary
    input sequence. SP800-22 only specifies randomness tests for these binary
    sequences, but in actuality all of its tests can be generalised for any
    sequence of a GF(2) field (i.e. contains two distinct values), so the
    `heads` and `tails` abstraction allows for mapping these GF(2) sequences to
    their binary counterparts.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(sequence, ctx: Progress = None, **kwargs):
            if isinstance(sequence, pd.Series):
                series = sequence
            else:
                series = pd.Series(sequence)

            if series.nunique() != 2:
                raise NonBinarySequenceError()

            n = len(series)
            if n < min_n:
                raise MinimumInputError(n, min_n)

            values = series.unique()
            heads, tails = infer_faces(tuple(values))

            result = func(series, heads, tails, ctx, **kwargs)

            return result

        return wrapper

    return decorator


@lru_cache()
def infer_faces(unique_values: Tuple[Face, Face]) -> Tuple[Face, Face]:
    """Infers the `heads` and `tails` faces from a list of unique values

    An equality check between the values is attempted where the "largest"
    value is chosen as the `heads`, and subsequently the other value is
    chosen as the `tails`.

    Parameters
    ----------
    unique_values : ``Tuple[Any, Any]``
        Tuple of two unique values

    Returns
    -------
    heads
        Inferred heads face of ``unique_values``
    tails
        Inferred tails face of ``unique_values``
    """
    heads = max(unique_values)
    tails = next(value for value in unique_values if value != heads)

    return heads, tails


def progress_context(func):
    @wraps(func)
    def wrapper(ctx: Optional[CliContext], *args):
        if ctx:
            progress, task = ctx
            func(progress, task, *args)

    return wrapper


@progress_context
def set_task_total(progress, task, total: int):
    progress.update(task, total=total)


@progress_context
def advance_task(progress, task):
    progress.update(task, advance=1)


def check_recommendations(ctx: Optional[CliContext], recommendations: Dict[str, bool]):
    """Warns on recommendation failures

    Parameters
    ----------
    recommendations : ``Dict[str, bool]``
        Map of recommendation string representations to the actual
        recommendation outcomes

    Warns
    -----
    UserWarning
        When one or more recommendations fail
    """
    failures = [expr for expr, success in recommendations.items() if not success]

    if failures and not ctx:
        warn(make_failures_msg(failures), UserWarning)

    return failures


def make_failures_msg(failures: List[str]) -> str:
    nfail = len(failures)

    if nfail == 1:
        expr = failures[0]
        return f"NIST recommendation not met: {expr}"

    elif nfail > 1:
        msg = "Multiple NIST recommendations not met:\n"
        msg += "\n".join([f"  • {expr}" for expr in failures])

        return msg
