from rngtest.stattests._fourier import discrete_fourier_transform
from rngtest.stattests._frequency import frequency_within_block
from rngtest.stattests._frequency import monobits
from rngtest.stattests._matrix import binary_matrix_rank
from rngtest.stattests._runs import longest_runs
from rngtest.stattests._runs import runs
from rngtest.stattests._template import non_overlapping_template_matching
from rngtest.stattests._template import overlapping_template_matching
from rngtest.stattests._universal import maurers_universal

__all__ = [
    "monobits",
    "frequency_within_block",
    "runs",
    "longest_runs",
    "binary_matrix_rank",
    "discrete_fourier_transform",
    "non_overlapping_template_matching",
    "overlapping_template_matching",
    "maurers_universal",
]
