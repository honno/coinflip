from math import ceil
from numbers import Real
from random import getrandbits
from typing import List

from hypothesis import strategies as st
from hypothesis.strategies import SearchStrategy
from typing_extensions import Literal

__all__ = ["mixedbits", "real"]


@st.composite
def mixedbits(draw, min_size=2) -> SearchStrategy[List[Literal[0, 1]]]:
    """Strategy to generate binary sequences"""
    n = draw(st.integers(min_value=min_size, max_value=1000))

    mixedbits = [getrandbits(1) for _ in range(n)]  # TODO make this reproducible
    mixedbits[0:2] = [0, 1]  # force bits being mixed TODO use a filter

    return mixedbits


def real(min_value: Real = None, allow_infinity: bool = True) -> SearchStrategy[Real]:
    return st.one_of(
        st.integers(min_value=ceil(min_value) if min_value else None),
        st.floats(
            min_value=float(min_value) if min_value else None,
            allow_infinity=allow_infinity,
            allow_nan=False,
        ),
    )
