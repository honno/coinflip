from random import getrandbits
from typing import List

from hypothesis import strategies as st
from hypothesis.strategies import SearchStrategy

__all__ = ["mixedbits"]


@st.composite
def mixedbits(draw, min_size=2) -> SearchStrategy[List[int]]:
    """Strategy to generate binary sequences"""
    n = draw(st.integers(min_value=min_size, max_value=1000000))

    mixedbits = [getrandbits(1) for _ in range(n)]  # TODO make this reproducible
    mixedbits[0:2] = [0, 1]  # force bits being mixed TODO use a filter

    return mixedbits
