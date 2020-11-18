from typing import List
from typing import NamedTuple

from pytest import mark
from typing_extensions import Literal

from coinflip.algorithms import berlekamp_massey

__all__ = ["bm_examples"]


class BMExample(NamedTuple):
    sequence: List[Literal[0, 1]]
    min_size: int


bm_examples = [
    BMExample(
        # SP800-22 example
        # 1-4  | 1 1 0 1  | 0
        # 2-5  | 1 0 1 0  | 1
        # 3-6  | 0 1 0 1  | 1
        # 4-7  | 1 0 1 1  | 1
        # 5-8  | 0 1 1 1  | 1
        # 6-9  | 1 1 1 1  | 0
        # 7-10 | 1 1 1 0  | 0
        # 8-11 | 1 1 0 0  | 0
        # 9-12 | 1 0 0 0  | 1
        sequence=[1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 1],
        min_size=4,
    ),
    BMExample(
        # https://bell0bytes.eu/linear-feedback-shift-registers/
        sequence=[
            1,
            0,
            0,
            1,
            1,
            1,
            0,
            1,
            1,
            0,
            0,
            1,
            1,
            1,
            0,
            1,
            0,
            1,
            0,
            0,
            1,
            0,
            0,
            1,
            1,
        ],
        min_size=13,
    ),
]


@mark.parametrize(BMExample._fields, bm_examples)
def test_berlekamp_massey(sequence, min_size):
    assert berlekamp_massey(sequence) == min_size
